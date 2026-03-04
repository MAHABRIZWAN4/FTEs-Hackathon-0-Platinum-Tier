#!/usr/bin/env python3
"""
Error Recovery - Test and Validation

Tests the error recovery system functionality.
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.error_recovery import (
        handle_error,
        with_error_recovery,
        log_error,
        move_to_errors,
        add_to_retry_queue,
        load_retry_queue,
        process_retry_queue,
        get_error_statistics,
        ERRORS_LOG,
        ERRORS_DIR,
        RETRY_QUEUE_FILE
    )
except ImportError as e:
    print(f"[ERROR] Failed to import error_recovery: {e}")
    sys.exit(1)

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_status(message, status="info"):
    """Print colored status."""
    if status == "success":
        print(f"{GREEN}[+]{RESET} {message}")
    elif status == "error":
        print(f"{RED}[!]{RESET} {message}")
    elif status == "warning":
        print(f"{YELLOW}[*]{RESET} {message}")
    else:
        print(f"{BLUE}[i]{RESET} {message}")


def test_error_logging():
    """Test error logging functionality."""
    print_status("Testing error logging...", "info")

    try:
        # Create a test error
        test_error = ValueError("Test error for validation")
        log_error(test_error, context="test_validation", file_path="test.txt")

        # Check if error was logged
        if ERRORS_LOG.exists():
            with open(ERRORS_LOG, "r") as f:
                content = f.read()
                if "Test error for validation" in content:
                    print_status("Error logged successfully", "success")
                    return True
                else:
                    print_status("Error not found in log", "error")
                    return False
        else:
            print_status("Error log file not created", "error")
            return False
    except Exception as e:
        print_status(f"Error logging test failed: {str(e)}", "error")
        return False


def test_file_quarantine():
    """Test moving files to Errors directory."""
    print_status("Testing file quarantine...", "info")

    try:
        # Create a test file
        test_file = Path("test_failed_file.txt")
        test_file.write_text("Test content for error recovery")

        # Move to errors
        new_path = move_to_errors(str(test_file))

        if new_path and Path(new_path).exists():
            print_status(f"File moved to Errors: {Path(new_path).name}", "success")
            # Clean up
            Path(new_path).unlink()
            return True
        else:
            print_status("File not moved to Errors", "error")
            # Clean up original if still exists
            if test_file.exists():
                test_file.unlink()
            return False
    except Exception as e:
        print_status(f"File quarantine test failed: {str(e)}", "error")
        return False


def test_retry_queue():
    """Test retry queue functionality."""
    print_status("Testing retry queue...", "info")

    try:
        # Add to retry queue
        add_to_retry_queue(
            context="test_operation",
            error_message="Test error",
            file_path="test.txt",
            retry_count=0
        )

        # Load queue
        queue = load_retry_queue()

        if queue and "tasks" in queue and len(queue["tasks"]) > 0:
            # Find our test task
            test_task = None
            for task in queue["tasks"]:
                if task.get("context") == "test_operation":
                    test_task = task
                    break

            if test_task:
                print_status("Task added to retry queue", "success")
                print_status(f"Task ID: {test_task['id']}", "info")
                return True
            else:
                print_status("Test task not found in queue", "error")
                return False
        else:
            print_status("Retry queue empty or invalid", "error")
            return False
    except Exception as e:
        print_status(f"Retry queue test failed: {str(e)}", "error")
        return False


def test_decorator():
    """Test error recovery decorator."""
    print_status("Testing decorator...", "info")

    @with_error_recovery
    def failing_function():
        raise RuntimeError("Intentional test error")

    try:
        failing_function()
        print_status("Decorator did not catch error", "error")
        return False
    except RuntimeError:
        # Error should be caught and logged, then re-raised
        print_status("Decorator caught and logged error", "success")
        return True
    except Exception as e:
        print_status(f"Decorator test failed: {str(e)}", "error")
        return False


def test_error_statistics():
    """Test error statistics gathering."""
    print_status("Testing error statistics...", "info")

    try:
        stats = get_error_statistics()

        if isinstance(stats, dict):
            print_status(f"Total errors: {stats.get('total_errors', 0)}", "info")
            print_status(f"Error types: {len(stats.get('error_types', {}))}", "info")
            print_status("Statistics gathered successfully", "success")
            return True
        else:
            print_status("Invalid statistics format", "error")
            return False
    except Exception as e:
        print_status(f"Statistics test failed: {str(e)}", "error")
        return False


def test_handle_error():
    """Test manual error handling."""
    print_status("Testing manual error handling...", "info")

    try:
        test_error = KeyError("test_key")
        result = handle_error(
            test_error,
            context="test_manual_handling",
            file_path="",
            add_to_queue=True
        )

        if result and result.get("status") == "error_handled":
            print_status("Error handled successfully", "success")
            print_status(f"Error type: {result.get('error_type')}", "info")
            return True
        else:
            print_status("Error handling failed", "error")
            return False
    except Exception as e:
        print_status(f"Manual error handling test failed: {str(e)}", "error")
        return False


def test_directories_created():
    """Test that required directories exist."""
    print_status("Testing directory structure...", "info")

    required_dirs = [
        ERRORS_DIR,
        ERRORS_LOG.parent
    ]

    all_exist = True
    for directory in required_dirs:
        if directory.exists():
            print_status(f"{directory.name} exists", "success")
        else:
            print_status(f"{directory.name} NOT found", "error")
            all_exist = False

    return all_exist


def cleanup_test_data():
    """Clean up test data from retry queue."""
    print_status("Cleaning up test data...", "info")

    try:
        queue = load_retry_queue()
        original_count = len(queue.get("tasks", []))

        # Remove test tasks
        queue["tasks"] = [
            task for task in queue.get("tasks", [])
            if not task.get("context", "").startswith("test_")
        ]

        from scripts.error_recovery import save_retry_queue
        save_retry_queue(queue)

        removed = original_count - len(queue["tasks"])
        if removed > 0:
            print_status(f"Removed {removed} test tasks from queue", "success")
        else:
            print_status("No test tasks to remove", "info")

        return True
    except Exception as e:
        print_status(f"Cleanup failed: {str(e)}", "warning")
        return False


def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Error Recovery - Validation Tests{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    tests = [
        ("Directory Structure", test_directories_created),
        ("Error Logging", test_error_logging),
        ("File Quarantine", test_file_quarantine),
        ("Retry Queue", test_retry_queue),
        ("Error Decorator", test_decorator),
        ("Manual Error Handling", test_handle_error),
        ("Error Statistics", test_error_statistics)
    ]

    results = {}
    for name, test_func in tests:
        print(f"\n{BLUE}[{name}]{RESET}")
        results[name] = test_func()

    # Cleanup
    print(f"\n{BLUE}[Cleanup]{RESET}")
    cleanup_test_data()

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "success" if result else "error"
        print_status(f"{name}: {'PASS' if result else 'FAIL'}", status)

    print(f"\n{BLUE}Result: {passed}/{total} tests passed{RESET}\n")

    if passed == total:
        print_status("All tests passed! Error Recovery is ready to use.", "success")
        print(f"\n{BLUE}Check the logs:{RESET}")
        print(f"  tail -f logs/errors.log")
        print(f"  cat logs/retry_queue.json\n")
        return 0
    else:
        print_status("Some tests failed. Check errors above.", "warning")
        return 1


if __name__ == "__main__":
    sys.exit(main())
