"""
Facebook + Instagram Meta Agent - Gold Tier AI Employee

Post content to Facebook and Instagram with logging.
"""

import requests
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

        # Log to Social Summary
        if SOCIAL_SUMMARY_AVAILABLE:
            try:
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
            except Exception as e:
                log_activity(f"Failed to log to Social Summary: {str(e)}", "WARNING")

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


def post_instagram(caption, image_url):
    """
    Post image to Instagram Business account.

    Args:
        caption (str): Post caption
        image_url (str): Publicly accessible image URL

    Returns:
        dict: Result with post_id, url, status
    """
    try:
        if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
            return {
                "status": "error",
                "message": "Missing META_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID in .env"
            }

        log_activity(f"Posting to Instagram: {caption[:50]}...", "INSTAGRAM")

        # Step 1: Create media container
        container_data = {
            "image_url": image_url,
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

        # Log to Social Summary
        if SOCIAL_SUMMARY_AVAILABLE:
            try:
                log_social_post(
                    platform="Instagram",
                    content=caption,
                    post_url=post_url,
                    metadata={
                        "post_id": post_id,
                        "media_id": container_id,
                        "likes": 0,
                        "comments": 0
                    }
                )
            except Exception as e:
                log_activity(f"Failed to log to Social Summary: {str(e)}", "WARNING")

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
        print("  Instagram: python social_meta.py instagram 'Caption' 'https://image-url.com/image.jpg'")
        sys.exit(1)

    platform = sys.argv[1].lower()

    if platform == "facebook":
        content = sys.argv[2]
        link = sys.argv[3] if len(sys.argv) > 3 else None
        result = post_facebook(content, link)
    elif platform == "instagram":
        caption = sys.argv[2]
        image_url = sys.argv[3] if len(sys.argv) > 3 else None
        if not image_url:
            print("Error: Instagram requires image URL")
            sys.exit(1)
        result = post_instagram(caption, image_url)
    else:
        print(f"Error: Unknown platform '{platform}'")
        sys.exit(1)

    print(json.dumps(result, indent=2))
