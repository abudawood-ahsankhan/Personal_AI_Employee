"""
Error Recovery and Graceful Degradation System
Part of Personal AI Employee Gold Tier

Handles error states, retry logic, and graceful degradation when components fail.
"""

import time
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from functools import wraps
import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ErrorCategories:
    """Error category definitions"""
    TRANSIENT = 'transient'  # Network timeout, API rate limit
    AUTHENTICATION = 'authentication'  # Expired token, revoked access
    LOGIC = 'logic'  # Claude misinterprets message
    DATA = 'data'  # Corrupted file, missing field
    SYSTEM = 'system'  # Process crash, disk full


class RecoveryStrategies:
    """Recovery strategy definitions"""
    RETRY = 'retry'  # Exponential backoff retry
    ALERT = 'alert'  # Alert human, pause operations
    REVIEW = 'review'  # Human review queue
    QUARANTINE = 'quarantine'  # Quarantine + alert
    RESTART = 'restart'  # Auto-restart process


class ErrorRecoveryManager:
    """
    Manages error recovery and graceful degradation for the AI Employee system.
    """
    
    def __init__(self, vault_path: str, config: Dict = None):
        self.vault_path = Path(vault_path)
        self.config = config or {}
        
        # Folders
        self.errors_folder = self.vault_path / 'Errors'
        self.quarantine_folder = self.vault_path / 'Quarantine'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.errors_folder, self.quarantine_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration
        self.max_retries = self.config.get('max_retries', 3)
        self.base_delay = self.config.get('base_delay', 1)  # seconds
        self.max_delay = self.config.get('max_delay', 60)  # seconds
        self.alert_threshold = self.config.get('alert_threshold', 5)  # errors before alert
        
        # Error tracking
        self.error_counts: Dict[str, int] = {}
        self.last_error_time: Dict[str, datetime] = {}
        
        # Recovery handlers
        self.recovery_handlers: Dict[str, Callable] = {
            ErrorCategories.TRANSIENT: self._handle_transient,
            ErrorCategories.AUTHENTICATION: self._handle_authentication,
            ErrorCategories.LOGIC: self._handle_logic,
            ErrorCategories.DATA: self._handle_data,
            ErrorCategories.SYSTEM: self._handle_system,
        }
        
        # Circuit breaker state
        self.circuit_breaker: Dict[str, Dict] = {}
    
    def with_retry(self, error_category: str = ErrorCategories.TRANSIENT):
        """
        Decorator for automatic retry with exponential backoff
        
        Usage:
            @error_manager.with_retry(ErrorCategories.TRANSIENT)
            def my_function():
                ...
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_with_retry(func, error_category, *args, **kwargs)
            return wrapper
        return decorator
    
    def _execute_with_retry(self, func: Callable, error_category: str, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                # Log error
                self.log_error(error_category, str(e), func.__name__)
                
                # Check if should retry
                if attempt < self.max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"All {self.max_retries} attempts failed")
        
        # All retries exhausted
        self._handle_persistent_failure(error_category, last_error, func.__name__)
        raise last_error
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        # Add jitter (±25%)
        jitter = delay * 0.25 * (random.random() * 2 - 1)
        return delay + jitter
    
    def handle_error(self, error_category: str, error: Exception, context: str = ''):
        """Handle an error with appropriate recovery strategy"""
        handler = self.recovery_handlers.get(error_category, self._handle_transient)
        return handler(error, context)
    
    def _handle_transient(self, error: Exception, context: str = '') -> bool:
        """Handle transient errors - retry with backoff"""
        self.logger.info(f"Handling transient error: {error}")
        # Retry is handled by decorator
        return True
    
    def _handle_authentication(self, error: Exception, context: str = '') -> bool:
        """Handle authentication errors - alert and pause"""
        self.logger.error(f"Authentication error: {error}")
        
        # Alert human
        self._alert_human(f"Authentication error in {context}: {error}")
        
        # Pause operations for this component
        self._open_circuit_breaker(context or 'auth')
        
        return False
    
    def _handle_logic(self, error: Exception, context: str = '') -> bool:
        """Handle logic errors - send to review queue"""
        self.logger.warning(f"Logic error: {error}")
        
        # Quarantine for human review
        self._quarantine(context, str(error))
        
        return False
    
    def _handle_data(self, error: Exception, context: str = '') -> bool:
        """Handle data errors - quarantine and alert"""
        self.logger.error(f"Data error: {error}")
        
        # Quarantine corrupted data
        self._quarantine(context, str(error))
        
        # Alert if threshold reached
        if self._should_alert('data'):
            self._alert_human(f"Multiple data errors detected: {error}")
        
        return False
    
    def _handle_system(self, error: Exception, context: str = '') -> bool:
        """Handle system errors - attempt restart"""
        self.logger.critical(f"System error: {error}")
        
        # Alert human
        self._alert_human(f"System error: {error}")
        
        # Attempt restart
        return self._attempt_restart(context)
    
    def _handle_persistent_failure(self, error_category: str, error: Exception, context: str):
        """Handle persistent failure after all retries exhausted"""
        self.logger.error(f"Persistent failure in {context}: {error}")
        
        # Log to errors folder
        self._log_persistent_failure(error_category, error, context)
        
        # Alert human
        self._alert_human(f"Persistent failure after {self.max_retries} retries: {error}")
    
    def _open_circuit_breaker(self, component: str):
        """Open circuit breaker for a component (pause operations)"""
        self.circuit_breaker[component] = {
            'state': 'open',
            'opened_at': datetime.now(),
            'failures': self.error_counts.get(component, 0) + 1
        }
        self.logger.warning(f"Circuit breaker opened for: {component}")
    
    def _close_circuit_breaker(self, component: str):
        """Close circuit breaker (resume operations)"""
        if component in self.circuit_breaker:
            self.circuit_breaker[component]['state'] = 'closed'
            self.logger.info(f"Circuit breaker closed for: {component}")
    
    def is_circuit_open(self, component: str) -> bool:
        """Check if circuit breaker is open"""
        if component not in self.circuit_breaker:
            return False
        
        cb = self.circuit_breaker[component]
        if cb['state'] != 'open':
            return False
        
        # Auto-close after 5 minutes
        if datetime.now() - cb['opened_at'] > timedelta(minutes=5):
            self._close_circuit_breaker(component)
            return False
        
        return True
    
    def _alert_human(self, message: str):
        """Alert human operator"""
        # Create alert file
        alert_file = self.errors_folder / f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        content = f"""---
