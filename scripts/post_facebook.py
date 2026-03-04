"""
Facebook Auto-Post Agent - Gold Tier AI Employee

This script automates posting to Facebook Pages using the Meta Graph API.

Features:
- Post text and link content to Facebook Pages
- Meta Graph API integration
- Comprehensive error handling and logging
- Rate limit management

Requirements:
- requests (pip install requests)
- python-dotenv (pip install python-dotenv)
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
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

# Graph API base URL
GRAPH_API_URL = "https://graph.facebook.com/v18.0"


def log_message(message: str, level: str = "INFO"):
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
            console.print(f"[red]✗[/red] {message}")
        elif level == "SUCCESS":
            console.print(f"[green]✓[/green] {message}")
        elif level == "WARNING":
            console.print(f"[yellow]⚠[/yellow] {message}")
        else:
            console.print(f"[cyan]ℹ[/cyan] {message}")
    else:
        print(f"[{level}] {message}")


def post_facebook(content: str, link: Optional[str] = None) -> Dict:
    """
    Post content to Facebook Page.

    Args:
        content (str): Post content/message
        link (str, optional): URL to share

    Returns:
        dict: Result with post_id, url, status
    """
    try:
        # Validate credentials
        if not ACCESS_TOKEN or not PAGE_ID:
            log_message("Missing FACEBOOK_ACCESS_TOKEN or FACEBOOK_PAGE_ID in .env", "ERROR")
            return {
                "status": "error",
                "message": "Missing Facebook API credentials. Check .env file."
            }

        log_message(f"Posting to Facebook: {content[:50]}...")

        # Prepare post data
        data = {
            "message": content,
            "access_token": ACCESS_TOKEN
        }

        if link:
            data["link"] = link
            log_message(f"Including link: {link}")

        # Post to Facebook
        response = requests.post(
            f"{GRAPH_API_URL}/{PAGE_ID}/feed",
            data=data,
            timeout=30
        )

        result = response.json()

        if "error" in result:
            error_msg = result["error"].get("message", "Unknown error")
            log_message(f"Facebook API error: {error_msg}", "ERROR")
            return {
                "status": "error",
                "message": f"Facebook API error: {error_msg}"
            }

        post_id = result.get("id")
        post_url = f"https://facebook.com/{post_id}"

        log_message(f"Facebook post successful: {post_id}", "SUCCESS")

        # Log to social summary
        if SOCIAL_SUMMARY_AVAILABLE:
            try:
                log_social_post(
                    platform="Facebook",
                    content=content,
                    post_url=post_url,
                    metadata={"likes": 0, "comments": 0, "shares": 0}
                )
            except Exception as e:
                log_message(f"Failed to log to social summary: {e}", "WARNING")

        return {
            "status": "success",
            "post_id": post_id,
            "url": post_url,
            "message": "✓ Posted to Facebook successfully"
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
    parser = argparse.ArgumentParser(description="Post to Facebook Page")
    parser.add_argument("content", help="Post content/message")
    parser.add_argument("--link", help="Optional URL to share", default=None)

    args = parser.parse_args()

    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold blue]Facebook Auto-Post Agent[/bold blue]\n"
            "[dim]Gold Tier AI Employee[/dim]",
            border_style="blue"
        ))
    else:
        print("=" * 60)
        print("FACEBOOK AUTO-POST AGENT")
        print("Gold Tier AI Employee")
        print("=" * 60)

    result = post_facebook(args.content, link=args.link)

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
