"""
Base Watcher Class - Template for all Watcher scripts
Part of Personal AI Employee Silver Tier
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseWatcher(ABC):
    """
    Abstract base class for all Watcher scripts.
    Watchers monitor external systems and create action files in Needs_Action folder.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processed_ids = set()
        
        # Ensure Needs_Action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Load previously processed IDs to avoid duplicates
        self._load_processed_ids()
    
    def _load_processed_ids(self):
        """Load previously processed item IDs from cache file"""
        cache_file = self.vault_path / f'.processed_{self.__class__.__name__.lower()}.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.processed_ids = set(json.load(f))
                self.logger.info(f"Loaded {len(self.processed_ids)} previously processed IDs")
            except Exception as e:
                self.logger.warning(f"Could not load processed IDs: {e}")
                self.processed_ids = set()
    
    def _save_processed_ids(self):
        """Save processed item IDs to cache file"""
        cache_file = self.vault_path / f'.processed_{self.__class__.__name__.lower()}.json'
        try:
            # Keep only last 1000 IDs to prevent unbounded growth
            ids_list = list(self.processed_ids)[-1000:]
            with open(cache_file, 'w') as f:
                json.dump(ids_list, f)
        except Exception as e:
            self.logger.warning(f"Could not save processed IDs: {e}")
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check the external system for new items.
        Returns a list of items that need processing.
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a .md action file in the Needs_Action folder.
        Returns the path to the created file.
        """
        pass
    
    def run(self):
        """Main run loop - continuously checks for updates"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    self.logger.info(f'Found {len(items)} new item(s) to process')
                    
                    for item in items:
                        try:
                            action_file = self.create_action_file(item)
                            self.logger.info(f'Created action file: {action_file.name}')
                        except Exception as e:
                            self.logger.error(f'Error creating action file: {e}')
                    
                    # Save processed IDs after each check
                    self._save_processed_ids()
                    
                except Exception as e:
                    self.logger.error(f'Error in check cycle: {e}')
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
            self._save_processed_ids()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
