#!/usr/bin/env python3
"""
Social Meta Skill - Test and Validation

Tests Facebook and Instagram API credentials.
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from social_meta import post_facebook, log_activity
    from dotenv import load_dotenv
    import requests
except ImportError as e:
    print(f"[ERROR] Missing dependencies: {e}")
    print("Run: pip install requests python-dotenv pillow")
    sys.exit(1)

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_status(message, status="info"):
    """Print colored status."""
    if status == "success":
        print(f"{GREEN}[+]{RESET} {message}")
    elif status == "error":
        print(f"{RED}[!]{RESET} {message}")
    elif status == "warning":
        print(f"{YELLOW}[*]{RESET} {message}")
    else:
        print(f"{BLUE}[i]{RESET} {message}")


def check_credentials():
    """Check Meta API credentials."""
    load_dotenv()

    required = {
        "META_ACCESS_TOKEN": "Meta Access Token",
        "FACEBOOK_PAGE_ID": "Facebook Page ID",
        "INSTAGRAM_ACCOUNT_ID": "Instagram Account ID"
    }

    missing = []
    for var, name in required.items():
        if not os.getenv(var):
            missing.append(name)
            print_status(f"{name}: NOT configured", "error")
        else:
            print_status(f"{name}: Configured", "success")

    if missing:
        return False

    return True


def test_facebook_connection():
    """Test Facebook API connection."""
    load_dotenv()

    access_token = os.getenv("META_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")

    if not access_token or not page_id:
        print_status("Missing Facebook credentials", "error")
        return False

    try:
        print_status("Testing Facebook API connection...", "info")

        # Get page info
        response = requests.get(
            f"https://graph.facebook.com/v18.0/{page_id}",
            params={
                "fields": "name,id",
                "access_token": access_token
            },
            timeout=10
        )

        result = response.json()

        if "error" in result:
            print_status(f"Facebook API error: {result['error']['message']}", "error")
            return False

        print_status(f"Connected to page: {result.get('name', 'Unknown')}", "success")
        return True

    except Exception as e:
        print_status(f"Connection test failed: {str(e)}", "error")
        return False


def test_instagram_connection():
    """Test Instagram API connection."""
    load_dotenv()

    access_token = os.getenv("META_ACCESS_TOKEN")
    instagram_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    if not access_token or not instagram_id:
        print_status("Missing Instagram credentials", "error")
        return False

    try:
        print_status("Testing Instagram API connection...", "info")

        # Get account info
        response = requests.get(
            f"https://graph.facebook.com/v18.0/{instagram_id}",
            params={
                "fields": "username,id",
                "access_token": access_token
            },
            timeout=10
        )

        result = response.json()

        if "error" in result:
            print_status(f"Instagram API error: {result['error']['message']}", "error")
            return False

        print_status(f"Connected to account: @{result.get('username', 'Unknown')}", "success")
        return True

    except Exception as e:
        print_status(f"Connection test failed: {str(e)}", "error")
        return False


def test_facebook_post():
    """Post a test message to Facebook."""
    test_content = "Test post from Gold Tier AI Employee - Social Meta skill validation"

    print_status("Posting test to Facebook...", "info")

    result = post_facebook(test_content)

    if result["status"] == "success":
        print_status(f"Test post successful!", "success")
        print_status(f"URL: {result['url']}", "info")
        return True
    else:
        print_status(f"Test post failed: {result['message']}", "error")
        return False


def main():
    """Run validation."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Social Meta Skill - Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    # Check credentials
    print(f"{BLUE}[Credentials Check]{RESET}")
    if not check_credentials():
        print_status("\nValidation failed. Configure Meta credentials in .env", "error")
        return 1

    # Test Facebook connection
    print(f"\n{BLUE}[Facebook Connection]{RESET}")
    fb_ok = test_facebook_connection()

    # Test Instagram connection
    print(f"\n{BLUE}[Instagram Connection]{RESET}")
    ig_ok = test_instagram_connection()

    # Ask to post test
    if fb_ok:
        print(f"\n{BLUE}[Test Post]{RESET}")
        print_status("Ready to post a test message to Facebook", "info")
        response = input(f"{YELLOW}Post test message? (y/n):{RESET} ").lower()

        if response == 'y':
            if test_facebook_post():
                print(f"\n{GREEN}✓ Validation successful!{RESET}\n")
                return 0
            else:
                print(f"\n{RED}✗ Test post failed{RESET}\n")
                return 1
        else:
            print_status("Test skipped", "warning")

    if fb_ok or ig_ok:
        print(f"\n{GREEN}✓ Connection validation successful!{RESET}\n")
        return 0
    else:
        print(f"\n{RED}✗ Validation failed{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
