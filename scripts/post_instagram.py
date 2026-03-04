"""
Instagram Auto-Post Agent - Gold Tier AI Employee

This script automates posting to Instagram Business accounts using the Meta Graph API.

Features:
- Post images with captions to Instagram Business accounts
- Meta Graph API integration
- Two-step posting process (container creation + publishing)
- Comprehensive error handling and logging
- Rate limit management

Requirements:
- requests (pip install requests)
- python-dotenv (pip install python-dotenv)
- pillow (pip install pillow) - for image validation

Note: Instagram requires:
- Instagram Business or Creator account
- Account linked to a Facebook Page
- Images must be publicly accessible URLs or uploaded to a CDN first
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

try:
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[WARNING] Pillow not installed. Image validation disabled. Run: pip install pillow")

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
    from rich import print as rprint
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

# Ensure directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Meta API credentials
ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN") or os.getenv("META_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")

# Graph API base URL
GRAPH_API_URL = "https://graph.facebook.com/v18.0"


def log_message(message: str, level: str = "INFO"):
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
            console.print(f"[red]✗[/red] {message}")
        elif level == "SUCCESS":
            console.print(f"[green]✓[/green] {message}")
        elif level == "WARNING":
            console.print(f"[yellow]⚠[/yellow] {message}")
        else:
            console.print(f"[cyan]ℹ[/cyan] {message}")
    else:
        print(f"[{level}] {message}")


def validate_image(image_path: str) -> bool:
    """
    Validate image file.

    Args:
        image_path (str): Path to image file

    Returns:
        bool: True if valid
    """
    if not PIL_AVAILABLE:
        log_message("Pillow not available, skipping image validation", "WARNING")
        return True

    try:
        img = Image.open(image_path)
        width, height = img.size

        # Instagram requirements
        if width < 320 or height < 320:
            log_message(f"Image too small: {width}x{height}. Min 320x320", "ERROR")
            return False

        # Check file size (8MB limit)
        file_size = Path(image_path).stat().st_size
        if file_size > 8 * 1024 * 1024:
            log_message(f"Image too large: {file_size / 1024 / 1024:.1f}MB. Max 8MB", "ERROR")
            return False

        log_message(f"Image validated: {width}x{height}, {file_size / 1024:.1f}KB")
        return True

    except Exception as e:
        log_message(f"Image validation error: {e}", "ERROR")
        return False


def post_instagram(caption: str, image_url: str) -> Dict:
    """
    Post image to Instagram Business account.

    Args:
        caption (str): Post caption (max 2200 chars)
        image_url (str): Publicly accessible image URL

    Returns:
        dict: Result with post_id, url, status
    """
    try:
        # Validate credentials
        if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
            log_message("Missing FACEBOOK_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID in .env", "ERROR")
            return {
                "status": "error",
                "message": "Missing Instagram API credentials. Check .env file."
            }

        # Validate caption length
        if len(caption) > 2200:
            log_message(f"Caption too long ({len(caption)} chars). Max 2200", "ERROR")
            return {
                "status": "error",
                "message": f"Caption too long ({len(caption)} chars). Max 2200 characters."
            }

        log_message(f"Posting to Instagram: {caption[:50]}...")
        log_message(f"Image URL: {image_url}")

        # Step 1: Create media container
        log_message("Step 1: Creating media container...")
        container_data = {
            "image_url": image_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }

        container_response = requests.post(
            f"{GRAPH_API_URL}/{INSTAGRAM_ACCOUNT_ID}/media",
            data=container_data,
            timeout=30
        )

        container_result = container_response.json()

        if "error" in container_result:
            error_msg = container_result["error"].get("message", "Unknown error")
            log_message(f"Container creation failed: {error_msg}", "ERROR")
            return {
                "status": "error",
                "message": f"Instagram API error: {error_msg}"
            }

        container_id = container_result.get("id")
        log_message(f"Container created: {container_id}")

        # Step 2: Publish the container
        log_message("Step 2: Publishing container...")
        publish_data = {
            "creation_id": container_id,
            "access_token": ACCESS_TOKEN
        }

        publish_response = requests.post(
            f"{GRAPH_API_URL}/{INSTAGRAM_ACCOUNT_ID}/media_publish",
            data=publish_data,
            timeout=30
        )

        publish_result = publish_response.json()

        if "error" in publish_result:
            error_msg = publish_result["error"].get("message", "Unknown error")
            log_message(f"Publishing failed: {error_msg}", "ERROR")
            return {
                "status": "error",
                "message": f"Instagram API error: {error_msg}"
            }

        post_id = publish_result.get("id")
        post_url = f"https://instagram.com/p/{post_id}"

        log_message(f"Instagram post successful: {post_id}", "SUCCESS")

        # Log to social summary
        if SOCIAL_SUMMARY_AVAILABLE:
            try:
                log_social_post(
                    platform="Instagram",
                    content=caption,
                    post_url=post_url,
                    metadata={"likes": 0, "comments": 0}
                )
            except Exception as e:
                log_message(f"Failed to log to social summary: {e}", "WARNING")

        return {
            "status": "success",
            "post_id": post_id,
            "url": post_url,
            "message": "✓ Posted to Instagram successfully"
        }

    except requests.exceptions.RequestException as e:
        log_message(f"Network error: {str(e)}", "ERROR")
        return {
            "status": "error",
            "message": f"Network error: {str(e)}"
        }

    except Exception as e:
        log_message(f"Unexpected error: {str(e)}", "ERROR")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Post to Instagram Business account")
    parser.add_argument("caption", help="Post caption")
    parser.add_argument("image_url", help="Publicly accessible image URL")
    parser.add_argument("--validate-local", help="Validate local image file before posting", default=None)

    args = parser.parse_args()

    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold magenta]Instagram Auto-Post Agent[/bold magenta]\n"
            "[dim]Gold Tier AI Employee[/dim]",
            border_style="magenta"
        ))
    else:
        print("=" * 60)
        print("INSTAGRAM AUTO-POST AGENT")
        print("Gold Tier AI Employee")
        print("=" * 60)

    # Validate local image if provided
    if args.validate_local:
        if not Path(args.validate_local).exists():
            log_message(f"Local image not found: {args.validate_local}", "ERROR")
            sys.exit(1)

        if not validate_image(args.validate_local):
            log_message("Image validation failed", "ERROR")
            sys.exit(1)

    result = post_instagram(args.caption, args.image_url)

    if RICH_AVAILABLE:
        if result["status"] == "success":
            console.print(Panel(
                f"[green]{result['message']}[/green]\n\n"
                f"[dim]URL:[/dim] {result.get('url', 'N/A')}",
                title="✓ Success",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[red]{result['message']}[/red]",
                title="✗ Error",
                border_style="red"
            ))
    else:
        print(json.dumps(result, indent=2))

    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
