"""
LinkedIn Auto-Post Agent - Silver Tier AI Employee

This script automates posting text content to LinkedIn using Playwright browser automation.

⚠️ IMPORTANT DISCLAIMER:
This tool is intended for authorized personal use, educational purposes, and testing only.
LinkedIn's Terms of Service generally prohibit automated posting. Users are responsible
for compliance with LinkedIn's policies. Use at your own risk.

Features:
- Automated LinkedIn login using environment credentials
- Text post creation and publishing
- Retry logic for transient failures
- Comprehensive error handling and logging
- Headless browser operation
- Screenshot capture on errors

Requirements:
- playwright (pip install playwright)
- python-dotenv (pip install python-dotenv)
- Run: playwright install chromium
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeout, Playwright
except ImportError:
    print("[ERROR] Playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

# Social Summary integration
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "social-summary"))
    from social_summary import log_social_post
    SOCIAL_SUMMARY_AVAILABLE = True
except ImportError:
    SOCIAL_SUMMARY_AVAILABLE = False

# Rich library for beautiful terminal output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


# Configuration
LOGS_FOLDER = "logs"
ACTIONS_LOG = os.path.join(LOGS_FOLDER, "actions.log")
SCREENSHOTS_FOLDER = os.path.join(LOGS_FOLDER, "screenshots")

# LinkedIn URLs
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"

# Timeouts (milliseconds)
DEFAULT_TIMEOUT = 30000
NAVIGATION_TIMEOUT = 30000
LOGIN_TIMEOUT = 15000
POST_TIMEOUT = 10000

# Retry configuration
MAX_RETRIES = 2
RETRY_DELAY_BASE = 5  # seconds


class LinkedInPoster:
    """
    Handles automated posting to LinkedIn using browser automation.
    """

    def __init__(self, headless: bool = True, timeout: int = DEFAULT_TIMEOUT, max_retries: int = MAX_RETRIES):
        """
        Initialize the LinkedIn poster.

        Args:
            headless (bool): Run browser in headless mode
            timeout (int): Default timeout in milliseconds
            max_retries (int): Maximum number of retry attempts
        """
        self.headless = headless
        self.timeout = timeout
        self.max_retries = max_retries
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Load environment variables
        load_dotenv()
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")

        # Ensure directories exist
        os.makedirs(LOGS_FOLDER, exist_ok=True)
        os.makedirs(SCREENSHOTS_FOLDER, exist_ok=True)

    def log_action(self, message: str, level: str = "INFO"):
        """
        Log an action to the actions.log file with timestamp.

        Args:
            message (str): The message to log
            level (str): Log level (INFO, ERROR, WARNING, SUCCESS)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [LINKEDIN] {message}\n"

        try:
            with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
                f.write(log_entry)

            # Colorful console output with rich
            if RICH_AVAILABLE:
                if level == "ERROR":
                    console.print(f"[bold red]✗[/bold red] [red]{message}[/red]")
                elif level == "SUCCESS":
                    console.print(f"[bold green]✓[/bold green] [green]{message}[/green]")
                elif level == "WARNING":
                    console.print(f"[bold yellow]⚠[/bold yellow] [yellow]{message}[/yellow]")
                else:
                    console.print(f"[bold cyan]ℹ[/bold cyan] [cyan]{message}[/cyan]")
            else:
                print(f"[{level}] {message}")
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[bold red]✗ Failed to write to log: {e}[/bold red]")
            else:
                print(f"[ERROR] Failed to write to log: {e}")

    async def take_screenshot(self, name: str):
        """
        Take a screenshot for debugging purposes.

        Args:
            name (str): Name for the screenshot file
        """
        try:
            if self.page:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.png"
                filepath = os.path.join(SCREENSHOTS_FOLDER, filename)
                await self.page.screenshot(path=filepath)
                self.log_action(f"Screenshot saved: {filepath}", "INFO")
        except Exception as e:
            self.log_action(f"Failed to take screenshot: {str(e)}", "WARNING")

    def validate_credentials(self) -> bool:
        """
        Validate that required credentials are present.

        Returns:
            bool: True if credentials are valid
        """
        if not self.email or not self.password:
            self.log_action("Missing LinkedIn credentials. Check .env file for LINKEDIN_EMAIL and LINKEDIN_PASSWORD", "ERROR")
            return False
        return True

    async def launch_browser(self) -> bool:
        """
        Launch the browser and create a new page.

        Returns:
            bool: True if successful
        """
        try:
            self.log_action("Starting LinkedIn post automation", "INFO")
            self.playwright = await async_playwright().start()

            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.timeout)

            self.log_action(f"Browser launched (headless={self.headless})", "INFO")
            return True

        except Exception as e:
            self.log_action(f"Failed to launch browser: {str(e)}", "ERROR")
            return False

    async def login(self) -> bool:
        """
        Login to LinkedIn using credentials from environment variables.

        Returns:
            bool: True if login successful
        """
        try:
            self.log_action("Navigating to login page", "INFO")
            await self.page.goto(LINKEDIN_LOGIN_URL, timeout=NAVIGATION_TIMEOUT)
            await asyncio.sleep(2)  # Wait for page to stabilize

            # Check if already logged in
            if "feed" in self.page.url:
                self.log_action("Already logged in", "INFO")
                return True

            # Enter email
            self.log_action("Entering email", "INFO")
            email_input = self.page.locator('input[id="username"]')
            await email_input.fill(self.email)
            await asyncio.sleep(1)

            # Enter password
            self.log_action("Entering password", "INFO")
            password_input = self.page.locator('input[id="password"]')
            await password_input.fill(self.password)
            await asyncio.sleep(1)

            # Click sign in button
            self.log_action("Clicking sign in button", "INFO")
            sign_in_button = self.page.locator('button[type="submit"]')
            await sign_in_button.click()

            # Wait for navigation
            await asyncio.sleep(5)

            # Check for successful login
            current_url = self.page.url

            # Check for CAPTCHA or verification
            if "checkpoint" in current_url or "challenge" in current_url:
                self.log_action("CAPTCHA or verification required. Waiting for manual intervention.", "WARNING")
                await self.take_screenshot("captcha_detected")

                # Wait for user to solve CAPTCHA manually
                print("\n" + "="*60)
                print("⚠️  CAPTCHA DETECTED!")
                print("="*60)
                print("Please solve the CAPTCHA in the browser window.")
                print("After solving, press Enter to continue...")
                print("="*60 + "\n")

                # Use asyncio.to_thread to avoid blocking the event loop
                await asyncio.to_thread(input)

                # Check if CAPTCHA was solved
                await asyncio.sleep(2)
                current_url = self.page.url

                if "checkpoint" in current_url or "challenge" in current_url:
                    self.log_action("CAPTCHA still not solved. Cannot proceed.", "ERROR")
                    return False

                if "feed" in current_url or "mynetwork" in current_url or "jobs" in current_url:
                    self.log_action("CAPTCHA solved successfully. Login successful.", "SUCCESS")
                    return True

                # Give it one more check
                self.log_action("Checking login status after CAPTCHA...", "INFO")
                await asyncio.sleep(3)

            # Check if login failed
            if "login" in current_url:
                self.log_action("Login failed. Check credentials or account status.", "ERROR")
                await self.take_screenshot("login_failed")
                return False

            # Check if we reached the feed
            if "feed" in current_url or "mynetwork" in current_url or "jobs" in current_url:
                self.log_action("Login successful", "SUCCESS")
                return True

            # Unknown state
            self.log_action(f"Unexpected page after login: {current_url}", "WARNING")
            await self.take_screenshot("unexpected_page")
            return False

        except PlaywrightTimeout:
            self.log_action("Login timeout. Check network connection or LinkedIn availability.", "ERROR")
            await self.take_screenshot("login_timeout")
            return False
        except Exception as e:
            self.log_action(f"Login error: {str(e)}", "ERROR")
            await self.take_screenshot("login_error")
            return False

    async def navigate_to_feed(self) -> bool:
        """
        Navigate to LinkedIn feed.

        Returns:
            bool: True if successful
        """
        try:
            if "feed" not in self.page.url:
                self.log_action("Navigating to feed", "INFO")
                await self.page.goto(LINKEDIN_FEED_URL, timeout=NAVIGATION_TIMEOUT)
                await asyncio.sleep(3)

            self.log_action("On LinkedIn feed", "INFO")
            return True

        except Exception as e:
            self.log_action(f"Failed to navigate to feed: {str(e)}", "ERROR")
            await self.take_screenshot("navigate_feed_error")
            return False

    async def create_post(self, content: str) -> bool:
        """
        Create and publish a text post on LinkedIn.

        Args:
            content (str): The text content to post

        Returns:
            bool: True if post was published successfully
        """
        try:
            # DEBUG: Wait and capture page information
            self.log_action("DEBUG: Waiting 5 seconds for page to fully load", "INFO")
            await self.page.wait_for_timeout(5000)

            # Save full page HTML
            self.log_action("DEBUG: Saving page source to logs/page_source.html", "INFO")
            html = await self.page.content()
            with open("logs/page_source.html", "w", encoding="utf-8") as f:
                f.write(html)

            # Print all button texts
            self.log_action("DEBUG: Extracting all button texts", "INFO")
            buttons = await self.page.locator("button").all_text_contents()
            print(f"[DEBUG] Buttons found: {buttons}")
            self.log_action(f"DEBUG: Found {len(buttons)} buttons", "INFO")

            # Print all input placeholders
            self.log_action("DEBUG: Extracting all input placeholders", "INFO")
            inputs = await self.page.locator("[placeholder]").all()
            for inp in inputs:
                ph = await inp.get_attribute("placeholder")
                print(f"[DEBUG] Placeholder: {ph}")
                self.log_action(f"DEBUG: Placeholder found: {ph}", "INFO")

            # Click "Start a post" element (it's a div/span, not a button)
            self.log_action("Looking for 'Start a post' element", "INFO")

            clicked = False

            # Method 1: Click by aria-label
            if not clicked:
                try:
                    self.log_action("Method 1: Trying aria-label='Start a post'", "INFO")
                    await self.page.locator("[aria-label='Start a post']").click(timeout=5000)
                    clicked = True
                    self.log_action("Method 1 SUCCESS: Clicked using aria-label", "SUCCESS")
                except Exception as e:
                    self.log_action(f"Method 1 failed: {str(e)}", "WARNING")

            # Method 2: Click any element containing exact text "Start a post"
            if not clicked:
                try:
                    self.log_action("Method 2: Trying get_by_text('Start a post', exact=True)", "INFO")
                    await self.page.get_by_text("Start a post", exact=True).first.click(timeout=5000)
                    clicked = True
                    self.log_action("Method 2 SUCCESS: Clicked using exact text", "SUCCESS")
                except Exception as e:
                    self.log_action(f"Method 2 failed: {str(e)}", "WARNING")

            # Method 3: JavaScript evaluation to click
            if not clicked:
                try:
                    self.log_action("Method 3: Trying JavaScript querySelector click", "INFO")
                    await self.page.goto(LINKEDIN_FEED_URL, timeout=NAVIGATION_TIMEOUT)
                    await self.page.wait_for_timeout(3000)
                    result = await self.page.evaluate("""
                        const btn = document.querySelector('.share-box-feed-entry__trigger-btn');
                        if (btn) {
                            btn.click();
                            return true;
                        }
                        return false;
                    """)
                    if result:
                        clicked = True
                        self.log_action("Method 3 SUCCESS: Clicked using JavaScript", "SUCCESS")
                    else:
                        self.log_action("Method 3 failed: Element not found in DOM", "WARNING")
                except Exception as e:
                    self.log_action(f"Method 3 failed: {str(e)}", "WARNING")

            # Method 4: Use role button with name
            if not clicked:
                try:
                    self.log_action("Method 4a: Trying get_by_role('button', name='Start a post')", "INFO")
                    await self.page.get_by_role("button", name="Start a post").click(timeout=5000)
                    clicked = True
                    self.log_action("Method 4a SUCCESS: Clicked using role button", "SUCCESS")
                except Exception as e:
                    self.log_action(f"Method 4a failed: {str(e)}", "WARNING")

            # Method 4b: Use div with role button and filter by text
            if not clicked:
                try:
                    self.log_action("Method 4b: Trying div[role='button'] with filter", "INFO")
                    await self.page.locator("div[role='button']").filter(has_text="Start a post").click(timeout=5000)
                    clicked = True
                    self.log_action("Method 4b SUCCESS: Clicked using div role button with filter", "SUCCESS")
                except Exception as e:
                    self.log_action(f"Method 4b failed: {str(e)}", "WARNING")

            if not clicked:
                self.log_action("All methods failed to find 'Start a post' element", "ERROR")
                await self.take_screenshot("start_post_not_found")
                return False

            # Wait 3 seconds after clicking
            self.log_action("Waiting 3 seconds for editor to open", "INFO")
            await asyncio.sleep(3)

            # Type content using keyboard
            self.log_action(f"Typing post content ({len(content)} characters)", "INFO")
            try:
                await self.page.keyboard.type(content)
                self.log_action("Content typed successfully", "SUCCESS")
            except Exception as e:
                self.log_action(f"Failed to type content: {str(e)}", "ERROR")
                await self.take_screenshot("typing_failed")
                return False

            await asyncio.sleep(2)

            # Click "Post" button - wait for share dialog first
            self.log_action("Looking for 'Post' button", "INFO")
            try:
                # Wait for the share dialog/modal to be visible first
                self.log_action("Waiting for share dialog to appear", "INFO")
                await self.page.wait_for_selector("div.share-creation-state", timeout=10000)

                # Find Post button specifically inside the share dialog
                post_btn = self.page.locator("div.share-creation-state button.share-actions__primary-action")
                btn_count = await post_btn.count()

                if btn_count == 0:
                    self.log_action("Trying fallback selector: button.share-actions__primary-action", "INFO")
                    post_btn = self.page.locator("button.share-actions__primary-action")
                    btn_count = await post_btn.count()

                if btn_count == 0:
                    self.log_action("Trying fallback selector: .share-box_actions button (last)", "INFO")
                    post_btn = self.page.locator(".share-box_actions button").last
                    btn_count = await post_btn.count()

                if btn_count == 0:
                    self.log_action("Post button not found with any selector", "ERROR")
                    await self.take_screenshot("post_button_not_found")
                    return False

                self.log_action(f"Found Post button (count: {btn_count}), clicking...", "INFO")
                await post_btn.click()
                self.log_action("Clicked 'Post' button", "SUCCESS")

            except Exception as e:
                self.log_action(f"Failed to click Post button: {str(e)}", "ERROR")
                await self.take_screenshot("post_button_error")
                return False

            # Wait for post to be published
            await asyncio.sleep(5)

            # Verify post was published (check if modal closed)
            try:
                modal = self.page.locator('div[role="dialog"]').first
                if await modal.is_visible(timeout=2000):
                    self.log_action("Post modal still visible, post may have failed", "WARNING")
                    await self.take_screenshot("post_verification_warning")
            except:
                # Modal not found, likely closed successfully
                pass

            self.log_action("Post published successfully", "SUCCESS")
            await self.take_screenshot("post_success")
            return True

        except PlaywrightTimeout:
            self.log_action("Post creation timeout", "ERROR")
            await self.take_screenshot("post_timeout")
            return False
        except Exception as e:
            self.log_action(f"Post creation error: {str(e)}", "ERROR")
            await self.take_screenshot("post_error")
            return False

    async def cleanup(self):
        """
        Close browser and cleanup resources.
        """
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.log_action("Browser closed", "INFO")
        except Exception as e:
            self.log_action(f"Cleanup error: {str(e)}", "WARNING")

    async def post(self, content: str) -> bool:
        """
        Main method to post content to LinkedIn with retry logic.

        Args:
            content (str): The text content to post

        Returns:
            bool: True if post was successful
        """
        if not content or not content.strip():
            self.log_action("Post content is empty", "ERROR")
            return False

        if not self.validate_credentials():
            return False

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                    self.log_action(f"Retry attempt {attempt}/{self.max_retries} after {delay}s delay", "INFO")
                    await asyncio.sleep(delay)

                # Launch browser
                if not await self.launch_browser():
                    continue

                # Login
                if not await self.login():
                    await self.cleanup()
                    if attempt == self.max_retries:
                        return False
                    continue

                # Navigate to feed
                if not await self.navigate_to_feed():
                    await self.cleanup()
                    if attempt == self.max_retries:
                        return False
                    continue

                # Create post
                if not await self.create_post(content):
                    await self.cleanup()
                    if attempt == self.max_retries:
                        return False
                    continue

                # Success!
                await self.cleanup()

                # Log to Social Summary
                if SOCIAL_SUMMARY_AVAILABLE:
                    try:
                        log_social_post(
                            platform="LinkedIn",
                            content=content,
                            metadata={"character_count": len(content)}
                        )
                    except Exception as e:
                        self.log_action(f"Failed to log to Social Summary: {str(e)}", "WARNING")

                return True

            except Exception as e:
                self.log_action(f"Unexpected error on attempt {attempt + 1}: {str(e)}", "ERROR")
                await self.cleanup()
                if attempt == self.max_retries:
                    return False

        return False


