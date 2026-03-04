# Social Media Setup Guide - Gold Tier

Complete guide for setting up all social media integrations in Gold Tier AI Employee.

## 🎯 Overview

Gold Tier includes comprehensive social media automation across 4 major platforms:

- **LinkedIn** - Browser automation with Playwright
- **Twitter/X** - API v2 integration with thread support
- **Facebook** - Meta Graph API for Page posting
- **Instagram** - Meta Graph API for Business account posting

All posts are automatically logged to:
- `logs/social.log` - Social media activity log
- `logs/actions.log` - General activity log
- `AI_Employee_Vault/Reports/Social_Log.md` - Centralized social summary

---

## 📦 Installation

### Core Dependencies

```bash
# Install all social media dependencies
pip install tweepy requests pillow python-dotenv playwright
playwright install chromium
```

### Individual Platform Dependencies

**LinkedIn**:
```bash
pip install playwright python-dotenv
playwright install chromium
```

**Twitter/X**:
```bash
pip install tweepy python-dotenv
```

**Facebook/Instagram**:
```bash
pip install requests python-dotenv pillow
```

---

## 🔑 Credentials Setup

### 1. LinkedIn

**Requirements**:
- LinkedIn account
- Email and password

**Setup**:
```bash
# Add to .env
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password_here
```

**Notes**:
- Uses browser automation (may violate LinkedIn ToS)
- Use at your own risk
- Limit to 5-10 posts per day

---

### 2. Twitter/X

**Requirements**:
- Twitter Developer account
- Twitter app with Read and Write permissions

**Setup Steps**:

1. Go to https://developer.twitter.com/
2. Create a new app (or use existing)
3. Navigate to "Keys and tokens"
4. Generate API keys and access tokens
5. Ensure app has "Read and Write" permissions

**Add to .env**:
```bash
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
TWITTER_BEARER_TOKEN=your-bearer-token
```

**Rate Limits**:
- 300 tweets per 3 hours
- 50 requests per 15 minutes

---

### 3. Facebook

**Requirements**:
- Facebook Page (not personal profile)
- Facebook Developer account
- Long-lived access token

**Setup Steps**:

1. Go to https://developers.facebook.com/
2. Create a new app (Business type)
3. Add "Pages" product
4. Use Graph API Explorer to generate token
5. Request permissions: `pages_manage_posts`
6. Generate long-lived token (60 days)

**Get Page ID**:
- Go to your Facebook Page
- Settings → About → Page ID

**Add to .env**:
```bash
FACEBOOK_ACCESS_TOKEN=your-long-lived-access-token
FACEBOOK_PAGE_ID=your-facebook-page-id
```

**Rate Limits**:
- 200 calls per hour per user

---

### 4. Instagram

**Requirements**:
- Instagram Business or Creator account
- Account linked to a Facebook Page
- Facebook access token (same as above)

**Setup Steps**:

1. Convert Instagram to Business account
2. Link to Facebook Page
3. Get Instagram Account ID via Graph API:
   ```bash
   curl "https://graph.facebook.com/v18.0/{page-id}?fields=instagram_business_account&access_token={token}"
   ```

**Add to .env**:
```bash
FACEBOOK_ACCESS_TOKEN=your-long-lived-access-token
INSTAGRAM_ACCOUNT_ID=your-instagram-business-account-id
```

**Requirements**:
- Images must be publicly accessible URLs
- Supported formats: JPG, PNG
- Min dimensions: 320x320 pixels
- Max file size: 8MB
- Max caption: 2200 characters

**Rate Limits**:
- 25 posts per day

---

## 🚀 Usage Examples

### LinkedIn

```bash
# Post to LinkedIn
python scripts/post_linkedin.py "Just shipped a new feature! 🚀"

# Debug mode (visible browser)
python scripts/post_linkedin.py "Test post" --headless=false
```

**Python API**:
```python
from scripts.post_linkedin import LinkedInPoster

poster = LinkedInPoster(headless=True)
await poster.post("Your content here")
```

---

### Twitter/X

```bash
# Post a tweet
python scripts/post_twitter.py "Just shipped a new feature! 🚀"

# Post a thread (auto-splits if > 280 chars)
python scripts/post_twitter.py "Long content that will be automatically split into multiple tweets..." --thread
```

**Python API**:
```python
from scripts.post_twitter import post_tweet

# Simple tweet
result = post_tweet("Your tweet content")

# Thread
result = post_tweet("Long content...", thread=True)
```

**Features**:
- Character limit validation (280 chars)
- Automatic thread creation
- Tweet history tracking in `AI_Employee_Vault/Reports/twitter_history.json`

---

### Facebook

```bash
# Text post
python scripts/post_facebook.py "Check out our latest update! 🚀"

# Link post
python scripts/post_facebook.py "Read our blog post" --link "https://example.com/blog"
```

**Python API**:
```python
from scripts.post_facebook import post_facebook

# Text post
result = post_facebook("Your content")

# Link post
result = post_facebook("Your content", link="https://example.com")
```

---

### Instagram

```bash
# Post image with caption
python scripts/post_instagram.py "Beautiful sunset! 🌅 #nature" "https://example.com/image.jpg"

# With local image validation
python scripts/post_instagram.py "Caption" "https://cdn.com/image.jpg" --validate-local "local/image.jpg"
```

**Python API**:
```python
from scripts.post_instagram import post_instagram

result = post_instagram(
    caption="Your caption with hashtags",
    image_url="https://publicly-accessible-url.com/image.jpg"
)
```

**Important**: Images must be publicly accessible URLs. Upload to a CDN first if needed.

---

## 🔌 MCP Integration

All social media tools are available via the Business MCP Server:

```bash
# Start MCP server
python mcp/business_mcp/server.py
```

**Available Tools**:
- `post_linkedin` - Post to LinkedIn
- `post_twitter` - Post to Twitter/X
- `post_facebook` - Post to Facebook Page
- `post_instagram` - Post to Instagram
- `send_email` - Send emails
- `log_activity` - Log business activities

---

## 📊 Monitoring & Logging

### Log Files

**logs/social.log** - Social media specific logs:
```
[2026-03-04 14:30:00] [INFO] [TWITTER] Posting tweet: Just shipped...
[2026-03-04 14:30:01] [SUCCESS] [TWITTER] Tweet posted successfully: 1234567890
[2026-03-04 14:31:00] [INFO] [FACEBOOK] Posting to Facebook: Check out...
[2026-03-04 14:31:02] [SUCCESS] [FACEBOOK] Facebook post successful: 123456789_987654321
```

**logs/actions.log** - All activity logs (includes social media)

**AI_Employee_Vault/Reports/Social_Log.md** - Centralized social summary

### View Logs

```bash
# Watch social media activity in real-time
tail -f logs/social.log

# View all logs
tail -f logs/actions.log

# Filter by platform
grep TWITTER logs/social.log
grep FACEBOOK logs/social.log
grep INSTAGRAM logs/social.log
grep LINKEDIN logs/actions.log
```

---

## 🛠️ Troubleshooting

### Twitter Issues

**Authentication Failed**:
- Verify all 5 credentials in .env
- Check app has "Read and Write" permissions
- Regenerate tokens if needed

**Rate Limit Exceeded**:
- Wait before retrying (300 tweets per 3 hours)
- Check history file for recent posts

**Duplicate Tweet**:
- Twitter blocks duplicate content
- Add timestamp or variation

---

### Facebook Issues

**Invalid Access Token**:
- Token expired (60-day limit)
- Regenerate long-lived token
- Verify permissions: `pages_manage_posts`

**Page Not Found**:
- Verify FACEBOOK_PAGE_ID is correct
- Check app has access to the page

---

### Instagram Issues

**Image Upload Failed**:
- Image must be publicly accessible URL
- Upload to CDN first
- Check format (JPG/PNG only)
- Verify dimensions (min 320px)

**Account Not Found**:
- Verify INSTAGRAM_ACCOUNT_ID
- Ensure account is Business type
- Check account is linked to Facebook Page

---

### LinkedIn Issues

**Login Failed**:
- Check credentials in .env
- Run in visible mode: `--headless=false`
- Check for CAPTCHA or 2FA
- Review screenshots in `logs/screenshots/`

**Post Button Not Found**:
- LinkedIn UI may have changed
- Check HTML snapshot: `logs/page_source.html`
- Update selectors in script if needed

---

## 🔒 Security Best Practices

1. **Never commit .env** - Contains sensitive API keys
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate tokens regularly** - Generate new tokens periodically
4. **Monitor usage** - Check platform dashboards for unusual activity
5. **Limit posting frequency** - Respect rate limits
6. **Review logs** - Check for failed attempts or errors

---

## 📈 Best Practices

### Content Strategy

- **LinkedIn**: Professional content, industry insights, company updates
- **Twitter/X**: Quick updates, news, engagement, threads for longer content
- **Facebook**: Community engagement, events, longer-form content
- **Instagram**: Visual content, behind-the-scenes, brand storytelling

### Posting Frequency

- **LinkedIn**: 1-2 posts per day
- **Twitter/X**: 3-10 tweets per day
- **Facebook**: 1-2 posts per day
- **Instagram**: 1-2 posts per day

### Automation Tips

1. Schedule posts during peak engagement times
2. Use consistent branding across platforms
3. Monitor engagement and adjust strategy
4. Respond to comments and messages manually
5. Mix automated and manual posts
6. Test content before automating

---

## 🎯 Integration Examples

### Post to All Platforms

```python
from scripts.post_twitter import post_tweet
from scripts.post_facebook import post_facebook
from scripts.post_linkedin import LinkedInPoster

content = "Just launched our new product! 🚀"

# Twitter
post_tweet(content)

# Facebook
post_facebook(content, link="https://example.com/product")

# LinkedIn
poster = LinkedInPoster()
await poster.post(content)
```

### Scheduled Posting

```python
import schedule
import time
from scripts.post_twitter import post_tweet

def post_daily_update():
    post_tweet("Good morning! Here's today's update...")

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(post_daily_update)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Error Recovery

```python
from scripts.error_recovery import with_error_recovery
from scripts.post_twitter import post_tweet

@with_error_recovery
def safe_post_tweet(content):
    return post_tweet(content)

# Automatically retries on failure
safe_post_tweet("Your content")
```

---

## 📚 Additional Resources

- **Twitter API Docs**: https://developer.twitter.com/en/docs
- **Meta Graph API Docs**: https://developers.facebook.com/docs/graph-api
- **LinkedIn Automation**: Use at your own risk
- **Playwright Docs**: https://playwright.dev/python/

---

## ✅ Quick Setup Checklist

- [ ] Install dependencies: `pip install tweepy requests pillow python-dotenv playwright`
- [ ] Install Chromium: `playwright install chromium`
- [ ] Copy `.env.example` to `.env`
- [ ] Add LinkedIn credentials
- [ ] Create Twitter Developer app and add credentials
- [ ] Create Facebook app and generate access token
- [ ] Get Facebook Page ID
- [ ] Link Instagram Business account and get ID
- [ ] Test each platform individually
- [ ] Monitor logs for errors
- [ ] Set up automated posting schedule (optional)

---

**Gold Tier AI Employee - Social Media Automation**

*Last Updated: March 4, 2026*
