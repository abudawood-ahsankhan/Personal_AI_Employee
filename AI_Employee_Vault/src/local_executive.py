"""
Local Executive - Platinum Tier
Part of Personal AI Employee Platinum Tier

Runs on local machine. Handles:
- Approvals (cloud drafts)
- WhatsApp session (local only)
- Payments/banking (local only)
- Final send/post actions
- Merging cloud updates into Dashboard
"""

import os
import sys
import time
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LocalExecutive:
    """
    Local AI Executive - Runs on local machine.
    
    Responsibilities:
    - Approve/reject cloud drafts
    - Execute WhatsApp actions
    - Execute payments/banking
    - Final send/post actions
    - Merge cloud updates into Dashboard
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Local-specific folders
        self.needs_action_local = self.vault_path / 'Needs_Action' / 'local'
        self.plans_local = self.vault_path / 'Plans' / 'local'
        self.pending_local = self.vault_path / 'Pending_Approval' / 'local'
        self.updates_folder = self.vault_path / 'Updates'
        self.signals_folder = self.vault_path / 'Signals'
        
        # Dashboard
        self.dashboard_file = self.vault_path / 'Dashboard.md'
        
        # Approval folders
        self.approved_folder = self.vault_path / 'Approved'
        self.rejected_folder = self.vault_path / 'Rejected'
        
        # Initialize
        for folder in [self.needs_action_local, self.plans_local, 
                       self.pending_local, self.approved_folder, self.rejected_folder]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def process_cloud_drafts(self):
        """Process drafts from cloud agent"""
        self.logger.info("Processing cloud drafts")
        
        for draft_file in self.updates_folder.glob('DRAFT_*.md'):
            content = draft_file.read_text()
            
            # Determine draft type
            if 'email_draft' in content:
                self._handle_email_draft(draft_file)
            elif 'social_draft' in content:
                self._handle_social_draft(draft_file)
            elif 'accounting_draft' in content:
                self._handle_accounting_draft(draft_file)
            else:
                self._handle_general_draft(draft_file)
    
    def _handle_email_draft(self, draft_file: Path):
        """Handle email draft - create approval request"""
        approval_content = draft_file.read_text()
        approval_content += f"""

---
# Approval Request

**Type:** Email Reply  
**Created:** {datetime.now().isoformat()}  
**Source:** Cloud Agent

**To Approve:** Move this file to /Approved folder  
**To Reject:** Move this file to /Rejected folder
"""
        
        approval_file = self.pending_local / f"APPROVAL_{draft_file.name}"
        approval_file.write_text(approval_content)
        
        self.logger.info(f"Email approval request: {approval_file.name}")
    
    def _handle_social_draft(self, draft_file: Path):
        """Handle social draft - create approval request"""
        # Extract platform
        content = draft_file.read_text()
        platform = 'unknown'
        for p in ['linkedin', 'facebook', 'twitter', 'instagram']:
            if p in draft_file.name.lower():
                platform = p
                break
        
        approval_content = f"""---
type: social_approval
platform: {platform}
status: pending
created: {datetime.now().isoformat()}
source: cloud_agent
---

# Social Media Approval Request

**Platform:** {platform}  
**Created:** {datetime.now().isoformat()}

{content}

---
**To Approve:** Move to /Approved  
**To Reject:** Move to /Rejected
"""
        
        approval_file = self.pending_local / f"APPROVAL_{draft_file.name}"
        approval_file.write_text(approval_content)
        
        self.logger.info(f"Social approval request: {approval_file.name}")
    
    def _handle_accounting_draft(self, draft_file: Path):
        """Handle accounting draft - create approval request"""
        approval_content = f"""---
type: accounting_approval
status: pending
created: {datetime.now().isoformat()}
source: cloud_agent
---

# Accounting Approval Request

{draft_file.read_text()}

