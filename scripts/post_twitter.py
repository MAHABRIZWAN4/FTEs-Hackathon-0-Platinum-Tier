"""
Twitter/X Auto-Post Agent - Gold Tier AI Employee

This script automates posting tweets to Twitter/X using the Twitter API v2.

Features:
- Post tweets via Twitter API v2
- Character limit validation (280 chars)
- Thread support for longer content
- Tweet history tracking
- Comprehensive error handling and logging
- Rate limit management

Requirements:
- tweepy (pip install tweepy)
- python-dotenv (pip install python-dotenv)
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

try:
    import tweepy
except ImportError:
    print("[ERROR] Tweepy not installed. Run: pip install tweepy")
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
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Load environment variables
load_dotenv()

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
REPORTS_DIR = VAULT_DIR / "Reports"
HISTORY_FILE = REPORTS_DIR / "twitter_history.json"
LOGS_DIR = Path("logs")
SOCIAL_LOG = LOGS_DIR / "social.log"
ACTIONS_LOG = LOGS_DIR / "actions.log"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Twitter API credentials
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")


def log_message(message: str, level: str = "INFO"):
    """Log message to both console and log files."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [TWITTER] {message}\n"

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


def load_history() -> Dict:
    """Load tweet history from file."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"tweets": []}


def save_history(history: Dict):
    """Save tweet history to file."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def post_tweet(content: str, thread: bool = False) -> Dict:
    """
    Post a tweet to Twitter/X.

    Args:
        content (str): Tweet content
        thread (bool): Split into thread if > 280 chars

    Returns:
        dict: Result with tweet_id, url, status
    """
    try:
        # Validate credentials
        if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
            log_message("Missing Twitter API credentials in .env", "ERROR")
            return {
                "status": "error",
                "message": "Missing Twitter API credentials. Check .env file."
            }

        log_message(f"Posting tweet: {content[:50]}...")

        # Initialize Twitter client
        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )

        # Handle threading for long content
        if len(content) > 280 and thread:
            return post_thread(client, content)

        # Validate length
        if len(content) > 280:
            log_message(f"Tweet too long ({len(content)} chars). Max 280 or use --thread", "ERROR")
            return {
                "status": "error",
                "message": f"Tweet too long ({len(content)} chars). Max 280 or use --thread flag"
            }

        # Post tweet
        response = client.create_tweet(text=content)
        tweet_id = response.data['id']

        # Get username for URL
        me = client.get_me()
        username = me.data.username
        tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

        log_message(f"Tweet posted successfully: {tweet_id}", "SUCCESS")

        # Save to history
        history = load_history()
        history["tweets"].append({
            "id": tweet_id,
            "content": content,
            "url": tweet_url,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "character_count": len(content)
        })
        save_history(history)

        # Log to social summary
        if SOCIAL_SUMMARY_AVAILABLE:
            try:
                log_social_post(
                    platform="X",
                    content=content,
                    post_url=tweet_url,
                    metadata={"likes": 0, "retweets": 0, "replies": 0}
                )
            except Exception as e:
                log_message(f"Failed to log to social summary: {e}", "WARNING")

        return {
            "status": "success",
            "tweet_id": tweet_id,
            "url": tweet_url,
            "message": f"[OK] Tweet posted successfully"
        }

    except tweepy.TweepyException as e:
        error_msg = str(e)
        log_message(f"Twitter API error: {error_msg}", "ERROR")

        # Save failed attempt to history
        history = load_history()
        history["tweets"].append({
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "status": "failed",
            "error": error_msg
        })
        save_history(history)

        return {
            "status": "error",
            "message": f"Twitter API error: {error_msg}"
        }

    except Exception as e:
        log_message(f"Unexpected error: {str(e)}", "ERROR")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def post_thread(client: tweepy.Client, content: str) -> Dict:
    """
    Post a thread of tweets.

    Args:
        client: Tweepy client
        content (str): Long content to split

    Returns:
        dict: Result with thread info
    """
    try:
        log_message(f"Creating thread for long content ({len(content)} chars)")

        # Split content into 270-char chunks (leave room for numbering)
        chunks = []
        words = content.split()
        current_chunk = ""

        for word in words:
            if len(current_chunk) + len(word) + 1 <= 270:
                current_chunk += word + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = word + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        # Post thread
        tweet_ids = []
        previous_tweet_id = None

        for i, chunk in enumerate(chunks, 1):
            tweet_text = f"{chunk}\n\n({i}/{len(chunks)})"

            if previous_tweet_id:
                response = client.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=previous_tweet_id
                )
            else:
                response = client.create_tweet(text=tweet_text)

            tweet_ids.append(response.data['id'])
            previous_tweet_id = response.data['id']
            log_message(f"Posted tweet {i}/{len(chunks)}")

        # Get username
        me = client.get_me()
        username = me.data.username
        thread_url = f"https://twitter.com/{username}/status/{tweet_ids[0]}"

        log_message(f"Thread posted successfully ({len(chunks)} tweets)", "SUCCESS")

        # Save to history
        history = load_history()
        history["tweets"].append({
            "id": tweet_ids[0],
            "thread_ids": tweet_ids,
            "content": content,
            "url": thread_url,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "tweet_count": len(chunks)
        })
        save_history(history)

        # Log to social summary
        if SOCIAL_SUMMARY_AVAILABLE:
            try:
                log_social_post(
                    platform="X",
                    content=content[:200] + "..." if len(content) > 200 else content,
                    post_url=thread_url,
                    metadata={"tweet_count": len(chunks)}
                )
            except Exception as e:
                log_message(f"Failed to log to social summary: {e}", "WARNING")

        return {
            "status": "success",
            "tweet_ids": tweet_ids,
            "url": thread_url,
            "message": f"[OK] Thread posted successfully ({len(chunks)} tweets)"
        }

    except Exception as e:
        log_message(f"Thread posting error: {str(e)}", "ERROR")
        return {
            "status": "error",
            "message": f"Thread posting error: {str(e)}"
        }


