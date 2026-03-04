# Twitter Post Skill - Gold Tier AI Employee

Post tweets to Twitter/X and maintain posting history.

## Overview

This skill enables automated Twitter posting with comprehensive history tracking. All tweets are logged to the AI Employee Vault for audit and reporting purposes.

## Features

- ✅ Post tweets to Twitter/X via API
- ✅ Character limit validation (280 chars)
- ✅ Thread support for longer content
- ✅ History tracking in AI_Employee_Vault/Reports/
- ✅ Comprehensive error handling
- ✅ Rate limit management

## Installation

### 1. Install Dependencies

```bash
pip install tweepy python-dotenv
```

### 2. Configure Twitter API Credentials

Add to your `.env` file:

```env
# Twitter API v2 Credentials
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
TWITTER_BEARER_TOKEN=your-bearer-token
```

**Getting Credentials:**
1. Go to https://developer.twitter.com/
2. Create a new app or use existing
3. Generate API keys and access tokens
4. Ensure app has "Read and Write" permissions

### 3. Usage

Invoke the skill:
```bash
/twitter-post "Your tweet content here"
```

Or use programmatically:
```python
from twitter_post import post_tweet

result = post_tweet("Hello Twitter! 🚀")
print(result)
```

## Functions

### post_tweet(content, thread=False)

Post a tweet to Twitter.

**Parameters:**
- `content` (str): Tweet content (max 280 characters)
- `thread` (bool): If True and content > 280 chars, split into thread

**Returns:**
- `dict`: Result with tweet_id, url, and status

**Example:**
```python
# Simple tweet
result = post_tweet("Excited to announce our new product! 🎉")

# Long content as thread
result = post_tweet(
    "This is a long announcement that will be split into multiple tweets...",
    thread=True
)
```

## History Tracking

All tweets are logged to:
```
AI_Employee_Vault/Reports/twitter_history.json
```

Format:
```json
{
  "tweets": [
    {
      "id": "1234567890",
      "content": "Tweet content",
      "url": "https://twitter.com/user/status/1234567890",
      "timestamp": "2026-03-03T14:30:45Z",
      "status": "success",
      "character_count": 42
    }
  ]
}
```

## Implementation

The skill uses the Twitter API v2 via the Tweepy library:

```python
import tweepy
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

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
```

## Error Handling

Common errors and solutions:

### Authentication Failed
- Verify all 5 credentials in .env
- Check app has "Read and Write" permissions
- Regenerate tokens if needed

### Rate Limit Exceeded
- Twitter has rate limits (300 tweets per 3 hours)
- Wait before retrying
- Check history file for recent posts

### Duplicate Tweet
- Twitter blocks duplicate content
- Add timestamp or variation to content

## Security

1. **Never commit .env** - Contains sensitive API keys
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate keys regularly** - Generate new tokens periodically
4. **Monitor usage** - Check Twitter developer dashboard

## Reporting

View posting history:
```bash
cat AI_Employee_Vault/Reports/twitter_history.json
```

Generate report:
```python
import json

with open("AI_Employee_Vault/Reports/twitter_history.json") as f:
    data = json.load(f)

print(f"Total tweets: {len(data['tweets'])}")
print(f"Successful: {sum(1 for t in data['tweets'] if t['status'] == 'success')}")
print(f"Failed: {sum(1 for t in data['tweets'] if t['status'] == 'failed')}")
```

## License

Part of the Gold Tier FTE automation system.
