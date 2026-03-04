# Social Summary Skill

## Description

Centralized logging system for all social media posts across platforms. Tracks posts to LinkedIn, Facebook, X (Twitter), and Instagram in a single unified log file.

## Trigger

**Programmatic:** Import and call from other skills
```python
from social_summary import log_social_post
```

**Command-line:**
```bash
python .claude/skills/social-summary/social_summary.py --platform LinkedIn --content "Post text"
```

## Capabilities

- Centralized social media activity logging
- Multi-platform support (LinkedIn, Facebook, X, Instagram)
- Post content tracking with timestamps
- URL tracking for published posts
- Metadata storage (likes, comments, shares)
- Post count statistics by platform
- Recent posts retrieval
- Summary report generation

## File Structure

```
.claude/skills/social-summary/
  ├── social_summary.py          # Main implementation
  ├── SKILL.md                   # This file
  ├── EXAMPLES.md                # Usage examples
  └── requirements.txt           # Dependencies (stdlib only)

AI_Employee_Vault/Reports/
  └── Social_Log.md              # Centralized social media log

logs/
  └── actions.log                # Activity logging
```

## Social_Log.md Format

```markdown
# Social Media Activity Log

This file tracks all social media posts across platforms.

**Platforms Tracked:**
- LinkedIn
- Facebook
- X (Twitter)
- Instagram

---

## LinkedIn Post - 2026-03-03

**Posted:** 2026-03-03 16:30:00

**Content:**
```
Just published a new article about AI automation...
```

**URL:** https://linkedin.com/posts/123456

**Metadata:**
- Likes: 0
- Comments: 0
- Shares: 0

---

## X Post - 2026-03-03

**Posted:** 2026-03-03 17:15:00

**Content:**
```
Excited to share our latest project! #AI #Automation
```

**URL:** https://x.com/user/status/123456

**Metadata:**
- Likes: 0
- Retweets: 0
- Replies: 0

---
```

## Core Functions

### log_social_post()

Log a social media post to Social_Log.md.

```python
def log_social_post(
    platform: str,
    content: str,
    post_url: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> bool
```

**Parameters:**
- `platform` (str): Platform name (LinkedIn, Facebook, X, Instagram)
- `content` (str): Post content/text
- `post_url` (str, optional): URL to the published post
- `metadata` (dict, optional): Additional data (likes, comments, shares, etc.)

**Returns:**
- `bool`: True if logged successfully

**Example:**
```python
log_social_post(
    platform="LinkedIn",
    content="Just published a new article about AI...",
    post_url="https://linkedin.com/posts/123",
    metadata={"likes": 0, "comments": 0, "shares": 0}
)
```

### get_post_count()

Get count of posts in Social_Log.md.

```python
def get_post_count(platform: Optional[str] = None) -> int
```

**Parameters:**
- `platform` (str, optional): Filter by platform name

**Returns:**
- `int`: Number of posts

**Example:**
```python
# Total posts across all platforms
total = get_post_count()

# Posts on LinkedIn only
linkedin_count = get_post_count(platform="LinkedIn")
```

### get_recent_posts()

Get recent posts from Social_Log.md.

```python
def get_recent_posts(limit: int = 10, platform: Optional[str] = None) -> list
```

**Parameters:**
- `limit` (int): Maximum number of posts to return
- `platform` (str, optional): Filter by platform name

**Returns:**
- `list`: List of post dictionaries

**Example:**
```python
# Get 5 most recent posts
recent = get_recent_posts(limit=5)

# Get recent LinkedIn posts only
linkedin_posts = get_recent_posts(limit=10, platform="LinkedIn")
```

### generate_summary()

Generate summary statistics for posts.

```python
def generate_summary(days: int = 7) -> Dict
```

**Parameters:**
- `days` (int): Number of days to include (currently informational)

**Returns:**
- `dict`: Summary statistics with total_posts, by_platform, period_days

