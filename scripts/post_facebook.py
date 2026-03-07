"""
Facebook Auto-Post Agent - Gold Tier AI Employee

This script automates posting to Facebook using Playwright browser automation.

[WARNING] IMPORTANT DISCLAIMER:
This tool is intended for authorized personal use, educational purposes, and testing only.
Facebook's Terms of Service generally prohibit automated posting. Users are responsible
for compliance with Facebook's policies. Use at your own risk.

Features:
- Automated Facebook login using environment credentials
- Text post creation and publishing
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
from typing import Optional

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
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Load environment variables
load_dotenv()

# Configuration
LOGS_DIR = Path("logs")
SOCIAL_LOG = LOGS_DIR / "social.log"
ACTIONS_LOG = LOGS_DIR / "actions.log"
SCREENSHOTS_DIR = LOGS_DIR / "screenshots"

# Ensure directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Facebook URLs
FACEBOOK_URL = "https://www.facebook.com"

# Timeouts (milliseconds)
DEFAULT_TIMEOUT = 30000
NAVIGATION_TIMEOUT = 30000


class FacebookPoster:
    """Handles automated posting to Facebook using browser automation."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Load credentials
        self.email = os.getenv("FACEBOOK_EMAIL")
        self.password = os.getenv("FACEBOOK_PASSWORD")

    def log_message(self, message: str, level: str = "INFO"):
        """Log message to both console and log files."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [FACEBOOK] {message}\n"

        # Log to social.log
        with open(SOCIAL_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        # Log to actions.log
        with open(ACTIONS_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        # Console output
        if RICH_AVAILABLE:
            if level == "ERROR":
                console.print(f"[red][X][/red] {message}")
            elif level == "SUCCESS":
                console.print(f"[green][OK][/green] {message}")
            elif level == "WARNING":
                console.print(f"[yellow][WARNING][/yellow] {message}")
            else:
                console.print(f"[cyan][INFO][/cyan] {message}")
        else:
            print(f"[{level}] {message}")

    async def take_screenshot(self, name: str):
        """Take a screenshot for debugging."""
        try:
            if self.page:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.png"
                filepath = SCREENSHOTS_DIR / filename
                await self.page.screenshot(path=str(filepath))
                self.log_message(f"Screenshot saved: {filepath}", "INFO")
        except Exception as e:
            self.log_message(f"Failed to take screenshot: {str(e)}", "WARNING")

    def validate_credentials(self) -> bool:
        """Validate that required credentials are present."""
        if not self.email or not self.password:
            self.log_message("Missing FACEBOOK_EMAIL or FACEBOOK_PASSWORD in .env", "ERROR")
            return False
        return True

    async def launch_browser(self) -> bool:
        """Launch the browser and create a new page."""
        try:
            self.log_message("Starting Facebook post automation", "INFO")
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
            self.page.set_default_timeout(DEFAULT_TIMEOUT)

            self.log_message(f"Browser launched (headless={self.headless})", "INFO")
            return True

        except Exception as e:
            self.log_message(f"Failed to launch browser: {str(e)}", "ERROR")
            return False

    async def login(self) -> bool:
        """Login to Facebook using credentials from environment variables."""
        try:
            self.log_message("Navigating to Facebook", "INFO")
            await self.page.goto(FACEBOOK_URL, timeout=NAVIGATION_TIMEOUT)
            await asyncio.sleep(3)

            # Check if already logged in
            if "login" not in self.page.url:
                self.log_message("Already logged in", "INFO")
                return True

            # Enter email
            self.log_message("Entering email", "INFO")
            email_input = self.page.locator('input[name="email"]')
            await email_input.fill(self.email)
            await asyncio.sleep(1)

            # Enter password
            self.log_message("Entering password", "INFO")
            password_input = self.page.locator('input[name="pass"]')
            await password_input.fill(self.password)
            await asyncio.sleep(1)

            # Click login button
            self.log_message("Clicking login button", "INFO")
            login_button = self.page.locator('button[name="login"]')
            await login_button.click()

            # Wait for navigation
            await asyncio.sleep(5)

            # Check for successful login
            current_url = self.page.url

            if "checkpoint" in current_url or "challenge" in current_url:
                self.log_message("Security checkpoint detected. Manual intervention required.", "WARNING")
                await self.take_screenshot("checkpoint_detected")
                return False

            if "login" in current_url:
                self.log_message("Login failed. Check credentials.", "ERROR")
                await self.take_screenshot("login_failed")
                return False

            self.log_message("Login successful", "SUCCESS")
            return True

        except Exception as e:
            self.log_message(f"Login error: {str(e)}", "ERROR")
            await self.take_screenshot("login_error")
            return False

    async def create_post(self, content: str) -> bool:
        """Create and publish a text post on Facebook."""
        try:
            self.log_message("Looking for post creation area", "INFO")
            await asyncio.sleep(3)

            # Click on "What's on your mind?" area
            clicked = False

            # Method 1: Click by placeholder text
            try:
                self.log_message("Method 1: Trying placeholder click", "INFO")
                post_box = self.page.locator('[placeholder*="What\'s on your mind"]').first
                await post_box.click(timeout=5000)
                clicked = True
                self.log_message("Method 1 SUCCESS: Clicked post box", "SUCCESS")
            except Exception as e:
                self.log_message(f"Method 1 failed: {str(e)}", "WARNING")

            # Method 2: Click by aria-label
            if not clicked:
                try:
                    self.log_message("Method 2: Trying aria-label click", "INFO")
                    post_box = self.page.locator('[aria-label*="Create a post"]').first
                    await post_box.click(timeout=5000)
                    clicked = True
                    self.log_message("Method 2 SUCCESS: Clicked post box", "SUCCESS")
                except Exception as e:
                    self.log_message(f"Method 2 failed: {str(e)}", "WARNING")

            # Method 3: Click by role
            if not clicked:
                try:
                    self.log_message("Method 3: Trying role='textbox' click", "INFO")
                    post_box = self.page.locator('[role="textbox"]').first
                    await post_box.click(timeout=5000)
                    clicked = True
                    self.log_message("Method 3 SUCCESS: Clicked post box", "SUCCESS")
                except Exception as e:
                    self.log_message(f"Method 3 failed: {str(e)}", "WARNING")

            if not clicked:
                self.log_message("Failed to find post creation area", "ERROR")
                await self.take_screenshot("post_box_not_found")
                return False

            # Wait for modal/editor to open
            await asyncio.sleep(3)

            # Type content
            self.log_message(f"Typing post content ({len(content)} characters)", "INFO")
            await self.page.keyboard.type(content)
            await asyncio.sleep(2)

            # Click Post button
            self.log_message("Looking for Post button", "INFO")
            try:
                # Try multiple selectors for the Post button
                post_button = None

                # Method 1: By text "Post"
                try:
                    post_button = self.page.get_by_role("button", name="Post").first
                    await post_button.click(timeout=5000)
                    self.log_message("Clicked Post button", "SUCCESS")
                except:
                    pass

                if not post_button:
                    # Method 2: By aria-label
                    try:
                        post_button = self.page.locator('[aria-label="Post"]').first
                        await post_button.click(timeout=5000)
                        self.log_message("Clicked Post button", "SUCCESS")
                    except:
                        pass

                if not post_button:
                    self.log_message("Post button not found", "ERROR")
                    await self.take_screenshot("post_button_not_found")
                    return False

            except Exception as e:
                self.log_message(f"Failed to click Post button: {str(e)}", "ERROR")
                await self.take_screenshot("post_button_error")
                return False

            # Wait for post to be published
            await asyncio.sleep(5)

            self.log_message("Post published successfully", "SUCCESS")
            await self.take_screenshot("post_success")
            return True

        except Exception as e:
            self.log_message(f"Post creation error: {str(e)}", "ERROR")
            await self.take_screenshot("post_error")
            return False

    async def cleanup(self):
        """Close browser and cleanup resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.log_message("Browser closed", "INFO")
        except Exception as e:
            self.log_message(f"Cleanup error: {str(e)}", "WARNING")

    async def post(self, content: str) -> bool:
        """Main method to post content to Facebook."""
        if not content or not content.strip():
            self.log_message("Post content is empty", "ERROR")
            return False

        if not self.validate_credentials():
            return False

        try:
            if not await self.launch_browser():
                return False

            if not await self.login():
                await self.cleanup()
                return False

            if not await self.create_post(content):
                await self.cleanup()
                return False

            await self.cleanup()

            # Log to Social Summary
            if SOCIAL_SUMMARY_AVAILABLE:
                try:
                    log_social_post(
                        platform="Facebook",
                        content=content,
                        metadata={"character_count": len(content)}
                    )
                except Exception as e:
                    self.log_message(f"Failed to log to Social Summary: {str(e)}", "WARNING")

            return True

        except Exception as e:
            self.log_message(f"Unexpected error: {str(e)}", "ERROR")
            await self.cleanup()
            return False