type: alert
created: {datetime.now().isoformat()}
severity: high
---

# Human Attention Required

{message}

---
*Generated by Error Recovery Manager*
"""
        alert_file.write_text(content, encoding='utf-8')
        
        self.logger.critical(f"ALERT: {message}")
    
    def _quarantine(self, context: str, error: str):
        """Quarantine item for human review"""
        quarantine_file = self.quarantine_folder / f"QUARANTINE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        content = f"""---
type: quarantine
created: {datetime.now().isoformat()}
context: {context}
---

# Item Quarantined for Review

**Context:** {context}  
**Error:** {error}

---
*Move to /Done after review, or /Rejected if invalid*
"""
        quarantine_file.write_text(content, encoding='utf-8')
    
    def _attempt_restart(self, component: str) -> bool:
        """Attempt to restart a component"""
        self.logger.info(f"Attempting restart of: {component}")
        # In production, this would actually restart the process
        return True
    
    def _should_alert(self, error_type: str) -> bool:
        """Check if alert threshold reached"""
        count = self.error_counts.get(error_type, 0)
        return count >= self.alert_threshold
    
    def log_error(self, category: str, message: str, context: str = ''):
        """Log error for tracking"""
        # Update counts
        self.error_counts[category] = self.error_counts.get(category, 0) + 1
        self.last_error_time[category] = datetime.now()
        
        # Log to file
        log_file = self.logs_folder / f"errors_{datetime.now().strftime('%Y%m%d')}.json"
        
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'message': message,
            'context': context,
        }
        
        # Append to log file
        errors = []
        if log_file.exists():
            try:
                errors = json.loads(log_file.read_text())
            except:
                errors = []
        
        errors.append(error_entry)
        log_file.write_text(json.dumps(errors, indent=2), encoding='utf-8')
    
    def _log_persistent_failure(self, category: str, error: Exception, context: str):
        """Log persistent failure"""
        failure_file = self.errors_folder / f"FAILURE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        content = f"""---
type: persistent_failure
created: {datetime.now().isoformat()}
category: {category}
context: {context}
---

# Persistent Failure

**Category:** {category}  
**Context:** {context}  
**Error:** {error}

---
*Requires human intervention*
"""
        failure_file.write_text(content, encoding='utf-8')
    
    def get_status(self) -> Dict:
        """Get error recovery system status"""
        return {
            'error_counts': dict(self.error_counts),
            'circuit_breakers': dict(self.circuit_breaker),
            'last_errors': {
                k: v.isoformat() for k, v in self.last_error_time.items()
            },
        }


# Graceful degradation decorators
def degrade_gracefully(default_value: Any = None):
    """
    Decorator for graceful degradation - returns default value on error
    
    Usage:
        @degrade_gracefully(default_value=[])
        def get_data():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.warning(f"Graceful degradation for {func.__name__}: {e}")
                return default_value
        return wrapper
    return decorator


if __name__ == '__main__':
    import sys
    
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent
    
    # Create error recovery manager
    error_manager = ErrorRecoveryManager(str(vault_path))
    
    print("Error Recovery Manager Status:")
    print(json.dumps(error_manager.get_status(), indent=2))
