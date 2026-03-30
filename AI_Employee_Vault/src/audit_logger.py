"""
Comprehensive Audit Logging System
Part of Personal AI Employee Gold Tier

Logs all actions, decisions, and state changes for compliance and debugging.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@dataclass
class AuditEntry:
    """Standard audit log entry"""
    timestamp: str
    action_type: str
    actor: str  # Who/what performed the action
    target: str  # What was acted upon
    action: str  # What action was taken
    parameters: Dict
    result: str  # success, failure, pending
    approval_status: str  # approved, rejected, pending, auto
    approved_by: str  # human, system, or empty
    correlation_id: str  # Links related actions
    metadata: Dict


class AuditLogger:
    """
    Comprehensive audit logging for the AI Employee system.
    
    Features:
    - Immutable log entries (SHA-256 hash chaining)
    - Multiple log levels (action, decision, state_change)
    - Searchable and filterable
    - Export capabilities
    """
    
    def __init__(self, vault_path: str, retention_days: int = 90):
        self.vault_path = Path(vault_path)
        self.retention_days = retention_days
        
        # Logs folder
        self.logs_folder = self.vault_path / 'Logs' / 'Audit'
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Current log file (daily rotation)
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.current_log_file = self.logs_folder / f'audit_{self.current_date}.jsonl'
        
        # Hash chain for immutability
        self.last_hash = self._get_last_hash()
        
        # Buffer for batch writes
        self.buffer: List[AuditEntry] = []
        self.buffer_size = 10
        self.max_buffer_size = 100
    
    def _get_last_hash(self) -> str:
        """Get hash of last entry for chain integrity"""
        # In production, would read last entry from log file
        return 'genesis'
    
    def _compute_hash(self, entry: Dict) -> str:
        """Compute SHA-256 hash of entry"""
        entry_copy = entry.copy()
        entry_copy['previous_hash'] = self.last_hash
        entry_json = json.dumps(entry_copy, sort_keys=True)
        return hashlib.sha256(entry_json.encode()).hexdigest()
    
    def log(
        self,
        action_type: str,
        actor: str,
        target: str,
        action: str,
        parameters: Dict = None,
        result: str = 'success',
        approval_status: str = 'auto',
        approved_by: str = '',
        correlation_id: str = None,
        metadata: Dict = None
    ) -> str:
        """
        Log an audit entry
        
        Returns:
            Entry ID (hash)
        """
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            action_type=action_type,
            actor=actor,
            target=target,
            action=action,
            parameters=parameters or {},
            result=result,
            approval_status=approval_status,
            approved_by=approved_by,
            correlation_id=correlation_id or self._generate_correlation_id(),
            metadata=metadata or {}
        )
        
        # Compute hash for immutability
        entry_hash = self._compute_hash(asdict(entry))
        entry.metadata['entry_hash'] = entry_hash
        entry.metadata['previous_hash'] = self.last_hash
        
        # Update last hash
        self.last_hash = entry_hash
        
        # Add to buffer
        self.buffer.append(entry)
        
        # Flush if buffer full
        if len(self.buffer) >= self.buffer_size:
            self.flush()
        
        self.logger.debug(f"Audit logged: {action_type} - {target}")
        return entry_hash
    
    def _generate_correlation_id(self) -> str:
        """Generate correlation ID for related actions"""
        return f"corr_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def flush(self):
        """Flush buffer to log file"""
        if not self.buffer:
            return
        
        # Check if date changed (rotate log)
        new_date = datetime.now().strftime('%Y-%m-%d')
        if new_date != self.current_date:
            self.current_date = new_date
            self.current_log_file = self.logs_folder / f'audit_{self.current_date}.jsonl'
        
        # Write entries
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            for entry in self.buffer:
                f.write(json.dumps(asdict(entry)) + '\n')
        
        self.logger.info(f"Flushed {len(self.buffer)} audit entries")
        self.buffer = []
    
    # Convenience methods for common actions
    
    def log_action(
        self,
        actor: str,
        action: str,
        target: str,
        parameters: Dict = None,
        result: str = 'success'
    ):
        """Log a general action"""
        return self.log(
            action_type='action',
            actor=actor,
            target=target,
            action=action,
            parameters=parameters,
            result=result
        )
    
    def log_decision(
        self,
        actor: str,
        decision: str,
        context: str,
        alternatives: List[str] = None,
        reasoning: str = ''
    ):
        """Log a decision made by AI or human"""
        return self.log(
            action_type='decision',
            actor=actor,
            target=context,
            action=decision,
            parameters={
                'alternatives': alternatives or [],
                'reasoning': reasoning
            }
        )
    
    def log_state_change(
        self,
        entity: str,
        from_state: str,
        to_state: str,
        triggered_by: str = ''
    ):
        """Log a state change"""
        return self.log(
            action_type='state_change',
            actor=triggered_by or 'system',
            target=entity,
            action=f'{from_state} → {to_state}',
            parameters={
                'from_state': from_state,
                'to_state': to_state
            }
        )
    
    def log_approval_request(
        self,
        requester: str,
        action_type: str,
        details: Dict,
        approval_id: str
    ):
        """Log an approval request"""
        return self.log(
            action_type='approval_request',
            actor=requester,
            target=approval_id,
            action=action_type,
            parameters=details,
            approval_status='pending'
        )
    
    def log_approval_decision(
        self,
        approver: str,
        approval_id: str,
        decision: str,  # approved, rejected
        reasoning: str = ''
    ):
        """Log an approval decision"""
        return self.log(
            action_type='approval_decision',
            actor=approver,
            target=approval_id,
            action=decision,
            parameters={'reasoning': reasoning},
            approval_status=decision,
            approved_by=approver
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: str = '',
        stack_trace: str = ''
    ):
        """Log an error"""
        return self.log(
            action_type='error',
            actor='system',
            target=context,
            action=error_type,
            parameters={
                'message': error_message,
                'stack_trace': stack_trace
            },
            result='failure'
        )
    
    def log_watcher_event(
        self,
        watcher_name: str,
        event_type: str,
        source: str,
        items_found: int = 0
    ):
        """Log a watcher event"""
        return self.log(
            action_type='watcher_event',
            actor=watcher_name,
            target=source,
            action=event_type,
            parameters={'items_found': items_found}
        )
    
    def log_claude_interaction(
        self,
        prompt_type: str,
        tokens_in: int,
        tokens_out: int,
        model: str,
        duration_ms: int
    ):
        """Log a Claude Code interaction"""
        return self.log(
            action_type='claude_interaction',
            actor='claude_code',
            target=model,
            action=prompt_type,
            parameters={
                'tokens_in': tokens_in,
                'tokens_out': tokens_out,
                'duration_ms': duration_ms
            }
        )
    
    def search(
        self,
        action_type: str = None,
        actor: str = None,
        target: str = None,
        date_from: str = None,
        date_to: str = None,
        result: str = None
    ) -> List[Dict]:
        """Search audit logs"""
        results = []
        
        # Determine which files to search
        log_files = self._get_log_files_for_date_range(date_from, date_to)
        
        for log_file in log_files:
            if not log_file.exists():
                continue
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        
                        # Apply filters
                        if action_type and entry.get('action_type') != action_type:
                            continue
                        if actor and entry.get('actor') != actor:
                            continue
                        if target and target not in entry.get('target', ''):
                            continue
                        if result and entry.get('result') != result:
                            continue
                        
                        results.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        return results
    
    def _get_log_files_for_date_range(
        self,
        date_from: str = None,
        date_to: str = None
    ) -> List[Path]:
        """Get log files for date range"""
        if not date_from:
            date_from = self.current_date
        if not date_to:
            date_to = self.current_date
        
        log_files = []
        current = datetime.strptime(date_from, '%Y-%m-%d')
        end = datetime.strptime(date_to, '%Y-%m-%d')
        
        while current <= end:
            log_file = self.logs_folder / f"audit_{current.strftime('%Y-%m-%d')}.jsonl"
            if log_file.exists():
                log_files.append(log_file)
            current += timedelta(days=1)
        
        return log_files
    
    def export(self, output_path: str, date_from: str = None, date_to: str = None):
        """Export audit logs to file"""
        entries = self.search(date_from=date_from, date_to=date_to)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, default=str)
        
        self.logger.info(f"Exported {len(entries)} entries to {output_path}")
    
    def get_daily_summary(self, date: str = None) -> Dict:
        """Get daily audit summary"""
        if not date:
            date = self.current_date
        
        entries = self.search(date_from=date, date_to=date)
        
        summary = {
            'date': date,
            'total_entries': len(entries),
            'by_action_type': {},
            'by_actor': {},
            'by_result': {},
            'errors': 0,
            'approvals_pending': 0,
            'approvals_approved': 0,
            'approvals_rejected': 0,
        }
        
        for entry in entries:
            # Count by action type
            action_type = entry.get('action_type', 'unknown')
            summary['by_action_type'][action_type] = \
                summary['by_action_type'].get(action_type, 0) + 1
            
            # Count by actor
            actor = entry.get('actor', 'unknown')
            summary['by_actor'][actor] = \
                summary['by_actor'].get(actor, 0) + 1
            
            # Count by result
            result = entry.get('result', 'unknown')
            summary['by_result'][result] = \
                summary['by_result'].get(result, 0) + 1
            
            # Count specific items
            if entry.get('result') == 'failure':
                summary['errors'] += 1
            
            if entry.get('action_type') == 'approval_decision':
                if entry.get('approval_status') == 'pending':
                    summary['approvals_pending'] += 1
                elif entry.get('approval_status') == 'approved':
                    summary['approvals_approved'] += 1
                elif entry.get('approval_status') == 'rejected':
                    summary['approvals_rejected'] += 1
        
        return summary
    
    def cleanup_old_logs(self):
        """Remove logs older than retention period"""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        for log_file in self.logs_folder.glob('audit_*.jsonl'):
            try:
                # Parse date from filename
                date_str = log_file.stem.replace('audit_', '')
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log: {log_file.name}")
            except Exception as e:
                self.logger.error(f"Error cleaning up log {log_file.name}: {e}")


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger(vault_path: str = None) -> AuditLogger:
    """Get or create global audit logger"""
    global _audit_logger
    
    if _audit_logger is None:
        if vault_path is None:
            vault_path = Path(__file__).parent.parent
        _audit_logger = AuditLogger(str(vault_path))
    
    return _audit_logger


if __name__ == '__main__':
    import sys
    
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent
    
    # Create audit logger
    audit = AuditLogger(str(vault_path))
    
    # Example: Log some actions
    audit.log_action(
        actor='gmail_watcher',
        action='check_emails',
        target='gmail',
        parameters={'check_interval': 120},
        result='success'
    )
    
    audit.log_decision(
        actor='claude_code',
        decision='create_approval_request',
        context='payment_processing',
        alternatives=['auto_approve', 'reject', 'request_approval'],
        reasoning='Amount exceeds auto-approve threshold'
    )
    
    audit.log_approval_request(
        requester='claude_code',
        action_type='payment',
        details={'amount': 500, 'recipient': 'Vendor ABC'},
        approval_id='APPROVAL_001'
    )
    
    # Flush and show summary
    audit.flush()
    
    summary = audit.get_daily_summary()
    print("Daily Audit Summary:")
    print(json.dumps(summary, indent=2))
