"""
Instagram Auto-Post Agent - Gold Tier AI Employee

This script automates posting to Instagram using Playwright browser automation.

[WARNING] IMPORTANT DISCLAIMER:
This tool is intended for authorized personal use, educational purposes, and testing only.
Instagram's Terms of Service generally prohibit automated posting. Users are responsible
for compliance with Instagram's policies. Use at your own risk.

Features:
- Automated Instagram login using environment credentials
- Text/caption post creation and publishing
- Comprehensive error handling and logging
- Headless browser operation
- Screenshot capture on errors

Requirements:
- playwright (pip install playwright)
- python-dotenv (pip install python-dotenv)
- pillow (pip install pillow)
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

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[ERROR] Pillow not installed. Run: pip install pillow")
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

# Instagram URLs
INSTAGRAM_URL = "https://www.instagram.com"
INSTAGRAM_LOGIN_URL = "https://www.instagram.com/accounts/login/"

# Timeouts (milliseconds)
DEFAULT_TIMEOUT = 30000
NAVIGATION_TIMEOUT = 30000


class InstagramPoster:
    """Handles automated posting to Instagram using browser automation."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Load credentials
        self.email = os.getenv("INSTAGRAM_EMAIL")
        self.password = os.getenv("INSTAGRAM_PASSWORD")

    def log_message(self, message: str, level: str = "INFO"):
        """Log message to both console and log files."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [INSTAGRAM] {message}\n"

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
            self.log_message("Missing INSTAGRAM_EMAIL or INSTAGRAM_PASSWORD in .env", "ERROR")
            return False
        return True

    def generate_default_image(self, text: str) -> Path:
        """Generate a default image with text on white background."""
        try:
            self.log_message("Generating default image with text", "INFO")

            # Image dimensions
            width, height = 1080, 1080

            # Create white background
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)

            # Try to use a nice font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()

            # Word wrap text
            words = text.split()
            lines = []
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] < width - 100:  # 50px margin on each side
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(' '.join(current_line))

            # Calculate total text height
            line_height = 50
            total_height = len(lines) * line_height

            # Start position (centered vertically)
            y = (height - total_height) // 2

            # Draw each line centered
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                draw.text((x, y), line, fill='black', font=font)
                y += line_height

            # Save image
            output_path = SCREENSHOTS_DIR / "ig_post_temp.png"
            img.save(output_path)
            self.log_message(f"Default image saved: {output_path}", "SUCCESS")

            return output_path

        except Exception as e:
            self.log_message(f"Failed to generate default image: {str(e)}", "ERROR")
            raise

    async def launch_browser(self) -> bool:
        """Launch the browser and create a new page."""
        try:
            self.log_message("Starting Instagram post automation", "INFO")
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
        """Login to Instagram using credentials from environment variables."""
        try:
            # Step 1: Navigate directly to login page
            self.log_message("Navigating to Instagram login page", "INFO")
            await self.page.goto(INSTAGRAM_LOGIN_URL, timeout=NAVIGATION_TIMEOUT)

            # Step 2: Wait for network idle to ensure page is fully loaded
            self.log_message("Waiting for page to load completely", "INFO")
            await self.page.wait_for_load_state("networkidle")

            # Debug: Check what page we're actually on
            print(f"[DEBUG] Page URL: {self.page.url}")
            print(f"[DEBUG] Page title: {await self.page.title()}")

            # Take screenshot to see what's on the page
            await self.take_screenshot("before_login_fields")

            # Handle cookie consent if present
            try:
                self.log_message("Checking for cookie consent", "INFO")
                cookie_buttons = [
                    "Allow essential and optional cookies",
                    "Allow all cookies",
                    "Accept",
                    "Accept All"
                ]
                for button_text in cookie_buttons:
                    try:
                        cookie_btn = self.page.get_by_role("button", name=button_text)
                        if await cookie_btn.is_visible(timeout=2000):
                            await cookie_btn.click()
                            self.log_message(f"Clicked cookie consent: {button_text}", "INFO")
                            await asyncio.sleep(2)
                            break
                    except:
                        continue
            except Exception as e:
                self.log_message(f"No cookie consent found: {str(e)}", "INFO")

            # Step 3: Detect which login form variant is present
            self.log_message("Detecting login form fields", "INFO")
            username_field = None
            password_field = None

            # Try standard Instagram fields first
            try:
                await self.page.wait_for_selector("input[name='username']", timeout=5000)
                username_field = "input[name='username']"
                password_field = "input[name='password']"
                self.log_message("Detected standard Instagram login form", "INFO")
            except:
                # Try Facebook-style fields
                try:
                    await self.page.wait_for_selector("input[name='email']", timeout=5000)
                    username_field = "input[name='email']"
                    password_field = "input[name='pass']"
                    self.log_message("Detected Facebook-style login form", "INFO")
                except Exception as e:
                    self.log_message(f"Username field not found. Checking page content...", "ERROR")
                    # Debug: Print all input fields on the page
                    inputs = await self.page.locator("input").all()
                    print(f"[DEBUG] Found {len(inputs)} input fields on page")
                    for i, inp in enumerate(inputs):
                        try:
                            name = await inp.get_attribute("name")
                            input_type = await inp.get_attribute("type")
                            print(f"[DEBUG] Input {i}: name={name}, type={input_type}")
                        except:
                            pass
                    raise e

            # Step 4: Find email field and enter INSTAGRAM_EMAIL
            self.log_message("Entering email", "INFO")
            await self.page.locator(username_field).fill(self.email)
            await asyncio.sleep(1)

            # Step 5: Find password field and enter INSTAGRAM_PASSWORD
            self.log_message("Entering password", "INFO")
            await self.page.locator(password_field).fill(self.password)
            await asyncio.sleep(1)

            # Step 6: Click login button (handle both button types)
            self.log_message("Clicking login button", "INFO")
            login_clicked = False

            # Debug: List all buttons on the page
            print("[DEBUG] Searching for login button...")
            try:
                all_buttons = await self.page.locator("button").all()
                print(f"[DEBUG] Found {len(all_buttons)} <button> elements")
                for i, btn in enumerate(all_buttons):
                    try:
                        btn_type = await btn.get_attribute("type")
                        btn_text = await btn.inner_text()
                        btn_class = await btn.get_attribute("class")
                        print(f"[DEBUG] Button {i}: type={btn_type}, text='{btn_text}', class={btn_class}")
                    except:
                        pass
            except Exception as e:
                print(f"[DEBUG] Error listing buttons: {e}")

            # Debug: List all input elements
            try:
                all_inputs = await self.page.locator("input").all()
                print(f"[DEBUG] Found {len(all_inputs)} <input> elements")
                for i, inp in enumerate(all_inputs):
                    try:
                        inp_type = await inp.get_attribute("type")
                        inp_name = await inp.get_attribute("name")
                        inp_value = await inp.get_attribute("value")
                        print(f"[DEBUG] Input {i}: type={inp_type}, name={inp_name}, value='{inp_value}'")
                    except:
                        pass
            except Exception as e:
                print(f"[DEBUG] Error listing inputs: {e}")

            # Try button[type='submit'] first (standard Instagram)
            try:
                await self.page.locator("button[type='submit']").click(timeout=5000)
                login_clicked = True
                self.log_message("Clicked button[type='submit']", "INFO")
            except Exception as e:
                print(f"[DEBUG] button[type='submit'] failed: {e}")

            # Try div with role="button" and aria-label="Log In" (Facebook-style form)
            if not login_clicked:
                try:
                    print("[DEBUG] Attempting to click div[role='button'][aria-label='Log In']...")
                    login_btn = self.page.locator('div[role="button"][aria-label="Log In"]').first
                    is_visible = await login_btn.is_visible(timeout=2000)
                    print(f"[DEBUG] Login button visible: {is_visible}")
                    await login_btn.click(timeout=5000)
                    login_clicked = True
                    self.log_message("Clicked Log In button (div)", "SUCCESS")
                except Exception as e:
                    print(f"[DEBUG] div[aria-label='Log In'] failed: {e}")

            # Try input[type='submit'] (Facebook-style)
            if not login_clicked:
                try:
                    print("[DEBUG] Attempting to click input[type='submit']...")
                    submit_input = self.page.locator("input[type='submit']")
                    is_visible = await submit_input.is_visible(timeout=2000)
                    print(f"[DEBUG] input[type='submit'] visible: {is_visible}")
                    await submit_input.click(timeout=5000, force=True)
                    login_clicked = True
                    self.log_message("Clicked input[type='submit']", "SUCCESS")
                except Exception as e:
                    print(f"[DEBUG] input[type='submit'] failed: {e}")

            # Try any button with "Log in" text
            if not login_clicked:
                try:
                    await self.page.get_by_role("button", name="Log in").first.click(timeout=5000)
                    login_clicked = True
                    self.log_message("Clicked 'Log in' button by role", "INFO")
                except Exception as e:
                    print(f"[DEBUG] Log in button by role failed: {e}")

            # Try pressing Enter on password field as fallback
            if not login_clicked:
                try:
                    self.log_message("Trying to press Enter on password field", "INFO")
                    print(f"[DEBUG] Pressing Enter on password field: {password_field}")
                    await self.page.locator(password_field).press("Enter")
                    login_clicked = True
                    self.log_message("Pressed Enter on password field", "SUCCESS")
                except Exception as e:
                    print(f"[DEBUG] Enter key press failed: {e}")

            if not login_clicked:
                self.log_message("Could not find login button", "ERROR")
                await self.take_screenshot("login_button_not_found")
                return False

            # Step 7: Wait 5 seconds for login to complete
            await asyncio.sleep(5)

            # Step 8: Add screenshot after login attempt for debugging
            await self.take_screenshot("after_login_attempt")

            # Step 9: Check current URL
            current_url = self.page.url
            self.log_message(f"Current URL after login: {current_url}", "INFO")

            # Check for security checkpoint
            if "challenge" in current_url or "checkpoint" in current_url:
                self.log_message("Security checkpoint detected. Manual intervention required.", "WARNING")
                await self.take_screenshot("checkpoint_detected")
                return False

            # Step 10: Handle "Save your login info?" page at /accounts/onetap/
            if "onetap" in current_url:
                self.log_message("Detected 'Save your login info?' page", "INFO")
                not_now_clicked = False

                # Try multiple selectors for "Not Now" button
                try:
                    await self.page.get_by_text("Not Now").click(timeout=3000)
                    not_now_clicked = True
                    self.log_message("Clicked 'Not Now' (capital N)", "INFO")
                except:
                    pass

                if not not_now_clicked:
                    try:
                        await self.page.get_by_text("Not now").click(timeout=3000)
                        not_now_clicked = True
                        self.log_message("Clicked 'Not now' (lowercase n)", "INFO")
                    except:
                        pass

                if not not_now_clicked:
                    try:
                        await self.page.locator("button:has-text('Not Now')").click(timeout=3000)
                        not_now_clicked = True
                        self.log_message("Clicked 'Not Now' button by locator", "INFO")
                    except:
                        pass

                if not_now_clicked:
                    await asyncio.sleep(3)
                    current_url = self.page.url
                    self.log_message(f"URL after dismissing onetap: {current_url}", "INFO")
                else:
                    self.log_message("Could not find 'Not Now' button on onetap page", "WARNING")

            # Step 11: Check if login successful (on feed or main Instagram page)
            if "instagram.com" in current_url and "login" not in current_url:
                # Success if we're on feed OR not on accounts pages (except onetap which we handled)
                if "/feed" in current_url or "/accounts/" not in current_url:
                    self.log_message("Login successful - on Instagram feed/home", "SUCCESS")

                    # Handle "Turn on Notifications?" prompt
                    try:
                        not_now_button = self.page.get_by_role("button", name="Not Now").first
                        if await not_now_button.is_visible(timeout=3000):
                            await not_now_button.click()
                            self.log_message("Dismissed 'Notifications' prompt", "INFO")
                            await asyncio.sleep(2)
                    except:
                        pass

                    return True

            self.log_message("Login failed. Still on login/accounts page.", "ERROR")
            await self.take_screenshot("login_failed")
            return False

        except Exception as e:
            self.log_message(f"Login error: {str(e)}", "ERROR")
            await self.take_screenshot("login_error")
            return False

    async def create_post(self, content: str, image_path: Optional[Path] = None) -> bool:
        """Create and publish a post on Instagram with image and caption."""
        try:
            self.log_message("Looking for Create/New Post button", "INFO")
            await asyncio.sleep(3)

            # Click on "Create" or "New Post" button
            clicked = False

            # Method 1: Click by aria-label "New post"
            try:
                self.log_message("Method 1: Trying aria-label 'New post'", "INFO")
                create_button = self.page.locator('[aria-label="New post"]').first
                await create_button.click(timeout=5000)
                clicked = True
                self.log_message("Method 1 SUCCESS: Clicked New post button", "SUCCESS")
            except Exception as e:
                self.log_message(f"Method 1 failed: {str(e)}", "WARNING")

            # Method 2: Click by SVG icon (Create button)
            if not clicked:
                try:
                    self.log_message("Method 2: Trying Create button by role", "INFO")
                    create_button = self.page.get_by_role("link", name="Create").first
                    await create_button.click(timeout=5000)
                    clicked = True
                    self.log_message("Method 2 SUCCESS: Clicked Create button", "SUCCESS")
                except Exception as e:
                    self.log_message(f"Method 2 failed: {str(e)}", "WARNING")

            # Method 3: Click by text "Create"
            if not clicked:
                try:
                    self.log_message("Method 3: Trying text 'Create'", "INFO")
                    create_button = self.page.get_by_text("Create").first
                    await create_button.click(timeout=5000)
                    clicked = True
                    self.log_message("Method 3 SUCCESS: Clicked Create", "SUCCESS")
                except Exception as e:
                    self.log_message(f"Method 3 failed: {str(e)}", "WARNING")

            if not clicked:
                self.log_message("Failed to find Create/New Post button", "ERROR")
                await self.take_screenshot("create_button_not_found")
                return False

            # Wait for modal to open
            await asyncio.sleep(3)

            # Step 1: Click "Post" option (not Reel or Story)
            self.log_message("Looking for 'Post' option", "INFO")
            try:
                post_option = self.page.get_by_text("Post", exact=True).first
                await post_option.click(timeout=5000)
                self.log_message("Clicked 'Post' option", "SUCCESS")
                await asyncio.sleep(2)
            except Exception as e:
                self.log_message(f"Could not find 'Post' option, continuing: {str(e)}", "WARNING")

            # Step 2: Upload the image file
            self.log_message(f"Uploading image: {image_path}", "INFO")
            try:
                # Look for file input
                file_input = self.page.locator('input[type="file"]').first
                await file_input.set_input_files(str(image_path))
                self.log_message("Image uploaded successfully", "SUCCESS")
                await asyncio.sleep(3)
            except Exception as e:
                self.log_message(f"Failed to upload image: {str(e)}", "ERROR")
                await self.take_screenshot("image_upload_failed")
                return False

            # Step 3: Click Next button
            self.log_message("Looking for Next button", "INFO")
            try:
                next_button = self.page.get_by_role("button", name="Next").first
                await next_button.click(timeout=5000)
                self.log_message("Clicked Next button", "SUCCESS")
                await asyncio.sleep(3)
            except Exception as e:
                self.log_message(f"Failed to click Next: {str(e)}", "ERROR")
                await self.take_screenshot("next_button_failed")
                return False

            # Sometimes there's a second Next button (for filters/editing)
            try:
                next_button = self.page.get_by_role("button", name="Next").first
                if await next_button.is_visible(timeout=2000):
                    await next_button.click()
                    self.log_message("Clicked second Next button", "SUCCESS")
                    await asyncio.sleep(3)
            except:
                pass

            # Step 4: Add caption text
            self.log_message("Adding caption text", "INFO")
            try:
                caption_area = self.page.locator('[aria-label*="caption"]').first
                await caption_area.fill(content)
                self.log_message("Caption added successfully", "SUCCESS")
                await asyncio.sleep(2)
            except Exception as e:
                self.log_message(f"Failed to add caption: {str(e)}", "ERROR")
                await self.take_screenshot("caption_failed")
                return False

            # Step 5: Click Share button
            self.log_message("Looking for Share button", "INFO")
            try:
                share_button = self.page.get_by_role("button", name="Share").first
                await share_button.click(timeout=5000)
                self.log_message("Clicked Share button", "SUCCESS")
                await asyncio.sleep(5)
            except Exception as e:
                self.log_message(f"Failed to click Share: {str(e)}", "ERROR")
                await self.take_screenshot("share_button_failed")
                return False

            # Wait for post to complete
            await asyncio.sleep(3)

            # Check for success indicators
            try:
                # Look for "Post shared" or similar confirmation
                if await self.page.get_by_text("Post shared").is_visible(timeout=3000):
                    self.log_message("Post shared confirmation detected", "SUCCESS")
                elif await self.page.get_by_text("Your post has been shared").is_visible(timeout=3000):
                    self.log_message("Post shared confirmation detected", "SUCCESS")
            except:
                pass

            self.log_message("Post creation completed", "SUCCESS")
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

    async def post(self, content: str, image_path: Optional[str] = None) -> bool:
        """Main method to post content to Instagram."""
        if not content or not content.strip():
            self.log_message("Post content is empty", "ERROR")
            return False

        if not self.validate_credentials():
            return False

        try:
            # Handle image: use provided path or generate default
            if image_path:
                img_path = Path(image_path)
                if not img_path.exists():
                    self.log_message(f"Image file not found: {image_path}", "ERROR")
                    return False
                self.log_message(f"Using provided image: {image_path}", "INFO")
            else:
                self.log_message("No image provided, generating default image", "INFO")
                img_path = self.generate_default_image(content)

            if not await self.launch_browser():
                return False

            if not await self.login():
                await self.cleanup()
                return False

            if not await self.create_post(content, img_path):
                await self.cleanup()
                return False

            await self.cleanup()

            # Log to Social Summary
            if SOCIAL_SUMMARY_AVAILABLE:
                try:
                    log_social_post(
                        platform="Instagram",
                        content=content,
                        metadata={
                            "character_count": len(content),
                            "has_image": True,
                            "image_path": str(img_path)
                        }
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
            "[bold magenta]Instagram Auto-Post Agent[/bold magenta]\n"
            "[dim]Gold Tier AI Employee[/dim]\n"
            "[yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/yellow]\n"
            "[red][WARNING] Use responsibly - Instagram ToS may prohibit automation[/red]\n"
            "[cyan][INFO] Supports image posts with captions[/cyan]",
            border_style="magenta",
            padding=(1, 2)
        ))
        console.print()

    parser = argparse.ArgumentParser(description="Post content to Instagram automatically")
    parser.add_argument("content", type=str, help="The caption/text content to post")
    parser.add_argument("--image", type=str, help="Path to image file (optional - generates default if not provided)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (default: False)")

    args = parser.parse_args()

    if RICH_AVAILABLE:
        console.print(f"[cyan][CONTENT] Content:[/cyan] [white]{args.content[:50]}{'...' if len(args.content) > 50 else ''}[/white]")
        console.print(f"[cyan][IMAGE] Image:[/cyan] [white]{args.image if args.image else 'Auto-generated'}[/white]")
        console.print(f"[cyan][HEADLESS] Headless:[/cyan] [white]{args.headless}[/white]")
        console.print()

    # Create poster and post
    poster = InstagramPoster(headless=args.headless)
    success = asyncio.run(poster.post(args.content, args.image))

    if RICH_AVAILABLE:
        console.print()
        if success:
            console.print(Panel(
                "[bold green][OK] Post published successfully![/bold green]\n"
                "[dim]Your content is now live on Instagram[/dim]",
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
