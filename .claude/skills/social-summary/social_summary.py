#!/usr/bin/env python3
"""
Social Summary Skill - Gold Tier AI Employee

Logs all social media posts to a centralized Social_Log.md file.

Tracks posts across:
- LinkedIn
- Facebook
- X (Twitter)
- Instagram

Usage:
    from social_summary import log_social_post

    log_social_post(
        platform="LinkedIn",
        content="Just published a new article...",
        post_url="https://linkedin.com/posts/...",
        metadata={"likes": 0, "comments": 0}
    )
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
REPORTS_DIR = VAULT_DIR / "Reports"
SOCIAL_LOG = REPORTS_DIR / "Social_Log.md"
LOGS_DIR = Path("logs")
ACTIONS_LOG = LOGS_DIR / "actions.log"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log_action(message: str, level: str = "INFO"):
    """Log an action to logs/actions.log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [SOCIAL_SUMMARY] {message}\n"

    try:
        with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[ERROR] Failed to write to log: {e}")


def initialize_social_log():
    """Initialize Social_Log.md if it doesn't exist."""
    if not SOCIAL_LOG.exists():
        header = """# Social Media Activity Log

This file tracks all social media posts across platforms.

**Platforms Tracked:**
- LinkedIn
- Facebook
- X (Twitter)
- Instagram

---

"""
        with open(SOCIAL_LOG, "w", encoding="utf-8") as f:
            f.write(header)
        log_action("Initialized Social_Log.md", "INFO")


