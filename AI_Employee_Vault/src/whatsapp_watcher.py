"""
WhatsApp Watcher - Monitors WhatsApp Web for new messages
Part of Personal AI Employee Silver Tier

⚠️ IMPORTANT: This uses WhatsApp Web automation. Be aware of WhatsApp's Terms of Service.
For production use, consider the official WhatsApp Business API.

Setup Instructions:
1. Install playwright: pip install playwright
2. Install browsers: playwright install chromium
3. First run will open browser for QR code scanning
4. Session will be saved for future runs

Usage:
    python whatsapp_watcher.py
"""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from base_watcher import BaseWatcher


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for new messages containing priority keywords.
    Uses Playwright for browser automation.
    """
    
    def __init__(
        self, 
        vault_path: str, 
        session_path: str = None,
        check_interval: int = 60,
        headless: bool = True
    ):
        super().__init__(vault_path, check_interval)
        
        # Session path for browser profile
        if session_path is None:
            session_path = Path(__file__).parent / 'whatsapp_session'
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.headless = headless
        
        # Keywords that indicate important messages
        self.priority_keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'important',
            'deadline', 'meeting', 'help', 'call', 'money',
            'bank', 'transfer', 'client', 'customer', 'order'
        ]
        
        # Track last message timestamp per chat
        self.last_message_times: Dict[str, str] = {}
    
    def _init_browser(self) -> BrowserContext:
        """Initialize browser with persistent context"""
        playwright = sync_playwright().start()
        
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.session_path),
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        return browser
    
    def _wait_for_whatsapp_load(self, page: Page, timeout: int = 60000) -> bool:
        """Wait for WhatsApp Web to load"""
        try:
            # Wait for chat list or QR code
            page.wait_for_selector('[data-testid="chat-list"], #initial', timeout=timeout)
            return True
        except Exception as e:
            self.logger.warning(f"WhatsApp load timeout: {e}")
            return False
    
    def _is_authenticated(self, page: Page) -> bool:
        """Check if WhatsApp is authenticated (QR code scanned)"""
        try:
            # Look for chat list (authenticated) vs QR code (not authenticated)
            chat_list = page.query_selector('[data-testid="chat-list"]')
            return chat_list is not None
        except:
            return False
    
    def _get_unread_chats(self, page: Page) -> List[dict]:
        """Get list of chats with unread messages"""
        chats = []
        
        try:
            # Find all chat elements
            chat_elements = page.query_selector_all('[role="row"]')
            
            for chat in chat_elements:
                try:
                    # Get chat name
                    name_elem = chat.query_selector('span[title]')
                    if not name_elem:
                        continue
                    
                    chat_name = name_elem.get_attribute('title')
                    
                    # Get last message
                    msg_elem = chat.query_selector('span[data-testid="last-message-content"]')
                    last_message = msg_elem.inner_text() if msg_elem else ""
                    
                    # Check for unread indicator
                    unread_badge = chat.query_selector('[aria-label*="unread"]')
                    is_unread = unread_badge is not None
                    
                    # Check for priority keywords
                    message_lower = last_message.lower()
                    has_priority = any(kw in message_lower for kw in self.priority_keywords)
                    
                    if is_unread or has_priority:
                        chats.append({
                            'name': chat_name,
                            'last_message': last_message,
                            'is_unread': is_unread,
                            'has_priority': has_priority
                        })
                    
                except Exception as e:
                    self.logger.debug(f"Error processing chat: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error getting unread chats: {e}")
        
        return chats
    
    def check_for_updates(self) -> list:
        """Check WhatsApp for new messages"""
        new_messages = []
        
        try:
            with self._init_browser() as browser:
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to WhatsApp Web
                page.goto('https://web.whatsapp.com', wait_until='networkidle')
                
                # Wait for load
                if not self._wait_for_whatsapp_load(page):
                    self.logger.error("WhatsApp Web failed to load")
                    return []
                
                # Check authentication
                if not self._is_authenticated(page):
                    self.logger.warning("WhatsApp not authenticated. Please scan QR code.")
                    # Wait for authentication (user scans QR)
                    self.logger.info("Waiting for QR code scan (60 seconds)...")
                    for _ in range(12):  # Wait up to 60 seconds
                        time.sleep(5)
                        if self._is_authenticated(page):
                            self.logger.info("WhatsApp authenticated!")
                            break
                    else:
                        self.logger.error("Authentication timeout")
                        return []
                
                # Additional wait for messages to load
                time.sleep(3)
                
                # Get unread chats
                chats = self._get_unread_chats(page)
                
                for chat in chats:
                    # Create unique ID
                    chat_id = f"{chat['name']}_{datetime.now().strftime('%Y%m%d')}"
                    
                    # Skip if already processed today
                    if chat_id in self.processed_ids:
                        continue
                    
                    new_messages.append(chat)
                    self.processed_ids.add(chat_id)
                
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
        
        return new_messages
    
    def create_action_file(self, chat) -> Path:
        """Create a Markdown action file for the WhatsApp message"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chat_name_safe = chat['name'].replace(' ', '_').replace('/', '_')[:30]
        
        filename = f'WHATSAPP_{chat_name_safe}_{timestamp}.md'
        
        priority = 'high' if chat['has_priority'] else 'normal'
        
        content = f'''---
type: whatsapp
chat_name: {chat['name']}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

# WhatsApp Message

**From:** {chat['name']}  
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Priority:** {priority.upper()}

---

## Message Content

{chat['last_message']}

---

# Suggested Actions

- [ ] Read and understand the message
- [ ] Determine if response is needed
- [ ] Draft a response if required
- [ ] Take any requested action
- [ ] Mark as done and move to /Done folder

# Response Draft

_Draft your response here_

# Notes

_Add any context or follow-up notes_
'''
        
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        
        return filepath
    
    def run_headed(self):
        """Run with visible browser (useful for initial QR scan)"""
        self.headless = False
        self.run()


if __name__ == '__main__':
    import sys
    
    # Get vault path from argument or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent
    
    print("=" * 60)
    print("WhatsApp Watcher - Personal AI Employee")
    print("=" * 60)
    print(f"\nVault: {vault_path}")
    print(f"Session: {Path(__file__).parent / 'whatsapp_session'}")
    print("\n⚠️  First run instructions:")
    print("1. The browser will open")
    print("2. Scan the QR code with your WhatsApp phone")
    print("3. Session will be saved for future runs")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # First run should be headed (visible) for QR scan
        watcher = WhatsAppWatcher(
            vault_path=str(vault_path),
            check_interval=60,  # Check every minute
            headless=True  # Set to False for first run to scan QR
        )
        watcher.run()
    except KeyboardInterrupt:
        print("\n\nWhatsApp Watcher stopped")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