---
**To Approve:** Move to /Approved  
**To Reject:** Move to /Rejected
"""
        
        approval_file = self.pending_local / f"APPROVAL_{draft_file.name}"
        approval_file.write_text(approval_content)
        
        self.logger.info(f"Accounting approval request: {approval_file.name}")
    
    def _handle_general_draft(self, draft_file: Path):
        """Handle general draft"""
        self.logger.info(f"General draft: {draft_file.name}")
    
    def check_approvals(self):
        """Check approved folder and execute actions"""
        for approval_file in self.approved_folder.glob('*.md'):
            self.logger.info(f"Executing approved: {approval_file.name}")
            
            # Execute based on type
            content = approval_file.read_text()
            
            if 'email' in content.lower():
                self._execute_email(approval_file)
            elif 'social' in content.lower():
                self._execute_social(approval_file)
            elif 'payment' in content.lower() or 'accounting' in content.lower():
                self._execute_payment(approval_file)
            else:
                self._execute_general(approval_file)
    
    def _execute_email(self, approval_file: Path):
        """Execute approved email (local owns sending)"""
        self.logger.info(f"Sending approved email: {approval_file.name}")
        
        # In production, would use Email MCP server
        # For now, mark as sent
        content = approval_file.read_text()
        content += f"\n\n**Sent by Local:** {datetime.now().isoformat()}"
        approval_file.write_text(content)
        
        # Move to Done
        dest = self.vault_path / 'Done' / approval_file.name
        approval_file.rename(dest)
        
        self.logger.info(f"Email sent: {dest.name}")
    
    def _execute_social(self, approval_file: Path):
        """Execute approved social post (local owns posting)"""
        self.logger.info(f"Posting approved social: {approval_file.name}")
        
        # In production, would use Social MCP servers
        content = approval_file.read_text()
        content += f"\n\n**Posted by Local:** {datetime.now().isoformat()}"
        approval_file.write_text(content)
        
        # Move to Done
        dest = self.vault_path / 'Done' / approval_file.name
        approval_file.rename(dest)
        
        self.logger.info(f"Social posted: {dest.name}")
    
    def _execute_payment(self, approval_file: Path):
        """Execute approved payment (local owns payments)"""
        self.logger.info(f"Executing approved payment: {approval_file.name}")
        
        # In production, would use Odoo MCP server
        content = approval_file.read_text()
        content += f"\n\n**Executed by Local:** {datetime.now().isoformat()}"
        approval_file.write_text(content)
        
        # Move to Done
        dest = self.vault_path / 'Done' / approval_file.name
        approval_file.rename(dest)
        
        self.logger.info(f"Payment executed: {dest.name}")
    
    def _execute_general(self, approval_file: Path):
        """Execute general approved action"""
        self.logger.info(f"Executing approved general: {approval_file.name}")
        
        content = approval_file.read_text()
        content += f"\n\n**Executed by Local:** {datetime.now().isoformat()}"
        approval_file.write_text(content)
        
        dest = self.vault_path / 'Done' / approval_file.name
        approval_file.rename(dest)
    
    def merge_cloud_updates(self):
        """Merge cloud updates into local Dashboard"""
        self.logger.info("Merging cloud updates")
        
        # Read current dashboard
        if not self.dashboard_file.exists():
            self.logger.warning("Dashboard not found")
            return
        
        dashboard = self.dashboard_file.read_text()
        
        # Read cloud updates
        cloud_updates = []
        for update_file in self.updates_folder.glob('*.md'):
            cloud_updates.append(update_file.read_text())
        
        # Merge into dashboard
        if cloud_updates:
            dashboard += f"\n\n## Cloud Agent Updates ({datetime.now().strftime('%Y-%m-%d')})\n"
            for i, update in enumerate(cloud_updates[:5], 1):  # Max 5 updates
                dashboard += f"\n### Update {i}\n{update[:500]}...\n"
            
            self.dashboard_file.write_text(dashboard)
            self.logger.info(f"Merged {len(cloud_updates)} cloud updates")
    
    def run_whatsapp_session(self):
        """Run WhatsApp session (local only)"""
        self.logger.info("WhatsApp session: local only")
        # In production, would run WhatsApp watcher here
        pass
    
    def run(self, once: bool = False):
        """Run local executive"""
        self.logger.info("Starting Local Executive")
        self.logger.info(f"Vault: {self.vault_path}")
        
        try:
            while True:
                # Process cloud drafts
                self.process_cloud_drafts()
                
                # Check approvals
                self.check_approvals()
                
                # Merge cloud updates
                self.merge_cloud_updates()
                
                if once:
                    break
                
                time.sleep(60)
        
        except KeyboardInterrupt:
            self.logger.info("Local Executive stopped")


if __name__ == '__main__':
    vault_path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    once = '--once' in sys.argv
    
    executive = LocalExecutive(vault_path)
    executive.run(once=once)
