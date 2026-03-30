"""
Approval Workflow Manager - Human-in-the-Loop System
Part of Personal AI Employee Silver Tier

This module manages the approval workflow:
1. Watches /Pending_Approval for new approval requests
2. Notifies human when approval needed
3. Watches /Approved for approved actions
4. Executes approved actions
5. Watches /Rejected and handles rejections

Usage:
    python approval_manager.py
"""

import time
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ApprovalWorkflowManager:
    """
    Manages human-in-the-loop approval workflow.
    
    Folder Structure:
    - /Pending_Approval: Awaiting human review
    - /Approved: Approved by human, ready to execute
    - /Rejected: Rejected by human
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.rejected_folder = self.vault_path / 'Rejected'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.pending_folder, self.approved_folder, 
                       self.rejected_folder, self.done_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Action handlers (registered by type)
        self.action_handlers: Dict[str, Callable] = {}
        
        # Track processed files
        self.processed_files = set()
    
    def register_handler(self, action_type: str, handler: Callable):
        """Register a handler function for an action type"""
        self.action_handlers[action_type] = handler
        self.logger.info(f"Registered handler for: {action_type}")
    
    def parse_approval_file(self, filepath: Path) -> Dict:
        """Parse an approval request file"""
        content = filepath.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter = {}
        lines = content.split('\n')
        in_frontmatter = False
        
        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
            
            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        
        return {
            'path': filepath,
            'type': frontmatter.get('type', 'general'),
            'action': frontmatter.get('action', 'unknown'),
            'status': frontmatter.get('status', 'pending'),
            'created': frontmatter.get('created', ''),
            'amount': frontmatter.get('amount', ''),
            'recipient': frontmatter.get('recipient', ''),
            'content': content,
            'frontmatter': frontmatter,
        }
    
    def check_pending_approvals(self) -> List[Dict]:
        """Check for pending approval requests"""
        pending_items = []
        
        for filepath in self.pending_folder.glob('*.md'):
            if filepath.stem not in self.processed_files:
                try:
                    item = self.parse_approval_file(filepath)
                    pending_items.append(item)
                    self.logger.info(f"Found pending approval: {filepath.name}")
                except Exception as e:
                    self.logger.error(f"Error parsing {filepath.name}: {e}")
        
        return pending_items
    
    def notify_human(self, pending_items: List[Dict]):
        """Notify human about pending approvals"""
        if not pending_items:
            return
        
        print("\n" + "=" * 60)
        print("⏳ PENDING APPROVALS")
        print("=" * 60)
        
        for item in pending_items:
            print(f"\n📋 {item['path'].name}")
            print(f"   Type: {item['type']}")
            print(f"   Action: {item['action']}")
            
            if item.get('amount'):
                print(f"   Amount: ${item['amount']}")
            if item.get('recipient'):
                print(f"   Recipient: {item['recipient']}")
            
            print(f"   Created: {item['created']}")
            print("\n   To Approve: Move file to /Approved folder")
            print("   To Reject: Move file to /Rejected folder")
        
        print("\n" + "=" * 60)
        
        # Log notification
        self._log_notification(pending_items)
    
    def _log_notification(self, pending_items: List[Dict]):
        """Log approval notifications"""
        log_file = self.logs_folder / 'approval_notifications.md'
        
        timestamp = datetime.now().isoformat()
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## {timestamp}\n\n")
            f.write(f"Pending approvals: {len(pending_items)}\n")
            
            for item in pending_items:
                f.write(f"- {item['path'].name} ({item['type']})\n")
    
    def check_approved(self) -> List[Path]:
        """Check for approved files ready to execute"""
        approved_files = []
        
        for filepath in self.approved_folder.glob('*.md'):
            if filepath.stem not in self.processed_files:
                approved_files.append(filepath)
                self.logger.info(f"Found approved file: {filepath.name}")
        
        return approved_files
    
    def execute_approved_action(self, filepath: Path) -> bool:
        """Execute an approved action"""
        try:
            item = self.parse_approval_file(filepath)
            
            # Get handler for this action type
            handler = self.action_handlers.get(item['type'])
            
            if handler:
                self.logger.info(f"Executing {item['type']} action: {filepath.name}")
                success = handler(item)
                
                if success:
                    # Move to Done
                    dest = self.done_folder / filepath.name
                    shutil.move(str(filepath), str(dest))
                    self.logger.info(f"Action completed: {filepath.name}")
                    return True
                else:
                    self.logger.error(f"Handler failed for: {filepath.name}")
                    return False
            else:
                # No handler - just move to Done with note
                self.logger.warning(f"No handler for {item['type']}, marking as done")
                
                # Add completion note
                content = filepath.read_text(encoding='utf-8')
                content += f"\n\n---\n*Processed automatically at {datetime.now().isoformat()}*\n"
                filepath.write_text(content, encoding='utf-8')
                
                dest = self.done_folder / filepath.name
                shutil.move(str(filepath), str(dest))
                return True
                
        except Exception as e:
            self.logger.error(f"Error executing approved action: {e}")
            return False
    
    def check_rejected(self) -> List[Path]:
        """Check for rejected files"""
        rejected_files = []
        
        for filepath in self.rejected_folder.glob('*.md'):
            if filepath.stem not in self.processed_files:
                rejected_files.append(filepath)
        
        return rejected_files
    
    def process_rejected(self, filepath: Path):
        """Process a rejected file"""
        try:
            item = self.parse_approval_file(filepath)
            self.logger.info(f"Processing rejected: {filepath.name}")
            
            # Add rejection note
            content = filepath.read_text(encoding='utf-8')
            content += f"\n\n---\n*Rejected at {datetime.now().isoformat()}*\n"
            filepath.write_text(content, encoding='utf-8')
            
            # Move to Done/Rejected subfolder
            rejected_done = self.done_folder / 'Rejected'
            rejected_done.mkdir(parents=True, exist_ok=True)
            
            dest = rejected_done / filepath.name
            shutil.move(str(filepath), str(dest))
            
            # Log rejection
            self._log_rejection(item)
            
        except Exception as e:
            self.logger.error(f"Error processing rejected file: {e}")
    
    def _log_rejection(self, item: Dict):
        """Log rejection"""
        log_file = self.logs_folder / 'rejections.md'
        
        timestamp = datetime.now().isoformat()
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## {timestamp}\n\n")
            f.write(f"Rejected: {item['path'].name}\n")
            f.write(f"Type: {item['type']}\n")
            f.write(f"Action: {item['action']}\n")
            if item.get('amount'):
                f.write(f"Amount: ${item['amount']}\n")
    
    def run(self, check_interval: int = 30):
        """Run the approval workflow manager"""
        self.logger.info("Starting Approval Workflow Manager")
        self.logger.info(f"Pending: {self.pending_folder}")
        self.logger.info(f"Approved: {self.approved_folder}")
        self.logger.info(f"Rejected: {self.rejected_folder}")
        
        try:
            while True:
                # Check pending approvals
                pending = self.check_pending_approvals()
                if pending:
                    self.notify_human(pending)
                
                # Check approved files
                approved = self.check_approved()
                for filepath in approved:
                    success = self.execute_approved_action(filepath)
                    if success:
                        self.processed_files.add(filepath.stem)
                
                # Check rejected files
                rejected = self.check_rejected()
                for filepath in rejected:
                    self.process_rejected(filepath)
                    self.processed_files.add(filepath.stem)
                
                # Wait before next check
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Approval Workflow Manager stopped")


# Default action handlers
def email_handler(item: Dict) -> bool:
    """Handle approved email action"""
    print(f"  → Would send email: {item.get('recipient', 'unknown')}")
    # Add actual email sending logic here
    return True


def payment_handler(item: Dict) -> bool:
    """Handle approved payment action"""
    print(f"  → Would process payment: ${item.get('amount', 0)} to {item.get('recipient', 'unknown')}")
    # Add actual payment logic here (MCP server, API call, etc.)
    return True


def social_post_handler(item: Dict) -> bool:
    """Handle approved social media post"""
    print(f"  → Would post to social media")
    # Add actual posting logic here
    return True


if __name__ == '__main__':
    import sys
    
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent
    
    print("=" * 60)
    print("Approval Workflow Manager - Personal AI Employee")
    print("=" * 60)
    print(f"\nVault: {vault_path}")
    print("\nWorkflow:")
    print("1. AI creates approval request in /Pending_Approval")
    print("2. Human reviews and moves to /Approved or /Rejected")
    print("3. Approved actions are executed automatically")
    print("\nPress Ctrl+C to stop\n")
    
    # Create manager
    manager = ApprovalWorkflowManager(str(vault_path))
    
    # Register default handlers
    manager.register_handler('email', email_handler)
    manager.register_handler('payment', payment_handler)
    manager.register_handler('social_post', social_post_handler)
    
    # Run
    try:
        manager.run(check_interval=30)
    except KeyboardInterrupt:
        print("\n\nStopped by user")