**Example:**
```python
summary = generate_summary(days=7)
print(f"Total posts: {summary['total_posts']}")
print(f"LinkedIn: {summary['by_platform'].get('LinkedIn', 0)}")
```

## Integration with Other Skills

### LinkedIn Skill Integration

```python
# In .claude/skills/linkedin-post/linkedin_post.py

from social_summary import log_social_post

def post_to_linkedin(content: str) -> bool:
    # ... post to LinkedIn ...

    # Log to Social_Log.md
    log_social_post(
        platform="LinkedIn",
        content=content,
        post_url=post_url,
        metadata={
            "likes": 0,
            "comments": 0,
            "shares": 0
        }
    )
```

### Twitter/X Skill Integration

```python
# In .claude/skills/twitter-post/twitter_post.py

from social_summary import log_social_post

def post_tweet(content: str) -> bool:
    # ... post to Twitter ...

    # Log to Social_Log.md
    log_social_post(
        platform="X",
        content=content,
        post_url=tweet_url,
        metadata={
            "likes": 0,
            "retweets": 0,
            "replies": 0
        }
    )
```

### Facebook/Instagram Skill Integration

```python
# In .claude/skills/social-meta/social_meta.py

from social_summary import log_social_post

def post_to_facebook(content: str) -> bool:
    # ... post to Facebook ...

    # Log to Social_Log.md
    log_social_post(
        platform="Facebook",
        content=content,
        post_url=post_url,
        metadata={
            "likes": 0,
            "comments": 0,
            "shares": 0
        }
    )

def post_to_instagram(content: str, image_url: str) -> bool:
    # ... post to Instagram ...

    # Log to Social_Log.md
    log_social_post(
        platform="Instagram",
        content=content,
        post_url=post_url,
        metadata={
            "likes": 0,
            "comments": 0
        }
    )
```

## Command-Line Usage

### Log a Post

```bash
python .claude/skills/social-summary/social_summary.py \
  --platform LinkedIn \
  --content "Just published a new article..." \
  --url "https://linkedin.com/posts/123"
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
Total Posts: 15

By Platform:
  LinkedIn: 8
  X: 4
  Facebook: 2
  Instagram: 1
============================================================
```

### View Recent Posts

```bash
python .claude/skills/social-summary/social_summary.py --recent 5
```

Output:
```
============================================================
RECENT POSTS (5)
============================================================

1. LinkedIn - 2026-03-03
   Just published a new article about AI automation...

2. X - 2026-03-03
   Excited to share our latest project! #AI #Automation...

3. LinkedIn - 2026-03-02
   Great discussion at today's conference...

4. Facebook - 2026-03-01
   Check out our new product launch...

5. Instagram - 2026-02-28
   Behind the scenes at our office...

============================================================
```

## CEO Briefing Integration

The Social Summary skill integrates with the CEO Briefing system:

```python
# In scripts/ceo_briefing.py

from social_summary import generate_summary, get_recent_posts

def generate_briefing():
    # ... other sections ...

    # Social Media Activity
    social_summary = generate_summary(days=7)
    briefing += f"\n## Social Media Activity\n\n"
    briefing += f"**Total Posts (Last 7 Days):** {social_summary['total_posts']}\n\n"

    if social_summary['by_platform']:
        briefing += "**By Platform:**\n"
        for platform, count in social_summary['by_platform'].items():
            briefing += f"- {platform}: {count} posts\n"

    # Recent posts
    recent = get_recent_posts(limit=3)
    if recent:
        briefing += "\n**Recent Posts:**\n"
        for post in recent:
            briefing += f"- {post['platform']} ({post['date']}): {post['content'][:50]}...\n"
```

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. Social Media Skill Posts Content                    │
│     - LinkedIn, Facebook, X, Instagram                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Call log_social_post()                              │
│     - Platform name                                     │
│     - Content text                                      │
│     - Post URL                                          │
│     - Metadata (likes, comments, etc.)                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Append to Social_Log.md                             │
│     - Timestamp                                         │
│     - Platform                                          │
│     - Content (truncated if long)                       │
│     - URL                                               │
│     - Metadata                                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Log to actions.log                                  │
│     - Success/failure status                            │
│     - Timestamp                                         │
└─────────────────────────────────────────────────────────┘
```

## Benefits

1. **Centralized Tracking:** All social media activity in one place
2. **Cross-Platform:** Supports all major platforms
3. **Historical Record:** Permanent log of all posts
4. **Analytics Ready:** Easy to generate statistics and reports
5. **CEO Briefing Integration:** Automatic inclusion in executive reports
6. **Zero Dependencies:** Uses Python standard library only
7. **Simple Integration:** Easy to add to existing social media skills

## Use Cases

### Track Marketing Campaigns

```python
# Post campaign content across platforms
for platform in ["LinkedIn", "Facebook", "X"]:
    post_content(platform, campaign_text)
    log_social_post(platform, campaign_text, metadata={"campaign": "Q1_2026"})

