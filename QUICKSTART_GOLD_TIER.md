# Quick Start Guide - Gold Tier Integrations

## Installation (5 minutes)

### Step 1: Install All Dependencies
```bash
# Install everything at once
pip install mcp requests python-dotenv tweepy pillow
```

### Step 2: Configure Credentials

Create or update your `.env` file with all credentials:

```env
# === ODOO ERP ===
ODOO_URL=https://your-instance.odoo.com
ODOO_DB=your-database-name
ODOO_USERNAME=your-email@example.com
ODOO_PASSWORD=your-api-key

# === TWITTER ===
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
TWITTER_BEARER_TOKEN=your-bearer-token

# === META (Facebook/Instagram) ===
META_ACCESS_TOKEN=your-long-lived-token
FACEBOOK_PAGE_ID=your-page-id
INSTAGRAM_ACCOUNT_ID=your-instagram-business-id
```

### Step 3: Test Each Integration

```bash
# Test Odoo MCP (runs as server)
python mcp/odoo_mcp/server.py

# Test Twitter (post a tweet)
python .claude/skills/twitter-post/twitter_post.py "Test tweet from Gold Tier AI! 🚀"

# Test Facebook (post to page)
python .claude/skills/social-meta/social_meta.py facebook "Test post from Gold Tier AI!"
```

---

## Usage Examples

### Odoo: Create Invoice via MCP

When integrated with Claude Desktop:
```
Create an invoice for customer ID 123 with:
- Consulting Services: 10 hours at $150/hr
- Travel Expenses: $250
```

### Twitter: Post Tweet

```python
from twitter_post import post_tweet

# Simple tweet
post_tweet("Excited to announce our Q1 results! 📊 #business")

# Long content as thread
post_tweet("Very long announcement...", thread=True)
```

### Facebook: Share Update

```python
from social_meta import post_facebook

# Text post
post_facebook("Check out our latest blog post!")

# Link post
post_facebook("New article published!", link="https://example.com/blog")
```

### Instagram: Post Image

```python
from social_meta import post_instagram

post_instagram(
    "Beautiful product shot! 📸 #photography",
    "https://cdn.example.com/product.jpg"
)
```

---

## Integration with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "business-mcp": {
      "command": "python",
      "args": ["F:/FTEs/Gold Tier/mcp/business_mcp/server.py"]
    },
    "odoo-mcp": {
      "command": "python",
      "args": ["F:/FTEs/Gold Tier/mcp/odoo_mcp/server.py"]
    }
  }
}
```

Skills are automatically available in Claude Code.

---

## Monitoring & Logs

### Check Activity Logs

```bash
# Business activities
tail -f vault/logs/business.log

# Odoo operations
tail -f vault/logs/odoo.log

# Social media posts
tail -f logs/social.log

# Twitter history
cat AI_Employee_Vault/Reports/twitter_history.json
```

### View Recent Activity

```bash
# Last 20 Odoo operations
tail -20 vault/logs/odoo.log

# Last 10 social posts
tail -10 logs/social.log
```

---

## Credential Setup Guides

### Odoo API Key
1. Login to Odoo instance
2. Settings → Users → Your User
3. Account Security → API Keys
4. Generate new key
5. Copy to ODOO_PASSWORD in .env

### Twitter API
1. Go to https://developer.twitter.com/
2. Create app or use existing
3. Keys and Tokens → Generate
4. Copy all 5 credentials to .env
5. Ensure "Read and Write" permissions

### Facebook/Instagram
1. Go to https://developers.facebook.com/
2. Create Business app
3. Add Instagram and Pages products
4. Graph API Explorer → Generate Token
5. Request permissions: `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`
6. Generate long-lived token (60 days)
7. Get Page ID from Facebook Page settings
8. Get Instagram ID via Graph API: `/{page-id}?fields=instagram_business_account`

---

## Troubleshooting

### "Module not found" error
```bash
pip install mcp requests python-dotenv tweepy pillow
```

### "Authentication failed"
- Check credentials in .env file
- Verify API keys are active
- Ensure correct permissions granted

### "Connection timeout"
- Check internet connection
- Verify API endpoints are accessible
- Check firewall settings

### "Rate limit exceeded"
- Twitter: 300 tweets per 3 hours
- Facebook: 200 calls per hour
- Instagram: 25 posts per day
- Wait before retrying

---

## What's Included

✓ **Odoo MCP Server** - Invoice creation, listing, payment recording
✓ **Twitter Skill** - Tweet posting with thread support
✓ **Facebook Skill** - Page posting with link sharing
✓ **Instagram Skill** - Image posting to Business accounts
✓ **Comprehensive logging** - All activities tracked
✓ **Error handling** - Production-ready error management
✓ **Documentation** - Complete guides for each integration
✓ **Examples** - Ready-to-use code samples

---

## File Locations

```
mcp/odoo_mcp/server.py              - Odoo MCP server
.claude/skills/twitter-post/        - Twitter skill
.claude/skills/social-meta/         - Facebook/Instagram skill
vault/logs/odoo.log                 - Odoo activity log
logs/social.log                     - Social media log
AI_Employee_Vault/Reports/          - Twitter history
```

---

## Next Steps

1. ✓ Install dependencies: `pip install mcp requests python-dotenv tweepy pillow`
2. ✓ Configure `.env` with all credentials
3. ✓ Test each integration individually
4. ✓ Add Odoo MCP to Claude Desktop config
5. ✓ Monitor logs for activity
6. ✓ Set calendar reminder to rotate API tokens

Ready for production! 🚀
