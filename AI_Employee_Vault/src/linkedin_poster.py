"""
LinkedIn Auto Poster - Browser-based posting without API
Part of Personal AI Employee Silver Tier

This script uses Playwright to automate LinkedIn posting via browser.
No API credentials needed - just login once and session is saved.

⚠️ IMPORTANT: Use responsibly. LinkedIn may detect automation.
Consider using official API for production use.

Setup Instructions:
1. pip install playwright
2. playwright install chromium
3. First run: python linkedin_poster.py --login
4. Login to LinkedIn in the browser
5. Subsequent runs will use saved session

Usage:
    python linkedin_poster.py --post "Your post content here"
    python linkedin_poster.py --login  # To authenticate first
"""

import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Optional

from playwright.sync_api import sync_playwright, Page, BrowserContext


class LinkedInPoster:
    """Post to LinkedIn using browser automation"""
    
    def __init__(self, session_path: str = None):
        if session_path is None:
            session_path = Path(__file__).parent / 'linkedin_session'
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.linkedin_url = 'https://www.linkedin.com/feed/'
    
    def _init_browser(self) -> BrowserContext:
        """Initialize browser with persistent context"""
        from playwright.sync_api import sync_playwright
        
        playwright = sync_playwright().start()
        
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.session_path),
            headless=False,  # Always visible for LinkedIn
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        return browser
    
    def login(self):
        """Open browser for manual LinkedIn login"""
        print("Opening LinkedIn login page...")
        print("Please log in to your LinkedIn account.")
        print("The session will be saved for future use.")
        
        with self._init_browser() as browser:
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto(self.linkedin_url)
            
            print("\nOnce logged in, close the browser window.")
            print("Your session will be saved automatically.")
            
            # Keep browser open until user closes
            try:
                while browser.is_connected():
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        
        print("\n✓ Login session saved!")
    
    def post(self, text: str, wait_for_approval: bool = True) -> bool:
        """
        Create a post on LinkedIn
        
        Args:
            text: The post content
            wait_for_approval: If True, wait for human approval before posting
        
        Returns:
            True if post was successful, False otherwise
        """
        if not text or len(text.strip()) == 0:
            print("❌ Error: Post text cannot be empty")
            return False
        
        if len(text) > 3000:
            print("❌ Error: Post exceeds 3000 character limit")
            return False
        
        try:
            with self._init_browser() as browser:
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                print("Navigating to LinkedIn...")
                page.goto(self.linkedin_url, wait_until='networkidle')
                
                # Wait for page to load
                time.sleep(3)
                
                # Check if logged in
                if not self._is_logged_in(page):
                    print("❌ Not logged in. Please run: python linkedin_poster.py --login")
                    return False
                
                # Start creating post
                print("Opening post creator...")
                self._open_post_creator(page)
                
                # Enter text
                print("Entering post content...")
                self._enter_post_text(page, text)
                
                # Wait for approval if needed
                if wait_for_approval:
                    print("\n⏳ Waiting for human approval...")
                    print("Type 'yes' to post, or close browser to cancel:")
                    approval = input("> ").strip().lower()
                    if approval != 'yes':
                        print("❌ Post cancelled by user")
                        browser.close()
                        return False
                
                # Submit post
                print("Posting...")
                success = self._submit_post(page)
                
                if success:
                    print("✅ Post published successfully!")
                    self._log_post(text)
                else:
                    print("❌ Failed to publish post")
                
                return success
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def _is_logged_in(self, page: Page) -> bool:
        """Check if user is logged in to LinkedIn"""
        try:
            # Look for the "Start a post" button
            start_post = page.query_selector('[aria-label="Start a post"]')
            return start_post is not None
        except:
            return False
    
    def _open_post_creator(self, page: Page):
        """Open the post creation dialog"""
        # Click the "Start a post" button
        start_post = page.query_selector('[aria-label="Start a post"]')
        if start_post:
            start_post.click()
            time.sleep(2)
        else:
            # Alternative: try to find post input
            post_input = page.query_selector('[role="textbox"][placeholder*="post"]')
            if post_input:
                post_input.click()
                time.sleep(2)
    
    def _enter_post_text(self, page: Page, text: str):
        """Enter text into the post editor"""
        # Find the post editor textbox
        textbox = page.query_selector('[role="textbox"]')
        if textbox:
            # Clear any existing text
            textbox.click()
            time.sleep(1)
            
            # Use keyboard to type (more reliable)
            from playwright.sync_api import Keyboard
            textbox.fill(text)
            time.sleep(1)
    
    def _submit_post(self, page: Page) -> bool:
        """Click the Post button"""
        try:
            # Find the Post button
            post_button = page.query_selector('button:has-text("Post")')
            if post_button:
                post_button.click()
                time.sleep(3)
                
                # Wait for confirmation or error
                time.sleep(2)
                return True
            else:
                print("Could not find Post button")
                return False
        except Exception as e:
            print(f"Error submitting post: {e}")
            return False
    
    def _log_post(self, text: str):
        """Log the post to a file"""
        log_file = Path(__file__).parent.parent / 'Logs' / 'linkedin_posts.md'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f'''
## {timestamp}

{text}

---
'''
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)


def create_business_post(vault_path: str) -> str:
    """
    Create a business update post from vault data
    
    Reads from Dashboard.md and Business_Goals.md to generate post content
    """
    vault = Path(vault_path)
    
    # Try to read dashboard
    dashboard_file = vault / 'Dashboard.md'
    if dashboard_file.exists():
        content = dashboard_file.read_text()
        # Extract key metrics (simple parsing)
        lines = content.split('\n')
        metrics = []
        for line in lines:
            if '$' in line or 'revenue' in line.lower():
                metrics.append(line.strip())
        
        if metrics:
            post = "📊 Business Update\n\n"
            post += "\n".join(metrics[:3])  # Top 3 metrics
            post += "\n\n#BusinessUpdate #Entrepreneurship"
            return post
    
    # Default post if no dashboard data
    return "📈 Growing my business with AI automation! #AI #Automation #Business"


if __name__ == '__main__':
    import sys
    
    poster = LinkedInPoster()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--login':
            poster.login()
        
        elif sys.argv[1] == '--post':
            if len(sys.argv) > 2:
                text = ' '.join(sys.argv[2:])
                poster.post(text)
            else:
                print("❌ Error: Please provide post text")
                print("Usage: python linkedin_poster.py --post \"Your message here\"")
        
        elif sys.argv[1] == '--business':
            vault_path = sys.argv[2] if len(sys.argv) > 2 else str(Path(__file__).parent.parent)
            post_text = create_business_post(vault_path)
            print("Generated post:")
            print("-" * 60)
            print(post_text)
            print("-" * 60)
            poster.post(post_text)
        
        else:
            print("Usage:")
            print("  python linkedin_poster.py --login")
            print("  python linkedin_poster.py --post \"Your message\"")
            print("  python linkedin_poster.py --business [vault_path]")
    else:
        print("LinkedIn Auto Poster - Personal AI Employee")
        print("=" * 60)
        print("\nUsage:")
        print("  --login          Login to LinkedIn (save session)")
        print("  --post \"text\"    Create a post with given text")
        print("  --business       Create post from business dashboard")
        print("\nExample:")
        print('  python linkedin_poster.py --post "Hello LinkedIn!"')
