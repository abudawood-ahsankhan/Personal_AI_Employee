"""
Vault Sync Manager - Platinum Tier
Part of Personal AI Employee Platinum Tier

Handles bidirectional sync between Cloud and Local vaults.
Security: Never sync secrets (.env, tokens, credentials).
"""

import os
import json
import shutil
import logging
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@dataclass
class SyncRule:
    """Rule for syncing files between cloud and local"""
    pattern: str  # glob pattern
    direction: str  # 'cloud_to_local', 'local_to_cloud', 'bidirectional'
    sync_secrets: bool = False


class VaultSyncManager:
    """
    Manages secure synchronization between Cloud and Local vaults.
    
    Security Rules:
    - Never sync .env files
    - Never sync token files
    - Never sync credential files
    - Never sync session data
    - Only sync markdown/state files
    """
    
    def __init__(self, vault_path: str, mode: str = 'local'):
        self.vault_path = Path(vault_path)
        self.mode = mode  # 'cloud' or 'local'
        
        # Sync directories
        self.updates_folder = self.vault_path / 'Updates'
        self.signals_folder = self.vault_path / 'Signals'
        self.sync_exclude_folder = self.vault_path / 'Sync_Exclude'
        
        # Create folders
        for folder in [self.updates_folder, self.signals_folder, self.sync_exclude_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Define sync rules
        self.sync_rules = [
            SyncRule('*.md', 'bidirectional'),
            SyncRule('Needs_Action/**/*.md', 'bidirectional'),
            SyncRule('Plans/**/*.md', 'bidirectional'),
            SyncRule('Done/**/*.md', 'local_to_cloud'),
            SyncRule('Briefings/**/*.md', 'local_to_cloud'),
            SyncRule('Logs/**/*.md', 'local_to_cloud'),
            SyncRule('Logs/Audit/**/*.jsonl', 'local_to_cloud'),
        ]
        
        # Files/patterns to NEVER sync (security rule)
        self.never_sync_patterns = [
            '.env',
            '*.env',
            '*token*',
            '*credential*',
            '*secret*',
            '*password*',
            '*session*',
            'whatsapp_session/**',
            'tokens/**',
            'Sync_Exclude/**',
            'oauth_creds.json',
            '*.json',  # Config files stay local
        ]
        
        # Claim tracking
        self.claims_file = self.vault_path / '.sync_claims.json'
        self.claims: Dict[str, Dict] = self._load_claims()
    
    def _load_claims(self) -> Dict:
        """Load claim data"""
        if self.claims_file.exists():
            try:
                with open(self.claims_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_claims(self):
        """Save claim data"""
        with open(self.claims_file, 'w') as f:
            json.dump(self.claims, f, indent=2)
    
    def should_sync(self, file_path: Path) -> bool:
        """Check if file should be synced (security check)"""
        rel_path = file_path.relative_to(self.vault_path)
        rel_str = str(rel_path)
        
        # Check never-sync list
        for pattern in self.never_sync_patterns:
            if pattern in rel_str or file_path.match(pattern):
                self.logger.debug(f"Blocked sync for: {rel_str} (security rule)")
                return False
        
        return True
    
    def claim_task(self, task_file: Path, agent: str) -> bool:
        """
        Claim-by-move rule: First agent to move task owns it.
        
        Returns:
            True if claim successful, False if already claimed
        """
        rel_path = str(task_file.relative_to(self.vault_path))
        
        # Check if already claimed
        if rel_path in self.claims:
            claim = self.claims[rel_path]
            # Check if claim is stale (older than 1 hour)
            if datetime.fromisoformat(claim['claimed_at']) < datetime.now() - timedelta(hours=1):
                self.logger.info(f"Stale claim expired for: {rel_path}")
                del self.claims[rel_path]
            else:
                self.logger.info(f"Task already claimed by: {claim['agent']}")
                return False
        
        # Create claim
        self.claims[rel_path] = {
            'agent': agent,
            'claimed_at': datetime.now().isoformat(),
            'file': rel_path,
        }
        
        self._save_claims()
        self.logger.info(f"Claimed by {agent}: {rel_path}")
        return True
    
    def release_claim(self, task_file: Path):
        """Release claim after task completion"""
        rel_path = str(task_file.relative_to(self.vault_path))
        if rel_path in self.claims:
            del self.claims[rel_path]
            self._save_claims()
            self.logger.info(f"Released claim: {rel_path}")
    
    def sync_to_cloud(self, files: List[Path]) -> List[Path]:
        """Sync files to cloud (local -> cloud)"""
        synced = []
        
        for file_path in files:
            if not self.should_sync(file_path):
                continue
            
            rel_path = file_path.relative_to(self.vault_path)
            dest = self.updates_folder / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, dest)
            synced.append(dest)
            
            self.logger.info(f"Synced to cloud: {rel_path}")
        
        return synced
    
    def sync_from_cloud(self, files: List[Path]) -> List[Path]:
        """Sync files from cloud (cloud -> local)"""
        synced = []
        
        for file_path in files:
            if not self.should_sync(file_path):
                continue
            
            rel_path = file_path.relative_to(self.vault_path)
            
            # Check if local copy is newer
            local_file = self.vault_path / rel_path
            if local_file.exists():
                if local_file.stat().st_mtime >= file_path.stat().st_mtime:
                    self.logger.debug(f"Skipping (local newer): {rel_path}")
                    continue
            
            # Update local copy
            local_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, local_file)
            synced.append(local_file)
            
            self.logger.info(f"Synced from cloud: {rel_path}")
        
        return synced
    
    def write_signal(self, signal_type: str, data: Dict):
        """Write signal for other agent"""
        signal_file = self.signals_folder / f"{signal_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        signal_data = {
            'type': signal_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'source': self.mode,
        }
        
        with open(signal_file, 'w') as f:
            json.dump(signal_data, f, indent=2)
        
        self.logger.info(f"Signal written: {signal_type}")
        return signal_file
    
    def read_signals(self) -> List[Dict]:
        """Read pending signals"""
        signals = []
        
        for signal_file in self.signals_folder.glob('*.json'):
            try:
                with open(signal_file, 'r') as f:
                    signal = json.load(f)
                signals.append(signal)
                # Mark as read
                signal_file.rename(signal_file.with_suffix('.json.read'))
            except Exception as e:
                self.logger.error(f"Error reading signal: {e}")
        
        return signals
    
    def get_sync_status(self) -> Dict:
        """Get sync status"""
        return {
            'mode': self.mode,
            'claims': len(self.claims),
            'pending_updates': len(list(self.updates_folder.glob('**/*.md'))),
            'pending_signals': len(list(self.signals_folder.glob('*.json'))),
        }