def log_social_post(
    platform: str,
    content: str,
    post_url: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> bool:
    """
    Log a social media post to Social_Log.md.

    Args:
        platform (str): Platform name (LinkedIn, Facebook, X, Instagram)
        content (str): Post content/text
        post_url (str, optional): URL to the post
        metadata (dict, optional): Additional metadata (likes, comments, etc.)

    Returns:
        bool: True if logged successfully

    Example:
        log_social_post(
            platform="LinkedIn",
            content="Just published a new article about AI...",
            post_url="https://linkedin.com/posts/123",
            metadata={"likes": 0, "comments": 0}
        )
    """
    try:
        # Initialize log if needed
        initialize_social_log()

        # Prepare entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_only = datetime.now().strftime("%Y-%m-%d")

        # Truncate content if too long
        display_content = content[:200] + "..." if len(content) > 200 else content

        # Build entry
        entry = f"\n## {platform} Post - {date_only}\n\n"
        entry += f"**Posted:** {timestamp}\n\n"
        entry += f"**Content:**\n```\n{display_content}\n```\n\n"

        if post_url:
            entry += f"**URL:** {post_url}\n\n"

        if metadata:
            entry += "**Metadata:**\n"
            for key, value in metadata.items():
                entry += f"- {key.capitalize()}: {value}\n"
            entry += "\n"

        entry += "---\n"

        # Append to log
        with open(SOCIAL_LOG, "a", encoding="utf-8") as f:
            f.write(entry)

        log_action(f"Logged {platform} post to Social_Log.md", "SUCCESS")
        print(f"[SUCCESS] {platform} post logged to Social_Log.md")
        return True

    except Exception as e:
        log_action(f"Failed to log social post: {str(e)}", "ERROR")
        print(f"[ERROR] Failed to log social post: {str(e)}")
        return False


def get_post_count(platform: Optional[str] = None) -> int:
    """
    Get count of posts in Social_Log.md.

    Args:
        platform (str, optional): Filter by platform name

    Returns:
        int: Number of posts
    """
    try:
        if not SOCIAL_LOG.exists():
            return 0

        with open(SOCIAL_LOG, "r", encoding="utf-8") as f:
            content = f.read()

        if platform:
            # Count posts for specific platform
            search_string = f"## {platform} Post"
            return content.count(search_string)
        else:
            # Count all posts (any line starting with "## " and containing "Post")
            lines = content.split("\n")
            return sum(1 for line in lines if line.startswith("## ") and "Post" in line)

    except Exception as e:
        log_action(f"Failed to get post count: {str(e)}", "ERROR")
        return 0


def get_recent_posts(limit: int = 10, platform: Optional[str] = None) -> list:
    """
    Get recent posts from Social_Log.md.

    Args:
        limit (int): Maximum number of posts to return
        platform (str, optional): Filter by platform name

    Returns:
        list: List of post dictionaries
    """
    try:
        if not SOCIAL_LOG.exists():
            return []

        with open(SOCIAL_LOG, "r", encoding="utf-8") as f:
            content = f.read()

        posts = []
        sections = content.split("## ")[1:]  # Skip header

        for section in sections:
            if "Post" not in section:
                continue

            lines = section.split("\n")
            title = lines[0].strip()

            # Extract platform from title
            post_platform = title.split(" Post")[0].strip()

            # Filter by platform if specified
            if platform and post_platform != platform:
                continue

            # Extract date
            date = title.split(" - ")[-1].strip() if " - " in title else "Unknown"

            # Extract content
            content_text = ""
            in_content = False
            for line in lines:
                if line.startswith("**Content:**"):
                    in_content = True
                    continue
                if in_content:
                    if line.startswith("```"):
                        continue
                    if line.startswith("**"):
                        break
                    content_text += line + "\n"

            posts.append({
                "platform": post_platform,
                "date": date,
                "content": content_text.strip()
            })

            if len(posts) >= limit:
                break

        return posts

    except Exception as e:
        log_action(f"Failed to get recent posts: {str(e)}", "ERROR")
        return []


def generate_summary(days: int = 7) -> Dict:
    """
    Generate summary statistics for recent posts.

    Args:
        days (int): Number of days to include in summary

    Returns:
        dict: Summary statistics
    """
    try:
        if not SOCIAL_LOG.exists():
            return {
                "total_posts": 0,
                "by_platform": {},
                "period_days": days
            }

        with open(SOCIAL_LOG, "r", encoding="utf-8") as f:
            content = f.read()

        # Count posts by platform
        platforms = ["LinkedIn", "Facebook", "X", "Instagram"]
        by_platform = {}

        for platform in platforms:
            count = content.count(f"## {platform} Post")
            if count > 0:
                by_platform[platform] = count

        total = sum(by_platform.values())

        return {
            "total_posts": total,
            "by_platform": by_platform,
            "period_days": days
        }

    except Exception as e:
        log_action(f"Failed to generate summary: {str(e)}", "ERROR")
        return {
            "total_posts": 0,
            "by_platform": {},
            "period_days": days
        }


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Social Summary - Log social media posts")
    parser.add_argument("--platform", required=True, help="Platform name (LinkedIn, Facebook, X, Instagram)")
    parser.add_argument("--content", required=True, help="Post content")
    parser.add_argument("--url", help="Post URL")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--recent", type=int, help="Show N recent posts")

    args = parser.parse_args()

    if args.stats:
        summary = generate_summary()
        print("\n" + "="*60)
        print("SOCIAL MEDIA SUMMARY")
        print("="*60)
        print(f"Total Posts: {summary['total_posts']}")
        print("\nBy Platform:")
        for platform, count in summary['by_platform'].items():
            print(f"  {platform}: {count}")
        print("="*60 + "\n")
        return

    if args.recent:
        posts = get_recent_posts(limit=args.recent)
        print("\n" + "="*60)
        print(f"RECENT POSTS ({len(posts)})")
        print("="*60)
        for i, post in enumerate(posts, 1):
            print(f"\n{i}. {post['platform']} - {post['date']}")
            print(f"   {post['content'][:100]}...")
        print("\n" + "="*60 + "\n")
        return

    # Log post
    success = log_social_post(
        platform=args.platform,
        content=args.content,
        post_url=args.url
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
