"""
File System Watcher Module

Monitors a drop folder for new files and creates action files in the Needs_Action folder.
This is the simplest watcher to test and is perfect for the Bronze Tier.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/drop_folder
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from base_watcher import BaseWatcher


class FileDropItem:
    """Represents a file dropped for processing."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.name = file_path.name
        self.size = file_path.stat().st_size
        self.created = datetime.fromtimestamp(file_path.stat().st_ctime)
        self.modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        self.content_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate MD5 hash of file content for deduplication."""
        hash_md5 = hashlib.md5()
        with open(self.file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_extension(self) -> str:
        """Get file extension (lowercase, without dot)."""
        return self.file_path.suffix.lower().lstrip('.')
    
    def get_type_category(self) -> str:
        """Categorize file by extension."""
        categories = {
            'document': ['pdf', 'doc', 'docx', 'txt', 'md', 'rtf'],
            'spreadsheet': ['xls', 'xlsx', 'csv', 'ods'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'],
            'archive': ['zip', 'rar', '7z', 'tar', 'gz'],
            'data': ['json', 'xml', 'yaml', 'yml'],
        }
        
        ext = self.get_extension()
        for category, extensions in categories.items():
            if ext in extensions:
                return category
        return 'other'


class FilesystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files and creates action files.
    
    When a file is detected:
    1. Copy it to the vault's Inbox folder
    2. Create a .md action file in Needs_Action with metadata
    3. Log the action
    """
    
    def __init__(self, vault_path: str, drop_folder: str, check_interval: int = 30):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            drop_folder: Path to the folder to monitor for new files
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        self.drop_folder = Path(drop_folder)
        self.inbox = self.vault_path / 'Inbox'
        
        # Ensure drop folder exists
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash
        self.processed_hashes: set = set()
        
        self.logger.info(f'Drop folder: {self.drop_folder}')
    
    def check_for_updates(self) -> List[FileDropItem]:
        """
        Check the drop folder for new files.
        
        Returns:
            List of FileDropItem objects for new files
        """
        new_items = []
        
        try:
            # Get all files in drop folder (not subdirectories)
            files = [f for f in self.drop_folder.iterdir() if f.is_file()]
            
            for file_path in files:
                try:
                    item = FileDropItem(file_path)
                    
                    # Skip if already processed
                    if item.content_hash in self.processed_hashes:
                        self.logger.debug(f'Skipping already processed: {item.name}')
                        continue
                    
                    new_items.append(item)
                    self.logger.info(f'New file detected: {item.name} ({item.size} bytes)')
                    
                except Exception as e:
                    self.logger.error(f'Error processing file {file_path}: {e}')
            
        except Exception as e:
            self.logger.error(f'Error checking drop folder: {e}')
        
        return new_items
    
    def create_action_file(self, item: FileDropItem) -> Optional[Path]:
        """
        Create an action file for the dropped file.
        
        Args:
            item: FileDropItem to create action file for
            
        Returns:
            Path to the created action file
        """
        try:
            # Copy file to Inbox
            dest_path = self.inbox / item.name
            
            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = Path(item.name).stem
                suffix = Path(item.name).suffix
                dest_path = self.inbox / f'{stem}_{counter}{suffix}'
                counter += 1
            
            shutil.copy2(item.file_path, dest_path)
            self.logger.info(f'Copied file to Inbox: {dest_path.name}')
            
            # Categorize the file
            file_type = item.get_type_category()
            
            # Determine suggested actions based on file type
            suggested_actions = self._get_suggested_actions(file_type, item.get_extension())
            
            # Create the action file content
            content = f'''---
type: file_drop
source: {item.file_path}
original_name: {item.name}
inbox_path: {dest_path}
file_size: {item.size}
file_type: {file_type}
extension: {item.get_extension()}
content_hash: {item.content_hash}
received: {datetime.now().isoformat()}
status: pending
priority: medium
---

# File Drop: {item.name}

## File Information
- **Size:** {self._format_size(item.size)}
- **Type:** {file_type} ({item.get_extension().upper()})
- **Received:** {item.modified.strftime('%Y-%m-%d %H:%M:%S')}
- **Location:** `Inbox/{dest_path.name}`

## Content Hash
`{item.content_hash}`

## Suggested Actions
{self._format_actions(suggested_actions)}

## Notes
*Add any context or instructions for processing this file*

---
*Generated by Filesystem Watcher v0.1*
'''
            
            # Generate unique filename
            filename = self.generate_filename('FILE', item.content_hash[:8])
            action_file = self.needs_action / filename
            action_file.write_text(content)
            
            # Mark as processed
            self.processed_hashes.add(item.content_hash)
            
            # Remove original from drop folder (optional - can be disabled)
            # item.file_path.unlink()
            
            return action_file
            
        except Exception as e:
            self.logger.error(f'Failed to create action file: {e}')
            return None
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.1f} {unit}'
            size /= 1024
        return f'{size:.1f} TB'
    
    def _get_suggested_actions(self, file_type: str, extension: str) -> List[str]:
        """Get suggested actions based on file type."""
        actions = {
            'document': [
                '[ ] Review document content',
                '[ ] Categorize and tag',
                '[ ] Move to appropriate folder',
                '[ ] Archive after processing'
            ],
            'spreadsheet': [
                '[ ] Review data content',
                '[ ] Import to accounting system (if financial)',
                '[ ] Update Dashboard metrics',
                '[ ] Archive after processing'
            ],
            'image': [
                '[ ] Review image content',
                '[ ] Add to media library',
                '[ ] Use in content if relevant',
                '[ ] Archive after processing'
            ],
            'archive': [
                '[ ] Extract archive contents',
                '[ ] Process individual files',
                '[ ] Delete archive after extraction'
            ],
            'data': [
                '[ ] Parse data content',
                '[ ] Import to relevant system',
                '[ ] Validate data integrity',
                '[ ] Archive after processing'
            ],
            'other': [
                '[ ] Review file content',
                '[ ] Determine appropriate action',
                '[ ] Process or archive'
            ]
        }
        return actions.get(file_type, actions['other'])
    
    def _format_actions(self, actions: List[str]) -> str:
        """Format actions as markdown checklist."""
        return '\n'.join(f'- {action}' for action in actions)


def main():
    """Main entry point for the filesystem watcher."""
    # Default paths
    default_vault = Path(__file__).parent.parent
    default_drop = default_vault / 'Drop'
    
    # Parse command line arguments
    if len(sys.argv) >= 2:
        vault_path = sys.argv[1]
    else:
        vault_path = str(default_vault)
        print(f'Using default vault: {vault_path}')
    
    if len(sys.argv) >= 3:
        drop_folder = sys.argv[2]
    else:
        drop_folder = str(default_drop)
        print(f'Using default drop folder: {drop_folder}')
    
    # Create and run watcher
    watcher = FilesystemWatcher(vault_path, drop_folder, check_interval=30)
    
    print(f'\n📁 Filesystem Watcher Started')
    print(f'   Vault: {vault_path}')
    print(f'   Drop Folder: {drop_folder}')
    print(f'   Check Interval: 30s')
    print(f'\n   Drop files into the drop folder to create action files.')
    print(f'   Press Ctrl+C to stop.\n')
    
    watcher.run()


if __name__ == '__main__':
    main()
