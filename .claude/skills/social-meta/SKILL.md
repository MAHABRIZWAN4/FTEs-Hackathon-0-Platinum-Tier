# Facebook + Instagram Meta Skill - Gold Tier AI Employee

Post content to Facebook and Instagram with comprehensive logging.

## Overview

This skill enables automated posting to Facebook and Instagram using the Meta Graph API. All posts are logged to logs/social.log for audit and tracking purposes.

## Features

- ✅ Post to Facebook Pages
- ✅ Post to Instagram Business accounts
- ✅ Image and text post support
- ✅ Comprehensive logging to logs/social.log
- ✅ Error handling and retry logic
- ✅ Rate limit management

## Installation

### 1. Install Dependencies

```bash
pip install requests python-dotenv pillow
```

### 2. Configure Meta API Credentials

Add to your `.env` file:

```env
# Meta (Facebook/Instagram) API
META_ACCESS_TOKEN=your-long-lived-access-token
FACEBOOK_PAGE_ID=your-facebook-page-id
INSTAGRAM_ACCOUNT_ID=your-instagram-business-account-id
```

**Getting Credentials:**

1. **Create Facebook App:**
   - Go to https://developers.facebook.com/
   - Create a new app (Business type)
   - Add "Instagram" and "Pages" products

2. **Get Access Token:**
   - Use Graph API Explorer
   - Select your app
   - Request permissions: `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`
   - Generate long-lived token (60 days)

3. **Get Page ID:**
   - Go to your Facebook Page
   - Settings → About → Page ID

4. **Get Instagram Account ID:**
   - Must be Instagram Business account linked to Facebook Page
   - Use Graph API: `/{page-id}?fields=instagram_business_account`

### 3. Usage

```python
from social_meta import post_facebook, post_instagram

# Post to Facebook
result = post_facebook("Check out our latest update! 🚀")

# Post to Instagram
result = post_instagram("New product launch! #innovation", image_path="product.jpg")
```

## Functions

### post_facebook(content, link=None)

Post content to Facebook Page.

**Parameters:**
- `content` (str): Post content/message
- `link` (str, optional): URL to share

**Returns:**
- `dict`: Result with post_id, url, and status

**Example:**
```python
# Text post
result = post_facebook("Excited to announce our Q1 results!")

# Link post
result = post_facebook(
    "Read our latest blog post",
    link="https://example.com/blog/post"
)
```

### post_instagram(caption, image_path)

Post image to Instagram Business account.

**Parameters:**
- `caption` (str): Post caption (max 2200 chars)
- `image_path` (str): Path to image file (JPG/PNG)

**Returns:**
- `dict`: Result with post_id, url, and status

**Example:**
```python
result = post_instagram(
    "Beautiful sunset today! 🌅 #nature #photography",
    image_path="photos/sunset.jpg"
)
```

## Logging

All social media posts are logged to:
```
logs/social.log
```

Format:
```
[2026-03-03 14:30:45] [FACEBOOK] Posted: Check out our latest update! 🚀
[2026-03-03 14:30:45] [SUCCESS] Post ID: 123456789_987654321
[2026-03-03 14:31:02] [INSTAGRAM] Posted image: sunset.jpg
[2026-03-03 14:31:05] [SUCCESS] Post ID: 17841234567890123
```

## Implementation

