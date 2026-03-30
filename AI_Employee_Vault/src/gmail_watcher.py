"""
Gmail Watcher - Monitors Gmail for new important/unread emails
Part of Personal AI Employee Silver Tier

Setup Instructions:
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials.json to AI_Employee_Vault/src/credentials.json
6. Run this script once to authenticate

Usage:
    python gmail_watcher.py
"""

import os
import base64
from pathlib import Path
from datetime import datetime
from email import message_from_bytes

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from base_watcher import BaseWatcher

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail_readonly']

class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new unread/important messages and creates action files.
    """
    
    def __init__(self, vault_path: str, credentials_path: str = None, check_interval: int = 120):
        super().__init__(vault_path, check_interval)
        
        # Default credentials path
        if credentials_path is None:
            credentials_path = Path(__file__).parent / 'credentials.json'
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(__file__).parent / 'token.json'
        
        # Initialize Gmail service
        self.service = self._authenticate()
        
        # Keywords that indicate high priority
        self.priority_keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'important',
            'deadline', 'meeting', 'contract', 'agreement'
        ]
    
    def _authenticate(self):
        """Authenticate with Gmail API and return service object"""
        creds = None
        
        # Load saved credentials
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_path, SCOPES
                )
            except Exception as e:
                self.logger.warning(f"Error loading token: {e}")
                self.token_path.unlink()
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please download credentials.json from Google Cloud Console"
                    )
                
                self.logger.info("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=8080)
                
                # Save credentials
                with open(self.token_path, 'w') as f:
                    f.write(creds.to_json())
                self.logger.info("Credentials saved successfully")
        
        # Build and return service
        return build('gmail', 'v1', credentials=creds)
    
    def check_for_updates(self) -> list:
        """Check Gmail for new unread messages"""
        try:
            # Search for unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=20
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = [
                m for m in messages 
                if m['id'] not in self.processed_ids
            ]
            
            return new_messages
            
        except HttpError as error:
            self.logger.error(f'Gmail API error: {error}')
            return []
        except Exception as error:
            self.logger.error(f'Error checking Gmail: {error}')
            return []
    
    def _get_email_details(self, message_id: str) -> dict:
        """Fetch full email details"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message.get('payload', {}).get('headers', [])
            email_data = {
                'id': message_id,
                'internalDate': message.get('internalDate'),
            }
            
            for header in headers:
                name = header.get('name', '').lower()
                value = header.get('value', '')
                if name == 'from':
                    email_data['from'] = value
                elif name == 'to':
                    email_data['to'] = value
                elif name == 'subject':
                    email_data['subject'] = value
                elif name == 'date':
                    email_data['date'] = value
            
            # Extract body
            body_data = ''
            payload = message.get('payload', {})
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        body_data = part['body'].get('data', '')
                        break
            
            if not body_data and 'body' in payload:
                body_data = payload['body'].get('data', '')
            
            # Decode body
            if body_data:
                body_data = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            
            email_data['body'] = body_data
            email_data['snippet'] = message.get('snippet', '')
            
            return email_data
            
        except Exception as e:
            self.logger.error(f'Error getting email details: {e}')
            return None
    
    def _calculate_priority(self, email_data: dict) -> str:
        """Calculate email priority based on content"""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        from_email = email_data.get('from', '').lower()
        
        # Check for priority keywords
        for keyword in self.priority_keywords:
            if keyword in subject or keyword in body:
                return 'high'
        
        # Check if from known important contacts (add your important contacts)
        important_contacts = ['boss@', 'client@', 'bank@']
        for contact in important_contacts:
            if contact in from_email:
                return 'high'
        
        return 'normal'
    
    def create_action_file(self, message) -> Path:
        """Create a Markdown action file for the email"""
        # Get full email details
        email_data = self._get_email_details(message['id'])
        
        if not email_data:
            raise Exception("Could not fetch email details")
        
        # Calculate priority
        priority = self._calculate_priority(email_data)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        subject_safe = (email_data.get('subject', 'No Subject')[:30]
                       .replace(' ', '_')
                       .replace('/', '_'))
        filename = f'EMAIL_{subject_safe}_{timestamp}.md'
        
        # Create content
        content = f'''---
type: email
message_id: {email_data['id']}
from: {email_data.get('from', 'Unknown')}
to: {email_data.get('to', 'Unknown')}
subject: {email_data.get('subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

# Email Content

**From:** {email_data.get('from', 'Unknown')}  
**To:** {email_data.get('to', 'Unknown')}  
**Subject:** {email_data.get('subject', 'No Subject')}  
**Date:** {email_data.get('date', 'Unknown')}

---

{email_data.get('body', email_data.get('snippet', 'No content available'))}

---

# Suggested Actions

- [ ] Read and understand the email
- [ ] Draft a response if needed
- [ ] Take any required action
- [ ] Mark as done and move to /Done folder

# Notes

_Add any notes or context here_
'''
        
        # Write file
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        
        # Mark as processed
        self.processed_ids.add(message['id'])
        
        return filepath


if __name__ == '__main__':
    import sys
    
    # Get vault path from argument or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent
    
    print(f"Starting Gmail Watcher...")
    print(f"Vault: {vault_path}")
    print(f"Press Ctrl+C to stop\n")
    
    try:
        watcher = GmailWatcher(
            vault_path=str(vault_path),
            check_interval=120  # Check every 2 minutes
        )
        watcher.run()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nSetup instructions:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Gmail API")
        print("3. Create OAuth 2.0 credentials (Desktop app)")
        print("4. Download credentials.json to AI_Employee_Vault/src/")
        print("5. Run this script again")
    except KeyboardInterrupt:
        print("\n\nGmail Watcher stopped")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
