#!/usr/bin/env python3
"""
Twitter Skill - Test and Validation

Tests Twitter API credentials and posts a test tweet.
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from twitter_post import post_tweet, load_history
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[ERROR] Missing dependencies: {e}")
    print("Run: pip install tweepy python-dotenv")
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
    """Check Twitter API credentials."""
    load_dotenv()

    required = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET",
        "TWITTER_BEARER_TOKEN"
    ]

    missing = [var for var in required if not os.getenv(var)]

    if missing:
        print_status(f"Missing credentials: {', '.join(missing)}", "error")
        return False

    print_status("All Twitter credentials configured", "success")
    return True


def test_post():
    """Post a test tweet."""
    test_content = f"Test tweet from Gold Tier AI Employee - {Path(__file__).parent.name} skill validation"

    print_status("Posting test tweet...", "info")

    result = post_tweet(test_content)

    if result["status"] == "success":
        print_status(f"Test tweet posted successfully!", "success")
        print_status(f"URL: {result['url']}", "info")
        return True
    else:
        print_status(f"Test tweet failed: {result['message']}", "error")
        return False


def show_history():
    """Show recent tweet history."""
    history = load_history()
    tweets = history.get("tweets", [])

    if not tweets:
        print_status("No tweet history found", "warning")
        return

    print_status(f"Recent tweets ({len(tweets)} total):", "info")
    for tweet in tweets[-5:]:
        status_icon = "✓" if tweet.get("status") == "success" else "✗"
        print(f"  {status_icon} {tweet.get('timestamp', 'N/A')}: {tweet.get('content', 'N/A')[:50]}...")


def main():
    """Run validation."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Twitter Skill - Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    # Check credentials
    print(f"{BLUE}[Credentials Check]{RESET}")
    if not check_credentials():
        print_status("\nValidation failed. Configure Twitter credentials in .env", "error")
        return 1

    # Show history
    print(f"\n{BLUE}[Tweet History]{RESET}")
    show_history()

    # Ask to post test tweet
    print(f"\n{BLUE}[Test Tweet]{RESET}")
    print_status("Ready to post a test tweet", "info")
    response = input(f"{YELLOW}Post test tweet? (y/n):{RESET} ").lower()

    if response == 'y':
        if test_post():
            print(f"\n{GREEN}✓ Validation successful!{RESET}\n")
            return 0
        else:
            print(f"\n{RED}✗ Validation failed{RESET}\n")
            return 1
    else:
        print_status("Test skipped", "warning")
        return 0


if __name__ == "__main__":
    sys.exit(main())