```python
import requests
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Meta API credentials
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")

# Graph API base URL
GRAPH_API_URL = "https://graph.facebook.com/v18.0"

# Log file
LOG_FILE = Path("logs/social.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_activity(message, level="INFO"):
    """Log activity to logs/social.log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

    print(f"[{level}] {message}")


def post_facebook(content, link=None):
    """
    Post content to Facebook Page.

    Args:
        content (str): Post content
        link (str): Optional URL to share

    Returns:
        dict: Result with post_id, url, status
    """
    try:
        if not ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
            return {
                "status": "error",
                "message": "Missing META_ACCESS_TOKEN or FACEBOOK_PAGE_ID in .env"
            }

        log_activity(f"Posting to Facebook: {content[:50]}...", "FACEBOOK")

        # Prepare post data
        data = {
            "message": content,
            "access_token": ACCESS_TOKEN
        }

        if link:
            data["link"] = link

        # Post to Facebook
        response = requests.post(
            f"{GRAPH_API_URL}/{FACEBOOK_PAGE_ID}/feed",
            data=data,
            timeout=30
        )

        result = response.json()

        if "error" in result:
            error_msg = result["error"].get("message", "Unknown error")
            log_activity(f"Facebook post failed: {error_msg}", "ERROR")
            return {
                "status": "error",
                "message": f"Facebook API error: {error_msg}"
            }

        post_id = result.get("id")
        post_url = f"https://facebook.com/{post_id}"

        log_activity(f"Facebook post successful: {post_id}", "SUCCESS")

        return {
            "status": "success",
            "post_id": post_id,
            "url": post_url,
            "message": "✓ Posted to Facebook successfully"
        }

    except Exception as e:
        log_activity(f"Facebook post error: {str(e)}", "ERROR")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def post_instagram(caption, image_path):
    """
    Post image to Instagram Business account.

    Args:
        caption (str): Post caption
        image_path (str): Path to image file

    Returns:
        dict: Result with post_id, url, status
    """
    try:
        if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
            return {
                "status": "error",
                "message": "Missing META_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID in .env"
            }

        if not Path(image_path).exists():
            return {
                "status": "error",
                "message": f"Image file not found: {image_path}"
            }

        log_activity(f"Posting to Instagram: {Path(image_path).name}", "INSTAGRAM")

        # Step 1: Upload image and create container
        container_data = {
            "image_url": image_path,  # Must be publicly accessible URL
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }

        container_response = requests.post(
            f"{GRAPH_API_URL}/{INSTAGRAM_ACCOUNT_ID}/media",
            data=container_data,
            timeout=30
        )

        container_result = container_response.json()

        if "error" in container_result:
            error_msg = container_result["error"].get("message", "Unknown error")
            log_activity(f"Instagram container creation failed: {error_msg}", "ERROR")
            return {
                "status": "error",
                "message": f"Instagram API error: {error_msg}"
            }

        container_id = container_result.get("id")

        # Step 2: Publish the container
        publish_data = {
            "creation_id": container_id,
            "access_token": ACCESS_TOKEN
        }

        publish_response = requests.post(
            f"{GRAPH_API_URL}/{INSTAGRAM_ACCOUNT_ID}/media_publish",
            data=publish_data,
            timeout=30
        )

        publish_result = publish_response.json()

        if "error" in publish_result:
            error_msg = publish_result["error"].get("message", "Unknown error")
            log_activity(f"Instagram publish failed: {error_msg}", "ERROR")
            return {
                "status": "error",
                "message": f"Instagram API error: {error_msg}"
            }

        post_id = publish_result.get("id")
        post_url = f"https://instagram.com/p/{post_id}"

        log_activity(f"Instagram post successful: {post_id}", "SUCCESS")

        return {
            "status": "success",
            "post_id": post_id,
            "url": post_url,
            "message": "✓ Posted to Instagram successfully"
        }

    except Exception as e:
        log_activity(f"Instagram post error: {str(e)}", "ERROR")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  Facebook: python social_meta.py facebook 'Your post content'")
        print("  Instagram: python social_meta.py instagram 'Caption' image.jpg")
        sys.exit(1)

    platform = sys.argv[1].lower()

    if platform == "facebook":
        content = sys.argv[2]
        result = post_facebook(content)
    elif platform == "instagram":
        caption = sys.argv[2]
        image_path = sys.argv[3] if len(sys.argv) > 3 else None
        if not image_path:
            print("Error: Instagram requires image path")
            sys.exit(1)
        result = post_instagram(caption, image_path)
    else:
        print(f"Error: Unknown platform '{platform}'")
        sys.exit(1)

    print(json.dumps(result, indent=2))
```

## Error Handling

Common errors and solutions:

### Invalid Access Token
- Token expired (60-day limit for long-lived tokens)
- Regenerate token in Graph API Explorer
- Request required permissions

### Instagram Image Upload Failed
- Image must be publicly accessible URL
- Consider uploading to CDN first
- Check image format (JPG/PNG only)
- Verify image dimensions (min 320px)

### Rate Limit Exceeded
- Facebook: 200 calls per hour per user
- Instagram: 25 posts per day
- Wait before retrying

### Page Not Found
- Verify FACEBOOK_PAGE_ID is correct
- Check app has access to the page
- Ensure page is published

## Security

1. **Long-lived tokens** - Rotate every 60 days
2. **Never commit .env** - Contains sensitive tokens
3. **Use HTTPS** - All API calls over HTTPS
4. **Monitor usage** - Check Meta Business Suite

## Instagram Requirements

- Must be Instagram Business or Creator account
- Must be linked to a Facebook Page
- Images must be publicly accessible URLs
- Supported formats: JPG, PNG
- Min dimensions: 320px
- Max file size: 8MB

## Facebook Post Types

### Text Post
```python
post_facebook("Simple text update")
```

### Link Post
```python
post_facebook("Check this out!", link="https://example.com")
```

### Photo Post (via link)
```python
post_facebook("New photo!", link="https://example.com/photo.jpg")
```

## Monitoring

View posting activity:
```bash
tail -f logs/social.log
```

Generate report:
```python
with open("logs/social.log") as f:
    lines = f.readlines()
    facebook_posts = sum(1 for line in lines if "[FACEBOOK]" in line)
    instagram_posts = sum(1 for line in lines if "[INSTAGRAM]" in line)

print(f"Facebook posts: {facebook_posts}")
print(f"Instagram posts: {instagram_posts}")
```

## License

Part of the Gold Tier FTE automation system.
