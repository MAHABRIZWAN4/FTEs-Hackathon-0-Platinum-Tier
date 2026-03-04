# Social Summary Skill - Examples

## Basic Usage

### Log a LinkedIn Post

```python
from social_summary import log_social_post

# Simple post
log_social_post(
    platform="LinkedIn",
    content="Just published a new article about AI automation in business."
)

# With URL
log_social_post(
    platform="LinkedIn",
    content="Excited to share our Q1 results!",
    post_url="https://linkedin.com/posts/123456"
)

# With metadata
log_social_post(
    platform="LinkedIn",
    content="Check out our latest product launch!",
    post_url="https://linkedin.com/posts/123456",
    metadata={
        "likes": 0,
        "comments": 0,
        "shares": 0
    }
)
```

### Log a Twitter/X Post

```python
log_social_post(
    platform="X",
    content="Excited to announce our new AI features! #AI #Innovation",
    post_url="https://x.com/user/status/123456",
    metadata={
        "likes": 0,
        "retweets": 0,
        "replies": 0
    }
)
```

### Log a Facebook Post

```python
log_social_post(
    platform="Facebook",
    content="Join us for our upcoming webinar on AI automation!",
    post_url="https://facebook.com/posts/123456",
    metadata={
        "likes": 0,
        "comments": 0,
        "shares": 0
    }
)
```

### Log an Instagram Post

```python
log_social_post(
    platform="Instagram",
    content="Behind the scenes at our office! #WorkLife #Tech",
    post_url="https://instagram.com/p/123456",
    metadata={
        "likes": 0,
        "comments": 0
    }
)
```

---

## Integration Examples

### LinkedIn Skill Integration

Update `.claude/skills/linkedin-post/linkedin_post.py`:

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from social_summary import log_social_post

def post_to_linkedin(content: str, access_token: str) -> dict:
    """Post to LinkedIn and log to Social_Log.md."""

    # Post to LinkedIn
    response = linkedin_api.post(content, access_token)

    if response.get('success'):
        # Log to Social_Log.md
        log_social_post(
            platform="LinkedIn",
            content=content,
            post_url=response.get('post_url'),
            metadata={
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "post_id": response.get('post_id')
            }
        )

    return response
```

### Twitter Skill Integration

Update `.claude/skills/twitter-post/twitter_post.py`:

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from social_summary import log_social_post

def post_tweet(content: str) -> bool:
    """Post tweet and log to Social_Log.md."""

    # Post to Twitter
    tweet = api.create_tweet(text=content)

    if tweet.data:
        tweet_id = tweet.data['id']
        tweet_url = f"https://x.com/user/status/{tweet_id}"

        # Log to Social_Log.md
        log_social_post(
            platform="X",
            content=content,
            post_url=tweet_url,
            metadata={
                "tweet_id": tweet_id,
                "likes": 0,
                "retweets": 0,
                "replies": 0
            }
        )

        return True

    return False
```

### Facebook/Instagram Skill Integration

Update `.claude/skills/social-meta/social_meta.py`:

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from social_summary import log_social_post

def post_to_facebook(content: str, access_token: str) -> bool:
    """Post to Facebook and log to Social_Log.md."""

    # Post to Facebook
    response = requests.post(
        f"https://graph.facebook.com/v18.0/{page_id}/feed",
        data={"message": content, "access_token": access_token}
    )

    if response.status_code == 200:
        post_id = response.json().get('id')
        post_url = f"https://facebook.com/{post_id}"

        # Log to Social_Log.md
        log_social_post(
            platform="Facebook",
            content=content,
            post_url=post_url,
            metadata={
                "post_id": post_id,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }
        )

        return True

    return False

def post_to_instagram(content: str, image_url: str, access_token: str) -> bool:
    """Post to Instagram and log to Social_Log.md."""

    # Post to Instagram (simplified)
    # ... Instagram posting logic ...

    if success:
        # Log to Social_Log.md
        log_social_post(
            platform="Instagram",
            content=content,
            post_url=post_url,
            metadata={
                "media_id": media_id,
                "likes": 0,
                "comments": 0
            }
        )

        return True

    return False
```

---

## Statistics and Reporting

### Get Post Counts

```python
from social_summary import get_post_count

# Total posts across all platforms
total = get_post_count()
print(f"Total posts: {total}")

# Posts by platform
linkedin_count = get_post_count(platform="LinkedIn")
twitter_count = get_post_count(platform="X")
facebook_count = get_post_count(platform="Facebook")
instagram_count = get_post_count(platform="Instagram")

print(f"LinkedIn: {linkedin_count}")
print(f"X: {twitter_count}")
print(f"Facebook: {facebook_count}")
print(f"Instagram: {instagram_count}")
```

### Get Recent Posts

```python
from social_summary import get_recent_posts

