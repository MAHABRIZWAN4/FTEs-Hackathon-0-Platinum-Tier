"""
Twitter Post Agent - Gold Tier AI Employee

Post tweets to Twitter/X with history tracking.
"""

import tweepy
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Social Summary integration
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude" / "skills" / "social-summary"))
    from social_summary import log_social_post
    SOCIAL_SUMMARY_AVAILABLE = True
except ImportError:
    SOCIAL_SUMMARY_AVAILABLE = False

# Twitter API credentials
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# History file
HISTORY_FILE = Path("AI_Employee_Vault/Reports/twitter_history.json")
HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_history():
    """Load tweet history from file."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"tweets": []}


def save_history(history):
    """Save tweet history to file."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def post_tweet(content, thread=False):
    """
    Post a tweet to Twitter.

    Args:
        content (str): Tweet content
        thread (bool): Split into thread if > 280 chars

    Returns:
        dict: Result with tweet_id, url, status
    """
    try:
        # Validate credentials
        if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
            return {
                "status": "error",
                "message": "Missing Twitter API credentials in .env"
            }

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
            return {
                "status": "error",
                "message": f"Tweet too long ({len(content)} chars). Max 280 or use thread=True"
            }

        # Post tweet
        response = client.create_tweet(text=content)
        tweet_id = response.data['id']

        # Get username for URL
        me = client.get_me()
        username = me.data.username
        tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

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

        # Log to Social Summary
        if SOCIAL_SUMMARY_AVAILABLE:
            try:
                log_social_post(
                    platform="X",
                    content=content,
                    post_url=tweet_url,
                    metadata={
                        "tweet_id": tweet_id,
                        "character_count": len(content),
                        "likes": 0,
                        "retweets": 0,
                        "replies": 0
                    }
                )
            except Exception as e:
                print(f"[WARNING] Failed to log to Social Summary: {str(e)}")

        return {
            "status": "success",
            "tweet_id": tweet_id,
            "url": tweet_url,
            "message": f"✓ Tweet posted successfully"
        }

    except tweepy.TweepyException as e:
        error_msg = str(e)

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
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def post_thread(client, content):
    """
    Post a thread of tweets.

    Args:
        client: Tweepy client
        content (str): Long content to split

    Returns:
        dict: Result with thread info
    """
    # Split content into 280-char chunks
    chunks = []
    words = content.split()
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= 270:  # Leave room for numbering
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

    # Get username
    me = client.get_me()
    username = me.data.username
    thread_url = f"https://twitter.com/{username}/status/{tweet_ids[0]}"

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

    # Log to Social Summary
    if SOCIAL_SUMMARY_AVAILABLE:
        try:
            log_social_post(
                platform="X",
                content=content,
                post_url=thread_url,
                metadata={
                    "tweet_id": tweet_ids[0],
                    "thread_ids": tweet_ids,
                    "tweet_count": len(chunks),
                    "is_thread": True,
                    "likes": 0,
                    "retweets": 0,
                    "replies": 0
                }
            )
        except Exception as e:
            print(f"[WARNING] Failed to log thread to Social Summary: {str(e)}")

    return {
        "status": "success",
        "tweet_ids": tweet_ids,
        "url": thread_url,
        "message": f"✓ Thread posted successfully ({len(chunks)} tweets)"
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python twitter_post.py 'Your tweet content'")
        sys.exit(1)

    content = sys.argv[1]
    result = post_tweet(content)

    print(json.dumps(result, indent=2))