def main():
    """Main entry point."""
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            "[bold blue]Facebook Auto-Post Agent[/bold blue]\n"
            "[dim]Gold Tier AI Employee[/dim]\n"
            "[yellow]========================================[/yellow]\n"
            "[red][WARNING] Use responsibly - Facebook ToS may prohibit automation[/red]",
            border_style="blue",
            padding=(1, 2)
        ))
        console.print()

    parser = argparse.ArgumentParser(description="Post content to Facebook automatically")
    parser.add_argument("content", type=str, help="The text content to post")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (default: False)")

    args = parser.parse_args()

    if RICH_AVAILABLE:
        console.print(f"[cyan][CONTENT] Content:[/cyan] [white]{args.content[:50]}{'...' if len(args.content) > 50 else ''}[/white]")
        console.print(f"[cyan][HEADLESS] Headless:[/cyan] [white]{args.headless}[/white]")
        console.print()

    # Create poster and post
    poster = FacebookPoster(headless=args.headless)
    success = asyncio.run(poster.post(args.content))

    if RICH_AVAILABLE:
        console.print()
        if success:
            console.print(Panel(
                "[bold green][OK] Post published successfully![/bold green]\n"
                "[dim]Your content is now live on Facebook[/dim]",
                border_style="green",
                padding=(1, 2)
            ))
        else:
            console.print(Panel(
                "[bold red][X] Failed to publish post[/bold red]\n"
                "[yellow]Check logs/social.log for details[/yellow]",
                border_style="red",
                padding=(1, 2)
            ))
        console.print()
    else:
        if success:
            print("\n[OK] Post published successfully!")
        else:
            print("\n[X] Failed to publish post. Check logs/social.log for details.")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
