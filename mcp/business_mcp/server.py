"""
Business MCP Server - Gold Tier AI Employee

This MCP server exposes business automation actions as tools:
- send_email: Send emails via SMTP
- post_linkedin: Post content to LinkedIn
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
except ImportError as e:
    print(f"[ERROR] Failed to import business scripts: {e}")
    print("Ensure scripts/send_email.py and scripts/post_linkedin.py exist")
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
