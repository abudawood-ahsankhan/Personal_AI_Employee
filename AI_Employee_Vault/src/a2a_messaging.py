"""
A2A (Agent-to-Agent) Messaging System - Platinum Tier
Part of Personal AI Employee Platinum Tier

Direct messaging between Cloud Agent and Local Executive.
Keeps vault as audit record.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
import time
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class A2AMessage:
    """Agent-to-Agent message"""
    
    def __init__(self, msg_type: str, sender: str, receiver: str, data: Dict):
        self.id = f"a2a_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.type = msg_type
        self.sender = sender  # 'cloud' or 'local'
        self.receiver = receiver  # 'cloud' or 'local'
        self.data = data
        self.timestamp = datetime.now().isoformat()
        self.status = 'pending'  # pending, delivered, read
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type,
            'sender': self.sender,
            'receiver': self.receiver,
            'data': self.data,
            'timestamp': self.timestamp,
            'status': self.status,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'A2AMessage':
        msg = cls(
            msg_type=data['type'],
            sender=data['sender'],
            receiver=data['receiver'],
            data=data['data']
        )
        msg.id = data['id']
        msg.timestamp = data['timestamp']
        msg.status = data.get('status', 'pending')
        return msg


class A2AMessenger:
    """
    Agent-to-Agent messaging system.
    
    Features:
    - Direct messaging between agents
    - Message persistence
    - Message delivery tracking
    - Callback support
    - Vault audit trail
    """
    
    def __init__(self, vault_path: str, agent_name: str):
        self.vault_path = Path(vault_path)
        self.agent_name = agent_name  # 'cloud' or 'local'
        
        # Message folders
        self.messages_folder = self.vault_path / 'Messages'
        self.inbox = self.messages_folder / agent_name / 'inbox'
        self.outbox = self.messages_folder / agent_name / 'outbox'
        self.sent = self.messages_folder / agent_name / 'sent'
        self.received = self.messages_folder / agent_name / 'received'
        
        # Create folders
        for folder in [self.inbox, self.outbox, self.sent, self.received]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Message handlers
        self.handlers: Dict[str, Callable] = {}
        
        # Message queue
        self.message_queue: List[A2AMessage] = []
        self.running = False
    
    def register_handler(self, msg_type: str, handler: Callable):
        """Register handler for message type"""
        self.handlers[msg_type] = handler
        self.logger.info(f"Registered handler: {msg_type}")
    
    def send_message(self, msg_type: str, receiver: str, data: Dict) -> A2AMessage:
        """Send message to other agent"""
        msg = A2AMessage(
            msg_type=msg_type,
            sender=self.agent_name,
            receiver=receiver,
            data=data
        )
        
        # Save to outbox
        msg_file = self.outbox / f"{msg.id}.json"
        with open(msg_file, 'w') as f:
            json.dump(msg.to_dict(), f, indent=2)
        
        # Also save to vault audit trail
        audit_file = self.vault_path / 'Logs' / 'A2A' / f"{msg.id}.json"
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_file, 'w') as f:
            json.dump(msg.to_dict(), f, indent=2)
        
        self.message_queue.append(msg)
        self.logger.info(f"Message sent: {msg_type} -> {receiver}")
        
        return msg
    
    def check_inbox(self) -> List[A2AMessage]:
        """Check for new messages"""
        messages = []
        
        for msg_file in self.inbox.glob('*.json'):
            try:
                with open(msg_file, 'r') as f:
                    msg_data = json.load(f)
                
                msg = A2AMessage.from_dict(msg_data)
                
                if msg.status == 'pending':
                    messages.append(msg)
                    
                    # Move to received
                    msg.status = 'delivered'
                    received_file = self.received / msg_file.name
                    with open(received_file, 'w') as f:
                        json.dump(msg.to_dict(), f, indent=2)
                    
                    msg_file.unlink()
                    
            except Exception as e:
                self.logger.error(f"Error reading message: {e}")
        
        return messages
    
    def process_messages(self):
        """Process all pending messages"""
        messages = self.check_inbox()
        
        for msg in messages:
            handler = self.handlers.get(msg.type)
            
            if handler:
                try:
                    response = handler(msg.data)
                    msg.status = 'read'
                    self.logger.info(f"Processed: {msg.type}")
                    
                    # Send response if provided
                    if response:
                        self.send_message(
                            msg_type=f"{msg.type}_response",
                            receiver=msg.sender,
                            data=response
                        )
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
            else:
                self.logger.warning(f"No handler for: {msg.type}")
    
    def start_listening(self, interval: int = 10):
        """Start listening for messages"""
        self.running = True
        self.logger.info(f"Started listening for messages ({interval}s interval)")
        
        while self.running:
            try:
                self.process_messages()
            except Exception as e:
                self.logger.error(f"Error in message loop: {e}")
            
            time.sleep(interval)
    
    def stop_listening(self):
        """Stop listening for messages"""
        self.running = False
        self.logger.info("Stopped listening for messages")


class CloudA2AMessenger(A2AMessenger):
    """Cloud-specific A2A messenger"""
    
    def __init__(self, vault_path: str):
        super().__init__(vault_path, 'cloud')
        
        # Register default handlers
        self.register_handler('approval_request', self._handle_approval_request)
        self.register_handler('draft_approved', self._handle_draft_approved)
        self.register_handler('action_executed', self._handle_action_executed)
    
    def _handle_approval_request(self, data: Dict) -> Dict:
        """Handle approval request from local"""
        self.logger.info(f"Approval request: {data}")
        return {'status': 'acknowledged'}
    
    def _handle_draft_approved(self, data: Dict) -> Dict:
        """Handle draft approved by local"""
        self.logger.info(f"Draft approved: {data}")
        return {'status': 'acknowledged'}
    
    def _handle_action_executed(self, data: Dict) -> Dict:
        """Handle action executed by local"""
        self.logger.info(f"Action executed: {data}")
        return {'status': 'acknowledged'}
    
    def request_approval(self, action_type: str, details: Dict) -> A2AMessage:
        """Request approval from local"""
        return self.send_message(
            msg_type='approval_request',
            receiver='local',
            data={
                'action_type': action_type,
                'details': details,
                'timestamp': datetime.now().isoformat(),
            }
        )
    
    def notify_draft_ready(self, draft_file: str, platform: str = None) -> A2AMessage:
        """Notify local that draft is ready"""
        return self.send_message(
            msg_type='draft_ready',
            receiver='local',
            data={
                'draft_file': draft_file,
                'platform': platform,
                'timestamp': datetime.now().isoformat(),
            }
        )


class LocalA2AMessenger(A2AMessenger):
    """Local-specific A2A messenger"""
    
    def __init__(self, vault_path: str):
        super().__init__(vault_path, 'local')
        
        # Register default handlers
        self.register_handler('approval_request', self._handle_approval_request)
        self.register_handler('draft_ready', self._handle_draft_ready)
    
    def _handle_approval_request(self, data: Dict) -> Dict:
        """Handle approval request from cloud"""
        self.logger.info(f"Approval request from cloud: {data}")
        # In production, would create approval file
        return {'status': 'pending_review'}
    
    def _handle_draft_ready(self, data: Dict) -> Dict:
        """Handle draft ready from cloud"""
        self.logger.info(f"Draft ready from cloud: {data}")
        # In production, would process draft
        return {'status': 'processing'}
    
    def approve_draft(self, draft_id: str) -> A2AMessage:
        """Approve cloud draft"""
        return self.send_message(
            msg_type='draft_approved',
            receiver='cloud',
            data={
                'draft_id': draft_id,
                'approved_by': 'local',
                'timestamp': datetime.now().isoformat(),
            }
        )
    
    def notify_action_executed(self, action_type: str, result: Dict) -> A2AMessage:
        """Notify cloud that action was executed"""
        return self.send_message(
            msg_type='action_executed',
            receiver='cloud',
            data={
                'action_type': action_type,
                'result': result,
                'timestamp': datetime.now().isoformat(),
            }
        )


if __name__ == '__main__':
    import sys
    
    vault_path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    agent = sys.argv[2] if len(sys.argv) > 2 else 'local'
    
    print("=" * 60)
    print("A2A Messenger - Platinum Tier")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print(f"Agent: {agent}")
    print()
    
    if agent == 'cloud':
        messenger = CloudA2AMessenger(vault_path)
    else:
        messenger = LocalA2AMessenger(vault_path)
    
    # Test message
    test_msg = messenger.send_message(
        msg_type='test',
        receiver='local' if agent == 'cloud' else 'cloud',
        data={'message': 'Hello from A2A!'}
    )
    
    print(f"Test message sent: {test_msg.id}")
    print(f"Type: {test_msg.type}")
    print(f"Receiver: {test_msg.receiver}")