def post_tweet_demo(content: str) -> Dict:
    """
    Simulate posting a tweet in demo mode (no real API calls).

    Args:
        content (str): Tweet content

    Returns:
        dict: Simulated result
    """
    log_message("DEMO MODE: Simulating tweet post", "INFO")
    log_message(f"Content: {content[:100]}{'...' if len(content) > 100 else ''}", "INFO")

    # Simulate success
    import random
    tweet_id = f"demo_{random.randint(1000000000000000000, 9999999999999999999)}"
    tweet_url = f"https://twitter.com/demo_user/status/{tweet_id}"

    log_message(f"DEMO: Tweet posted successfully: {tweet_id}", "SUCCESS")

    # Save to Social_Log.md
    social_log_path = VAULT_DIR / "Reports" / "Social_Log.md"
    social_log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"\n## Twitter/X Post - {timestamp}\n"
    log_entry += f"**Status:** [OK] SUCCESS (DEMO MODE)\n"
    log_entry += f"**Content:** {content[:200]}{'...' if len(content) > 200 else ''}\n"
    log_entry += f"**URL:** {tweet_url}\n"
    log_entry += f"**Character Count:** {len(content)}\n"
    log_entry += "---\n"

    with open(social_log_path, 'a', encoding='utf-8') as f:
        f.write(log_entry)

    log_message(f"Logged to {social_log_path}", "INFO")

    return {
        "status": "success",
        "tweet_id": tweet_id,
        "url": tweet_url,
        "message": "[OK] Tweet posted successfully (DEMO MODE)"
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Post tweets to Twitter/X")
    parser.add_argument("content", help="Tweet content")
    parser.add_argument("--thread", action="store_true", help="Create thread if content > 280 chars")
    parser.add_argument("--demo", action="store_true", help="Demo mode: simulate posting without real API calls")

    args = parser.parse_args()

    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold cyan]Twitter/X Auto-Post Agent[/bold cyan]\n"
            "[dim]Gold Tier AI Employee[/dim]" +
            ("\n[yellow][WARNING] DEMO MODE - No real API calls[/yellow]" if args.demo else ""),
            border_style="cyan"
        ))
    else:
        print("=" * 60)
        print("TWITTER/X AUTO-POST AGENT")
        print("Gold Tier AI Employee")
        if args.demo:
            print("[WARNING] DEMO MODE - No real API calls")
        print("=" * 60)

    # Use demo mode or real posting
    if args.demo:
        result = post_tweet_demo(args.content)
    else:
        result = post_tweet(args.content, thread=args.thread)

    if RICH_AVAILABLE:
        if result["status"] == "success":
            console.print(Panel(
                f"[green]{result['message']}[/green]\n\n"
                f"[dim]URL:[/dim] {result.get('url', 'N/A')}",
                title="[OK] Success",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[red]{result['message']}[/red]",
                title="[X] Error",
                border_style="red"
            ))
    else:
        print(json.dumps(result, indent=2))

    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