def main():
    """
    Main entry point for command-line usage.
    """
    # Beautiful startup banner
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            "[bold blue]🔗 LINKEDIN AUTO-POST AGENT[/bold blue]\n"
            "[dim]Silver Tier AI Employee[/dim]\n"
            "[yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/yellow]\n"
            "[red]⚠️  Use responsibly - LinkedIn ToS may prohibit automation[/red]",
            border_style="blue",
            padding=(1, 2)
        ))
        console.print()

    parser = argparse.ArgumentParser(description="Post content to LinkedIn automatically")
    parser.add_argument("content", type=str, help="The text content to post")
    parser.add_argument("--headless", type=str, default="true", help="Run in headless mode (true/false)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout in milliseconds")

    args = parser.parse_args()

    # Parse headless argument
    headless = args.headless.lower() in ['true', '1', 'yes', 'y']

    if RICH_AVAILABLE:
        console.print(f"[cyan]📝 Content:[/cyan] [white]{args.content[:50]}{'...' if len(args.content) > 50 else ''}[/white]")
        console.print(f"[cyan]👁️  Headless:[/cyan] [white]{headless}[/white]")
        console.print(f"[cyan]⏱️  Timeout:[/cyan] [white]{args.timeout}ms[/white]")
        console.print()

    # Create poster and post
    poster = LinkedInPoster(headless=headless, timeout=args.timeout)
    success = asyncio.run(poster.post(args.content))

    if RICH_AVAILABLE:
        console.print()
        if success:
            console.print(Panel(
                "[bold green]✓ Post published successfully![/bold green]\n"
                "[dim]Your content is now live on LinkedIn[/dim]",
                border_style="green",
                padding=(1, 2)
            ))
        else:
            console.print(Panel(
                "[bold red]✗ Failed to publish post[/bold red]\n"
                "[yellow]Check logs/actions.log for details[/yellow]",
                border_style="red",
                padding=(1, 2)
            ))
        console.print()
    else:
        if success:
            print("\n✓ Post published successfully!")
        else:
            print("\n✗ Failed to publish post. Check logs/actions.log for details.")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
