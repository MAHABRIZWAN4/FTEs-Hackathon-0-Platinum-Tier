"""
Business MCP Server - Gold Tier AI Employee

This MCP server exposes business automation actions as tools:
- send_email: Send emails via SMTP
- post_linkedin: Post content to LinkedIn
- post_twitter: Post tweets to Twitter/X
- post_facebook: Post to Facebook Pages
- post_instagram: Post images to Instagram
- log_activity: Log business activities

Wraps existing scripts without duplication.
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directories to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("[ERROR] MCP SDK not installed. Run: pip install mcp")
    sys.exit(1)

# Import existing business action modules
try:
    from scripts.send_email import send_email as email_send_func, load_email_config, validate_config
    from scripts.post_linkedin import LinkedInPoster
    from scripts.post_twitter import post_tweet
    from scripts.post_facebook import post_facebook
    from scripts.post_instagram import post_instagram
except ImportError as e:
    print(f"[ERROR] Failed to import business scripts: {e}")
    print("Ensure all social media posting scripts exist in scripts/")
    sys.exit(1)

# Configuration
VAULT_LOGS_DIR = project_root / "vault" / "logs"
BUSINESS_LOG = VAULT_LOGS_DIR / "business.log"

# Ensure vault logs directory exists
VAULT_LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Initialize MCP server
app = Server("business-mcp")


def log_activity(message: str, level: str = "INFO") -> bool:
    """
    Log a business activity to vault/logs/business.log.

    Args:
        message (str): Activity message to log
        level (str): Log level (INFO, SUCCESS, WARNING, ERROR)

    Returns:
        bool: True if logged successfully
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        with open(BUSINESS_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)

        return True
    except Exception as e:
        print(f"[ERROR] Failed to log activity: {e}")
        return False


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available business automation tools.
    """
    return [
        Tool(
            name="send_email",
            description="Send an email via SMTP using configured credentials. Requires EMAIL_ADDRESS and EMAIL_PASSWORD in .env file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content (plain text or HTML)"
                    },
                    "html": {
                        "type": "boolean",
                        "description": "Whether body is HTML format (default: false)",
                        "default": False
                    }
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="post_linkedin",
            description="Post text content to LinkedIn using browser automation. Requires LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file. WARNING: May violate LinkedIn ToS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Text content to post on LinkedIn"
                    },
                    "headless": {
                        "type": "boolean",
                        "description": "Run browser in headless mode (default: true)",
                        "default": True
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="post_twitter",
            description="Post a tweet to Twitter/X using API v2. Requires TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, and TWITTER_BEARER_TOKEN in .env file. Supports threads for long content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Tweet content (max 280 chars, or use thread for longer)"
                    },
                    "thread": {
                        "type": "boolean",
                        "description": "Create thread if content > 280 chars (default: false)",
                        "default": False
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="post_facebook",
            description="Post content to Facebook Page using Meta Graph API. Requires FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Post content/message"
                    },
                    "link": {
                        "type": "string",
                        "description": "Optional URL to share"
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="post_instagram",
            description="Post image to Instagram Business account using Meta Graph API. Requires FACEBOOK_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in .env file. Image must be publicly accessible URL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "caption": {
                        "type": "string",
                        "description": "Post caption (max 2200 chars)"
                    },
                    "image_url": {
                        "type": "string",
                        "description": "Publicly accessible image URL"
                    }
                },
                "required": ["caption", "image_url"]
            }
        ),
        Tool(
            name="log_activity",
            description="Log a business activity message to vault/logs/business.log with timestamp and level.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Activity message to log"
                    },
                    "level": {
                        "type": "string",
                        "description": "Log level (INFO, SUCCESS, WARNING, ERROR)",
                        "enum": ["INFO", "SUCCESS", "WARNING", "ERROR"],
                        "default": "INFO"
                    }
                },
                "required": ["message"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool execution requests.
    """
    try:
        if name == "send_email":
            return await handle_send_email(arguments)
        elif name == "post_linkedin":
            return await handle_post_linkedin(arguments)
        elif name == "post_twitter":
            return await handle_post_twitter(arguments)
        elif name == "post_facebook":
            return await handle_post_facebook(arguments)
        elif name == "post_instagram":
            return await handle_post_instagram(arguments)
        elif name == "log_activity":
            return await handle_log_activity(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
    except Exception as e:
        error_msg = f"Tool execution error: {str(e)}"
        log_activity(f"[{name}] {error_msg}", "ERROR")
        return [TextContent(
            type="text",
            text=error_msg
        )]


async def handle_send_email(args: dict) -> list[TextContent]:
    """
    Handle send_email tool execution.
    """
    to_address = args.get("to")
    subject = args.get("subject")
    body = args.get("body")
    html = args.get("html", False)

    if not all([to_address, subject, body]):
        return [TextContent(
            type="text",
            text="Error: Missing required parameters (to, subject, body)"
        )]

    log_activity(f"Sending email to {to_address}: {subject}", "INFO")

    # Call existing send_email function
    success = email_send_func(to_address, subject, body, html)

    if success:
        log_activity(f"Email sent successfully to {to_address}", "SUCCESS")
        return [TextContent(
            type="text",
            text=f"✓ Email sent successfully to {to_address}\nSubject: {subject}"
        )]
    else:
        log_activity(f"Failed to send email to {to_address}", "ERROR")
        return [TextContent(
            type="text",
            text=f"✗ Failed to send email to {to_address}. Check logs/actions.log for details."
        )]


async def handle_post_linkedin(args: dict) -> list[TextContent]:
    """
    Handle post_linkedin tool execution.
    """
    content = args.get("content")
    headless = args.get("headless", True)

    if not content:
        return [TextContent(
            type="text",
            text="Error: Missing required parameter 'content'"
        )]

    log_activity(f"Posting to LinkedIn: {content[:50]}...", "INFO")

    # Create LinkedIn poster and post
    poster = LinkedInPoster(headless=headless)
    success = await poster.post(content)

    if success:
        log_activity("LinkedIn post published successfully", "SUCCESS")
        return [TextContent(
            type="text",
            text=f"✓ LinkedIn post published successfully\nContent: {content[:100]}{'...' if len(content) > 100 else ''}"
        )]
    else:
        log_activity("Failed to publish LinkedIn post", "ERROR")
        return [TextContent(
            type="text",
            text="✗ Failed to publish LinkedIn post. Check logs/actions.log for details."
        )]


async def handle_log_activity(args: dict) -> list[TextContent]:
    """
    Handle log_activity tool execution.
    """
    message = args.get("message")
    level = args.get("level", "INFO")

    if not message:
        return [TextContent(
            type="text",
            text="Error: Missing required parameter 'message'"
        )]

    success = log_activity(message, level)

    if success:
        return [TextContent(
            type="text",
            text=f"✓ Activity logged: [{level}] {message}"
        )]
    else:
        return [TextContent(
            type="text",
            text="✗ Failed to log activity"
        )]


async def handle_post_twitter(args: dict) -> list[TextContent]:
    """
    Handle post_twitter tool execution.
    """
    content = args.get("content")
    thread = args.get("thread", False)

    if not content:
        return [TextContent(
            type="text",
            text="Error: Missing required parameter 'content'"
        )]

    log_activity(f"Posting to Twitter: {content[:50]}...", "INFO")

    # Call post_tweet function
    result = post_tweet(content, thread=thread)

    if result["status"] == "success":
        log_activity("Twitter post published successfully", "SUCCESS")
        return [TextContent(
            type="text",
            text=f"✓ {result['message']}\nURL: {result.get('url', 'N/A')}"
        )]
    else:
        log_activity(f"Failed to publish Twitter post: {result['message']}", "ERROR")
        return [TextContent(
            type="text",
            text=f"✗ {result['message']}"
        )]


async def handle_post_facebook(args: dict) -> list[TextContent]:
    """
    Handle post_facebook tool execution.
    """
    content = args.get("content")
    link = args.get("link")

    if not content:
        return [TextContent(
            type="text",
            text="Error: Missing required parameter 'content'"
        )]

    log_activity(f"Posting to Facebook: {content[:50]}...", "INFO")

    # Call post_facebook function
    result = post_facebook(content, link=link)

    if result["status"] == "success":
        log_activity("Facebook post published successfully", "SUCCESS")
        return [TextContent(
            type="text",
            text=f"✓ {result['message']}\nURL: {result.get('url', 'N/A')}"
        )]
    else:
        log_activity(f"Failed to publish Facebook post: {result['message']}", "ERROR")
        return [TextContent(
            type="text",
            text=f"✗ {result['message']}"
        )]


async def handle_post_instagram(args: dict) -> list[TextContent]:
    """
    Handle post_instagram tool execution.
    """
    caption = args.get("caption")
    image_url = args.get("image_url")

    if not caption or not image_url:
        return [TextContent(
            type="text",
            text="Error: Missing required parameters 'caption' and 'image_url'"
        )]

    log_activity(f"Posting to Instagram: {caption[:50]}...", "INFO")

    # Call post_instagram function
    result = post_instagram(caption, image_url)

    if result["status"] == "success":
        log_activity("Instagram post published successfully", "SUCCESS")
        return [TextContent(
            type="text",
            text=f"✓ {result['message']}\nURL: {result.get('url', 'N/A')}"
        )]
    else:
        log_activity(f"Failed to publish Instagram post: {result['message']}", "ERROR")
        return [TextContent(
            type="text",
            text=f"✗ {result['message']}"
        )]


async def main():
    """
    Main entry point for the MCP server.
    """
    # Log server startup
    log_activity("Business MCP Server starting", "INFO")

    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        log_activity("Business MCP Server running on stdio", "INFO")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_activity("Business MCP Server stopped by user", "INFO")
    except Exception as e:
        log_activity(f"Business MCP Server error: {e}", "ERROR")
        sys.exit(1)