# Get 10 most recent posts
recent = get_recent_posts(limit=10)

for post in recent:
    print(f"{post['platform']} - {post['date']}")
    print(f"  {post['content'][:50]}...")
    print()

# Get recent LinkedIn posts only
linkedin_posts = get_recent_posts(limit=5, platform="LinkedIn")

for post in linkedin_posts:
    print(f"{post['date']}: {post['content']}")
```

### Generate Summary Report

```python
from social_summary import generate_summary

# Get summary statistics
summary = generate_summary(days=7)

print(f"Total Posts (Last 7 Days): {summary['total_posts']}")
print("\nBy Platform:")
for platform, count in summary['by_platform'].items():
    print(f"  {platform}: {count}")
```

---

## Command-Line Examples

### Log a Post from Command Line

```bash
# LinkedIn post
python .claude/skills/social-summary/social_summary.py \
  --platform LinkedIn \
  --content "Just published a new article about AI automation" \
  --url "https://linkedin.com/posts/123456"

# Twitter post
python .claude/skills/social-summary/social_summary.py \
  --platform X \
  --content "Excited to share our latest project! #AI" \
  --url "https://x.com/user/status/123456"

# Facebook post
python .claude/skills/social-summary/social_summary.py \
  --platform Facebook \
  --content "Join us for our upcoming webinar!" \
  --url "https://facebook.com/posts/123456"

# Instagram post
python .claude/skills/social-summary/social_summary.py \
  --platform Instagram \
  --content "Behind the scenes! #WorkLife" \
  --url "https://instagram.com/p/123456"
```

### View Statistics

```bash
python .claude/skills/social-summary/social_summary.py --stats
```

Output:
```
============================================================
SOCIAL MEDIA SUMMARY
============================================================
Total Posts: 25

By Platform:
  LinkedIn: 12
  X: 8
  Facebook: 3
  Instagram: 2
============================================================
```

### View Recent Posts

```bash
# Show 5 most recent posts
python .claude/skills/social-summary/social_summary.py --recent 5

# Show 10 most recent posts
python .claude/skills/social-summary/social_summary.py --recent 10
```

Output:
```
============================================================
RECENT POSTS (5)
============================================================

1. LinkedIn - 2026-03-03
   Just published a new article about AI automation in business...

2. X - 2026-03-03
   Excited to share our latest project! #AI #Innovation...

3. LinkedIn - 2026-03-02
   Great discussion at today's conference about the future of AI...

4. Facebook - 2026-03-01
   Join us for our upcoming webinar on AI automation!...

5. Instagram - 2026-02-28
   Behind the scenes at our office! #WorkLife #Tech...

============================================================
```

---

## CEO Briefing Integration

Add to `scripts/ceo_briefing.py`:

```python
import sys
from pathlib import Path

# Add skills to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "social-summary"))

from social_summary import generate_summary, get_recent_posts

def generate_social_section():
    """Generate social media section for CEO briefing."""

    section = "\n## Social Media Activity\n\n"

    # Get summary
    summary = generate_summary(days=7)

    section += f"**Total Posts (Last 7 Days):** {summary['total_posts']}\n\n"

    if summary['by_platform']:
        section += "**By Platform:**\n"
        for platform, count in summary['by_platform'].items():
            section += f"- {platform}: {count} posts\n"
        section += "\n"

    # Get recent posts
    recent = get_recent_posts(limit=5)

    if recent:
        section += "**Recent Posts:**\n\n"
        for i, post in enumerate(recent, 1):
            section += f"{i}. **{post['platform']}** ({post['date']})\n"
            content_preview = post['content'][:100]
            if len(post['content']) > 100:
                content_preview += "..."
            section += f"   {content_preview}\n\n"

    return section

# In main briefing generation function
def generate_briefing():
    briefing = "# CEO Weekly Briefing\n\n"

    # ... other sections ...

    # Add social media section
    briefing += generate_social_section()

    # ... rest of briefing ...

    return briefing
```

---

## Batch Logging

### Log Multiple Posts at Once

```python
from social_summary import log_social_post

posts = [
    {
        "platform": "LinkedIn",
        "content": "Post 1 content",
        "url": "https://linkedin.com/posts/1"
    },
    {
        "platform": "X",
        "content": "Post 2 content",
        "url": "https://x.com/user/status/2"
    },
    {
        "platform": "Facebook",
        "content": "Post 3 content",
        "url": "https://facebook.com/posts/3"
    }
]

for post in posts:
    success = log_social_post(
        platform=post['platform'],
        content=post['content'],
        post_url=post['url']
    )
    if success:
        print(f"Logged {post['platform']} post")
    else:
        print(f"Failed to log {post['platform']} post")
```

---

## Analytics Examples

### Calculate Posting Frequency

```python
from social_summary import generate_summary