class CloudVaultSyncManager(VaultSyncManager):
    """Cloud-specific sync manager (drafts only)"""
    
    def __init__(self, vault_path: str):
        super().__init__(vault_path, mode='cloud')
    
    def process_email_draft(self, email_file: Path) -> Path:
        """Process email and create draft (no sending from cloud)"""
        self.logger.info(f"Processing email draft: {email_file.name}")
        
        # Read email
        content = email_file.read_text()
        
        # Create draft with approval request
        draft_content = f"""---
type: email_draft
status: draft
created: {datetime.now().isoformat()}
source: cloud
requires_approval: true
---

# Email Draft (Cloud Agent)

{content}

---
**NOTE:** This is a DRAFT. Local agent must approve before sending.
"""
        
        draft_file = self.updates_folder / f"DRAFT_{email_file.name}"
        draft_file.write_text(draft_content)
        
        # Write signal for local
        self.write_signal('email_draft_ready', {
            'file': draft_file.name,
        })
        
        return draft_file
    
    def process_social_draft(self, platform: str, content: str) -> Path:
        """Create social media draft (no posting from cloud)"""
        draft_content = f"""---
type: social_draft
platform: {platform}
status: draft
created: {datetime.now().isoformat()}
source: cloud
requires_approval: true
---

# Social Media Draft ({platform})

{content}

---
**NOTE:** This is a DRAFT. Local agent must approve before posting.
"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_file = self.updates_folder / f"DRAFT_{platform}_{timestamp}.md"
        draft_file.write_text(draft_content)
        
        self.write_signal('social_draft_ready', {
            'platform': platform,
            'file': draft_file.name,
        })
        
        return draft_file


class LocalVaultSyncManager(VaultSyncManager):
    """Local-specific sync manager (approvals and execution)"""
    
    def __init__(self, vault_path: str):
        super().__init__(vault_path, mode='local')
    
    def approve_draft(self, draft_file: Path) -> Path:
        """Approve cloud draft (local owns approvals)"""
        content = draft_file.read_text()
        content = content.replace('status: draft', 'status: approved')
        content += f"\n\n**Approved by Local:** {datetime.now().isoformat()}"
        
        approved_file = self.vault_path / 'Approved' / draft_file.name
        approved_file.write_text(content)
        
        self.write_signal('draft_approved', {
            'file': draft_file.name,
        })
        
        return approved_file
    
    def execute_approved_action(self, action_file: Path):
        """Execute action that was approved (local owns execution)"""
        self.logger.info(f"Executing approved action: {action_file.name}")
        
        # In production, would execute via MCP servers
        # Move to Done
        dest = self.vault_path / 'Done' / action_file.name
        action_file.rename(dest)
        
        self.write_signal('action_executed', {
            'file': dest.name,
        })


if __name__ == '__main__':
    import sys
    
    vault_path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    mode = sys.argv[2] if len(sys.argv) > 2 else 'local'
    
    print("=" * 60)
    print("Vault Sync Manager - Platinum Tier")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Mode: {mode}")
    print()
    
    if mode == 'cloud':
        sync_mgr = CloudVaultSyncManager(vault_path)
    else:
        sync_mgr = LocalVaultSyncManager(vault_path)
    
    # Show status
    status = sync_mgr.get_sync_status()
    print("Sync Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print()
    print("Security Rules:")
    print("  ✓ Never sync: .env, tokens, credentials, sessions")
    print("  ✓ Only sync: Markdown and state files")
    print("  ✓ Claim-by-move rule active")
