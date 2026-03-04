#!/usr/bin/env python3
"""
Social Summary Skill - Validation Test Suite

Tests all core functionality of the Social Summary system.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add skill directory to path
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from social_summary import (
    log_social_post,
    get_post_count,
    get_recent_posts,
    generate_summary,
    SOCIAL_LOG,
    REPORTS_DIR
)


class TestSocialSummary:
    """Test suite for Social Summary functionality."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests_run = 0
        self.backup_file = None

    def setup(self):
        """Set up test environment."""
        print("\n" + "="*60)
        print("SOCIAL SUMMARY VALIDATION TEST SUITE")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Backup existing Social_Log.md if it exists
        if SOCIAL_LOG.exists():
            self.backup_file = SOCIAL_LOG.parent / "Social_Log_backup.md"
            shutil.copy(str(SOCIAL_LOG), str(self.backup_file))
            print(f"[INFO] Backed up existing Social_Log.md\n")

        # Create fresh log for testing
        if SOCIAL_LOG.exists():
            SOCIAL_LOG.unlink()

    def teardown(self):
        """Clean up test environment."""
        # Restore backup if it exists
        if self.backup_file and self.backup_file.exists():
            if SOCIAL_LOG.exists():
                SOCIAL_LOG.unlink()
            shutil.move(str(self.backup_file), str(SOCIAL_LOG))
            print(f"\n[INFO] Restored original Social_Log.md")

        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        if self.tests_run > 0:
            print(f"Success Rate: {(self.passed/self.tests_run*100):.1f}%")
        print("="*60 + "\n")

    def assert_true(self, condition, test_name):
        """Assert that condition is true."""
        self.tests_run += 1
        if condition:
            print(f"[PASS] {test_name}")
            self.passed += 1
            return True
        else:
            print(f"[FAIL] {test_name}")
            self.failed += 1
            return False

    def assert_equal(self, actual, expected, test_name):
        """Assert that actual equals expected."""
        self.tests_run += 1
        if actual == expected:
            print(f"[PASS] {test_name}")
            self.passed += 1
            return True
        else:
            print(f"[FAIL] {test_name}")
            print(f"  Expected: {expected}")
            print(f"  Actual: {actual}")
            self.failed += 1
            return False

    def test_directory_structure(self):
        """Test that required directories exist."""
        print("\n[TEST] Directory Structure")
        print("-" * 60)

        self.assert_true(REPORTS_DIR.exists(), "Reports directory exists")

    def test_log_initialization(self):
        """Test Social_Log.md initialization."""
        print("\n[TEST] Log Initialization")
        print("-" * 60)

        # Log should be created on first post
        success = log_social_post("LinkedIn", "Test initialization post")

        self.assert_true(success, "First post logged successfully")
        self.assert_true(SOCIAL_LOG.exists(), "Social_Log.md created")

        # Verify header content
        with open(SOCIAL_LOG, "r", encoding="utf-8") as f:
            content = f.read()

        self.assert_true("Social Media Activity Log" in content, "Log has header")
        self.assert_true("LinkedIn" in content, "Log contains platform name")

    def test_log_linkedin_post(self):
        """Test logging a LinkedIn post."""
        print("\n[TEST] Log LinkedIn Post")
        print("-" * 60)

        success = log_social_post(
            platform="LinkedIn",
            content="Test LinkedIn post content",
            post_url="https://linkedin.com/posts/123",
            metadata={"likes": 0, "comments": 0}
        )

        self.assert_true(success, "LinkedIn post logged")

        # Verify content
        with open(SOCIAL_LOG, "r", encoding="utf-8") as f:
            content = f.read()

        self.assert_true("LinkedIn Post" in content, "Post header present")
        self.assert_true("Test LinkedIn post content" in content, "Post content present")
        self.assert_true("https://linkedin.com/posts/123" in content, "Post URL present")

    def test_log_twitter_post(self):
        """Test logging a Twitter/X post."""
        print("\n[TEST] Log Twitter/X Post")
        print("-" * 60)

        success = log_social_post(
            platform="X",
            content="Test Twitter post #test",
            post_url="https://x.com/user/status/123"
        )

        self.assert_true(success, "X post logged")

        with open(SOCIAL_LOG, "r", encoding="utf-8") as f:
            content = f.read()

        self.assert_true("X Post" in content, "X post header present")

    def test_log_facebook_post(self):
        """Test logging a Facebook post."""
        print("\n[TEST] Log Facebook Post")
        print("-" * 60)

        success = log_social_post(
            platform="Facebook",
            content="Test Facebook post",
            post_url="https://facebook.com/posts/123"
        )

        self.assert_true(success, "Facebook post logged")

    def test_log_instagram_post(self):
        """Test logging an Instagram post."""
        print("\n[TEST] Log Instagram Post")
        print("-" * 60)

        success = log_social_post(
            platform="Instagram",
            content="Test Instagram post #photo",
            post_url="https://instagram.com/p/123"
        )

        self.assert_true(success, "Instagram post logged")

    def test_get_post_count(self):
        """Test getting post counts."""
        print("\n[TEST] Get Post Count")
        print("-" * 60)

        # Clear log
        if SOCIAL_LOG.exists():
            SOCIAL_LOG.unlink()

        # Log posts to different platforms
        log_social_post("LinkedIn", "Post 1")
        log_social_post("LinkedIn", "Post 2")
        log_social_post("X", "Post 3")
        log_social_post("Facebook", "Post 4")

        # Test total count
        total = get_post_count()
        self.assert_equal(total, 4, "Total post count is 4")

        # Test platform-specific counts
        linkedin_count = get_post_count(platform="LinkedIn")
        self.assert_equal(linkedin_count, 2, "LinkedIn post count is 2")

        twitter_count = get_post_count(platform="X")
        self.assert_equal(twitter_count, 1, "X post count is 1")

        facebook_count = get_post_count(platform="Facebook")
        self.assert_equal(facebook_count, 1, "Facebook post count is 1")

    def test_get_recent_posts(self):
        """Test getting recent posts."""
        print("\n[TEST] Get Recent Posts")
        print("-" * 60)

        # Clear log
        if SOCIAL_LOG.exists():
            SOCIAL_LOG.unlink()

        # Log test posts
        log_social_post("LinkedIn", "Recent post 1")
        log_social_post("X", "Recent post 2")
        log_social_post("Facebook", "Recent post 3")

        # Get all recent posts
        recent = get_recent_posts(limit=10)
        self.assert_equal(len(recent), 3, "Retrieved 3 recent posts")

        # Test limit
        recent_limited = get_recent_posts(limit=2)
        self.assert_equal(len(recent_limited), 2, "Limit works correctly")

        # Test platform filter
        linkedin_posts = get_recent_posts(limit=10, platform="LinkedIn")
        self.assert_equal(len(linkedin_posts), 1, "Platform filter works")
        self.assert_equal(linkedin_posts[0]['platform'], "LinkedIn", "Correct platform returned")

    def test_generate_summary(self):
        """Test generating summary statistics."""
        print("\n[TEST] Generate Summary")
        print("-" * 60)

        # Clear log
        if SOCIAL_LOG.exists():
            SOCIAL_LOG.unlink()

        # Log posts
        log_social_post("LinkedIn", "Summary test 1")
        log_social_post("LinkedIn", "Summary test 2")
        log_social_post("X", "Summary test 3")

        # Generate summary
        summary = generate_summary(days=7)

        self.assert_equal(summary['total_posts'], 3, "Summary total is 3")
        self.assert_equal(summary['by_platform']['LinkedIn'], 2, "LinkedIn count in summary is 2")
        self.assert_equal(summary['by_platform']['X'], 1, "X count in summary is 1")

    def test_long_content_truncation(self):
        """Test that long content is truncated."""
        print("\n[TEST] Long Content Truncation")
        print("-" * 60)

        # Create long content (300 chars)
        long_content = "A" * 300

        success = log_social_post("LinkedIn", long_content)
        self.assert_true(success, "Long content logged")

        # Verify truncation in log
        with open(SOCIAL_LOG, "r", encoding="utf-8") as f:
            content = f.read()

        # Should contain truncated version (200 chars + "...")
        self.assert_true("..." in content, "Content truncated with ellipsis")

    def test_metadata_logging(self):
        """Test that metadata is logged correctly."""
        print("\n[TEST] Metadata Logging")
        print("-" * 60)

        success = log_social_post(
            platform="LinkedIn",
            content="Metadata test",
            metadata={
                "likes": 10,
                "comments": 5,
                "shares": 2
            }
        )

        self.assert_true(success, "Post with metadata logged")

        with open(SOCIAL_LOG, "r", encoding="utf-8") as f:
            content = f.read()

        self.assert_true("Likes: 10" in content, "Likes metadata present")
        self.assert_true("Comments: 5" in content, "Comments metadata present")
        self.assert_true("Shares: 2" in content, "Shares metadata present")

    def test_empty_log_handling(self):
        """Test handling of empty/non-existent log."""
        print("\n[TEST] Empty Log Handling")
        print("-" * 60)

        # Remove log
        if SOCIAL_LOG.exists():
            SOCIAL_LOG.unlink()

        # Test functions with empty log
        count = get_post_count()
        self.assert_equal(count, 0, "Empty log returns 0 count")

        recent = get_recent_posts()
        self.assert_equal(len(recent), 0, "Empty log returns empty list")

        summary = generate_summary()
        self.assert_equal(summary['total_posts'], 0, "Empty log returns 0 in summary")

    def run_all_tests(self):
        """Run all tests."""
        self.setup()

        try:
            self.test_directory_structure()
            self.test_log_initialization()
            self.test_log_linkedin_post()
            self.test_log_twitter_post()
            self.test_log_facebook_post()
            self.test_log_instagram_post()
            self.test_get_post_count()
            self.test_get_recent_posts()
            self.test_generate_summary()
            self.test_long_content_truncation()
            self.test_metadata_logging()
            self.test_empty_log_handling()
        except Exception as e:
            print(f"\n[ERROR] Test suite failed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.teardown()

        return self.failed == 0


def main():
    """Main entry point."""
    test_suite = TestSocialSummary()
    success = test_suite.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