summary = generate_summary(days=30)

total_posts = summary['total_posts']
avg_per_day = total_posts / 30

print(f"Total posts in last 30 days: {total_posts}")
print(f"Average posts per day: {avg_per_day:.1f}")

for platform, count in summary['by_platform'].items():
    avg = count / 30
    print(f"{platform}: {avg:.1f} posts/day")
```

### Find Most Active Platform

```python
from social_summary import generate_summary

summary = generate_summary(days=7)

if summary['by_platform']:
    most_active = max(summary['by_platform'].items(), key=lambda x: x[1])
    print(f"Most active platform: {most_active[0]} ({most_active[1]} posts)")
```

### Generate Weekly Report

```python
from social_summary import generate_summary, get_recent_posts
from datetime import datetime

def generate_weekly_social_report():
    """Generate weekly social media report."""

    report = f"# Social Media Weekly Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Summary
    summary = generate_summary(days=7)
    report += f"## Summary\n\n"
    report += f"**Total Posts:** {summary['total_posts']}\n\n"

    if summary['by_platform']:
        report += "**By Platform:**\n"
        for platform, count in summary['by_platform'].items():
            report += f"- {platform}: {count} posts\n"
        report += "\n"

    # Recent activity
    recent = get_recent_posts(limit=10)
    if recent:
        report += "## Recent Activity\n\n"
        for i, post in enumerate(recent, 1):
            report += f"### {i}. {post['platform']} - {post['date']}\n\n"
            report += f"{post['content']}\n\n"
            report += "---\n\n"

    return report

# Generate and save report
report = generate_weekly_social_report()
with open("AI_Employee_Vault/Reports/Social_Weekly_Report.md", "w") as f:
    f.write(report)
```

---

## Error Handling Examples

### Handle Logging Failures

```python
from social_summary import log_social_post

def safe_log_post(platform, content, url=None):
    """Safely log a post with error handling."""

    try:
        success = log_social_post(
            platform=platform,
            content=content,
            post_url=url
        )

        if success:
            print(f"[SUCCESS] Logged {platform} post")
        else:
            print(f"[WARNING] Failed to log {platform} post")

        return success

    except Exception as e:
        print(f"[ERROR] Exception while logging: {str(e)}")
        return False

# Use it
safe_log_post("LinkedIn", "Test post", "https://linkedin.com/posts/123")
```

### Retry on Failure

```python
from social_summary import log_social_post
import time

def log_with_retry(platform, content, url=None, max_retries=3):
    """Log post with retry logic."""

    for attempt in range(max_retries):
        try:
            success = log_social_post(platform, content, url)
            if success:
                return True

            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(1)

        except Exception as e:
            print(f"Attempt {attempt + 1} error: {str(e)}")
            time.sleep(1)

    print(f"Failed after {max_retries} attempts")
    return False
```

---

## Testing Examples

### Test Basic Logging

```python
from social_summary import log_social_post, get_post_count

# Get initial count
initial_count = get_post_count()

# Log test post
success = log_social_post(
    platform="LinkedIn",
    content="Test post for validation"
)

# Verify count increased
new_count = get_post_count()
assert new_count == initial_count + 1, "Post count should increase by 1"
assert success, "Logging should succeed"

print("[PASS] Basic logging test")
```

### Test Platform Filtering

```python
from social_summary import log_social_post, get_post_count

# Log posts to different platforms
log_social_post("LinkedIn", "LinkedIn test")
log_social_post("X", "Twitter test")
log_social_post("Facebook", "Facebook test")

# Verify counts
linkedin_count = get_post_count(platform="LinkedIn")
twitter_count = get_post_count(platform="X")
facebook_count = get_post_count(platform="Facebook")

print(f"LinkedIn: {linkedin_count}")
print(f"X: {twitter_count}")
print(f"Facebook: {facebook_count}")
```

---

## Maintenance Examples

### Archive Old Posts

```bash
# Backup Social_Log.md
cp AI_Employee_Vault/Reports/Social_Log.md \
   AI_Employee_Vault/Reports/Social_Log_Archive_2026_Q1.md

# Start fresh log (optional)
# mv AI_Employee_Vault/Reports/Social_Log.md \
#    AI_Employee_Vault/Reports/Social_Log_Archive_2026_Q1.md
```

### Export to CSV

```python
from social_summary import get_recent_posts
import csv

# Get all posts
posts = get_recent_posts(limit=1000)

# Export to CSV
with open('social_posts.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['platform', 'date', 'content'])
    writer.writeheader()
    writer.writerows(posts)

print(f"Exported {len(posts)} posts to social_posts.csv")
```

---

## Notes

- All examples use UTF-8 encoding
- Timestamps are in local system time
- Content is truncated to 200 chars in log file
- Metadata is optional but recommended for analytics
- Integration examples assume proper path setup