# Later: analyze campaign performance
posts = get_recent_posts(limit=100)
campaign_posts = [p for p in posts if "Q1_2026" in str(p)]
```

### Monitor Posting Frequency

```python
summary = generate_summary(days=30)
avg_per_day = summary['total_posts'] / 30
print(f"Average posts per day: {avg_per_day:.1f}")

for platform, count in summary['by_platform'].items():
    print(f"{platform}: {count/30:.1f} posts/day")
```

### Generate Social Media Report

```python
def generate_social_report():
    summary = generate_summary(days=7)
    recent = get_recent_posts(limit=10)

    report = f"# Social Media Weekly Report\n\n"
    report += f"**Total Posts:** {summary['total_posts']}\n\n"
    report += f"**By Platform:**\n"
    for platform, count in summary['by_platform'].items():
        report += f"- {platform}: {count}\n"

    report += f"\n**Recent Activity:**\n"
    for post in recent:
        report += f"- {post['platform']} ({post['date']})\n"

    return report
```

## Error Handling

The skill includes comprehensive error handling:

- File I/O errors are caught and logged
- Invalid parameters are handled gracefully
- Failed operations return False/empty results
- All errors logged to logs/actions.log

## Performance

- **Lightweight:** Minimal memory footprint
- **Fast:** Simple file append operations
- **Scalable:** Handles thousands of posts efficiently
- **No External Dependencies:** Pure Python stdlib

## Limitations

- No automatic post deletion/editing tracking
- No engagement metrics auto-update (manual metadata only)
- No post scheduling or queuing
- No image/media content storage (URLs only)
- Content truncated to 200 characters in log (full content in metadata)

## Future Enhancements

- Automatic engagement metrics updates
- Post scheduling and queuing
- Media content archival
- Analytics dashboard
- Export to CSV/JSON
- Search functionality
- Post editing history
- Hashtag tracking
- Audience insights integration

## Dependencies

- Python 3.7+
- Standard library only (no external packages)

## Troubleshooting

### Social_Log.md Not Created

**Issue:** Log file doesn't exist
**Solution:** File is auto-created on first use. Ensure AI_Employee_Vault/Reports/ directory exists.

### Posts Not Appearing

**Issue:** log_social_post() returns True but posts not in log
**Solution:** Check file permissions, verify VAULT_DIR path is correct

### Encoding Errors

**Issue:** Unicode characters causing errors
**Solution:** All files use UTF-8 encoding. Ensure system supports UTF-8.

## Notes

- All timestamps in local system time
- Content truncated to 200 chars in log (prevents file bloat)
- Metadata is optional but recommended for analytics
- Log file grows over time - consider periodic archival
- Integrates seamlessly with existing Gold Tier skills

## Support

For issues or questions:
1. Check EXAMPLES.md for usage patterns
2. Review logs/actions.log for error details
3. Verify AI_Employee_Vault/Reports/ directory exists
4. Ensure proper file permissions
