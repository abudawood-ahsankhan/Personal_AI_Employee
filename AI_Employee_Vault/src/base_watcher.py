"""
Base Watcher Module

Abstract base class for all watcher scripts in the Personal AI Employee system.
All watchers follow the same pattern: monitor -> detect -> create action file.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    Watchers are lightweight Python scripts that run continuously in the background,
    monitoring various inputs (email, WhatsApp, filesystem, etc.) and creating
    actionable .md files in the Needs_Action folder for Claude Code to process.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs_dir = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
        self.logger.info(f'{self.__class__.__name__} initialized')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {check_interval}s')
    
    def _setup_logging(self):
        """Configure logging for the watcher."""
        log_file = self.logs_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items that need processing.
        
        Returns:
            List of new items to process
            
        This method must be implemented by each watcher subclass.
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file, or None if creation failed
            
        This method must be implemented by each watcher subclass.
        """
        pass
    
    def generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a unique filename for an action file.
        
        Args:
            prefix: File prefix (e.g., 'EMAIL', 'WHATSAPP', 'FILE')
            unique_id: Unique identifier for the item
            
        Returns:
            Filename string
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{prefix}_{unique_id}_{timestamp}.md'
    
    def create_metadata_file(self, action_file: Path, metadata: dict) -> Path:
        """
        Create a companion metadata file for an action file.
        
        Args:
            action_file: Path to the main action file
            metadata: Dictionary of metadata to store
            
        Returns:
            Path to the metadata file
        """
        meta_path = action_file.with_suffix('.meta.json')
        import json
        meta_path.write_text(json.dumps(metadata, indent=2, default=str))
        return meta_path
    
    def log_action(self, action_type: str, details: dict):
        """
        Log an action to the daily log file.
        
        Args:
            action_type: Type of action (e.g., 'file_created', 'item_detected')
            details: Dictionary of action details
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'watcher': self.__class__.__name__,
            'action_type': action_type,
            'details': details
        }
        
        log_file = self.logs_dir / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        
        import json
        try:
            if log_file.exists():
                logs = json.loads(log_file.read_text())
            else:
                logs = []
            logs.append(log_entry)
            log_file.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            self.logger.error(f'Failed to write log: {e}')
    
    def run(self):
        """
        Main run loop for the watcher.
        
        Continuously checks for updates and creates action files.
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__} main loop')
        self.logger.info('Press Ctrl+C to stop')
        
        try:
            while True:
                try:
                    # Check for new items
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s) to process')
                        
                        for item in items:
                            try:
                                action_file = self.create_action_file(item)
                                if action_file:
                                    self.logger.info(f'Created action file: {action_file.name}')
                                    self.log_action('file_created', {
                                        'file': str(action_file),
                                        'item_type': type(item).__name__
                                    })
                            except Exception as e:
                                self.logger.error(f'Failed to create action file: {e}')
                    
                    # Wait before next check
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    self.logger.error(f'Error in main loop: {e}')
                    self.logger.info(f'Retrying in {self.check_interval}s...')
                    time.sleep(self.check_interval)
                    
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


if __name__ == '__main__':
    # This is an abstract class - show usage example
    print("BaseWatcher is an abstract base class.")
    print("Create a subclass implementing check_for_updates() and create_action_file()")
    print("\nExample:")
    print("  class MyWatcher(BaseWatcher):")
    print("      def check_for_updates(self) -> list:")
    print("          # Your detection logic here")
    print("          return []")
    print("\n      def create_action_file(self, item) -> Path:")
    print("          # Your file creation logic here")
    print("          return path")
