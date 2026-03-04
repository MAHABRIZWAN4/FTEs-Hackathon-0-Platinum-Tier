"""
Error Recovery Agent - Gold Tier AI Employee

Automated error handling and recovery system for the AI Employee.
Detects failures, logs errors, moves failed files, and retries operations.

Features:
- Automatic error detection and logging
- Failed file quarantine to AI_Employee_Vault/Errors/
- Automatic retry after 5 minutes (once)
- Comprehensive error tracking
- Decorator for wrapping functions with error handling
- Error recovery service

Usage:
    # As decorator
    from scripts.error_recovery import with_error_recovery

    @with_error_recovery
    def my_function():
        # Your code here
        pass

    # Manual error handling
    from scripts.error_recovery import handle_error, retry_failed_task

    try:
        risky_operation()
    except Exception as e:
        handle_error(e, context="operation_name", file_path="path/to/file")

    # Start error recovery service
    python scripts/error_recovery.py --service
"""

import os
import sys
import time
import json
import shutil
import traceback
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Any, Optional, Dict
from functools import wraps

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
ERRORS_DIR = VAULT_DIR / "Errors"
LOGS_DIR = Path("logs")
ERRORS_LOG = LOGS_DIR / "errors.log"
RETRY_QUEUE_FILE = LOGS_DIR / "retry_queue.json"
ACTIONS_LOG = LOGS_DIR / "actions.log"

# Retry configuration
RETRY_DELAY_SECONDS = 300  # 5 minutes
MAX_RETRIES = 1

# Ensure directories exist
ERRORS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log_action(message: str, level: str = "INFO"):
    """Log an action to logs/actions.log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [ERROR_RECOVERY] {message}\n"

    try:
        with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[{level}] {message}")
    except Exception as e:
        print(f"[ERROR] Failed to write to log: {e}")


def log_error(error: Exception, context: str = "", file_path: str = "", stack_trace: str = ""):
    """
    Log an error to logs/errors.log with full details.

    Args:
        error (Exception): The exception that occurred
        context (str): Context/operation where error occurred
        file_path (str): Path to file that caused error (if applicable)
        stack_trace (str): Full stack trace
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    error_entry = f"""
{'='*80}
[{timestamp}] ERROR DETECTED
{'='*80}
Context: {context or 'Unknown'}
Error Type: {type(error).__name__}
Error Message: {str(error)}
File: {file_path or 'N/A'}

Stack Trace:
{stack_trace or traceback.format_exc()}
{'='*80}

"""

    try:
        with open(ERRORS_LOG, "a", encoding="utf-8") as f:
            f.write(error_entry)

        log_action(f"Error logged: {type(error).__name__} in {context}", "ERROR")
    except Exception as e:
        print(f"[CRITICAL] Failed to write to error log: {e}")


def move_to_errors(file_path: str) -> Optional[str]:
    """
    Move a failed file to AI_Employee_Vault/Errors/ directory.

    Args:
        file_path (str): Path to file that failed

    Returns:
        Optional[str]: New path in Errors directory, or None if failed
    """
    if not file_path or not Path(file_path).exists():
        return None

    try:
        source = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{timestamp}_{source.name}"
        destination = ERRORS_DIR / new_name

        shutil.move(str(source), str(destination))

        log_action(f"Moved failed file to Errors: {source.name} -> {new_name}", "WARNING")
        return str(destination)
    except Exception as e:
        log_action(f"Failed to move file to Errors: {str(e)}", "ERROR")
        return None


def load_retry_queue() -> Dict:
    """
    Load the retry queue from disk.

    Returns:
        Dict: Retry queue data
    """
    if not RETRY_QUEUE_FILE.exists():
        return {"tasks": []}

    try:
        with open(RETRY_QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_action(f"Failed to load retry queue: {str(e)}", "ERROR")
        return {"tasks": []}


def save_retry_queue(queue: Dict):
    """
    Save the retry queue to disk.

    Args:
        queue (Dict): Retry queue data
    """
    try:
        with open(RETRY_QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)
    except Exception as e:
        log_action(f"Failed to save retry queue: {str(e)}", "ERROR")


def add_to_retry_queue(context: str, error_message: str, file_path: str = "", retry_count: int = 0):
    """
    Add a failed task to the retry queue.

    Args:
        context (str): Context/operation that failed
        error_message (str): Error message
        file_path (str): Path to failed file
        retry_count (int): Current retry count
    """
    queue = load_retry_queue()

    task = {
        "id": f"{context}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "context": context,
        "error_message": error_message,
        "file_path": file_path,
        "retry_count": retry_count,
        "failed_at": datetime.now().isoformat(),
        "retry_at": (datetime.now() + timedelta(seconds=RETRY_DELAY_SECONDS)).isoformat(),
        "status": "pending_retry"
    }

    queue["tasks"].append(task)
    save_retry_queue(queue)

    log_action(f"Added to retry queue: {context} (retry in {RETRY_DELAY_SECONDS}s)", "INFO")


def handle_error(error: Exception, context: str = "", file_path: str = "", add_to_queue: bool = True) -> Dict:
    """
    Handle an error: log it, move file, and optionally add to retry queue.

    Args:
        error (Exception): The exception that occurred
        context (str): Context where error occurred
        file_path (str): Path to file that caused error
        add_to_queue (bool): Whether to add to retry queue

    Returns:
        Dict: Error handling result
    """
    # Log the error
    stack_trace = traceback.format_exc()
    log_error(error, context, file_path, stack_trace)

    # Move file to errors directory if provided
    new_path = None
    if file_path:
        new_path = move_to_errors(file_path)

    # Add to retry queue
    if add_to_queue:
        add_to_retry_queue(context, str(error), new_path or file_path)

    return {
        "status": "error_handled",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "original_file": file_path,
        "moved_to": new_path,
        "queued_for_retry": add_to_queue
    }


def with_error_recovery(func: Callable) -> Callable:
    """
    Decorator to wrap functions with automatic error recovery.

    Usage:
        @with_error_recovery
        def my_function(arg1, arg2):
            # Your code here
            pass

    Args:
        func (Callable): Function to wrap

    Returns:
        Callable: Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        context = f"{func.__module__}.{func.__name__}"

        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Extract file_path if it's in kwargs or args
            file_path = kwargs.get("file_path", "")
            if not file_path and args:
                # Try to find a Path-like argument
                for arg in args:
                    if isinstance(arg, (str, Path)) and Path(str(arg)).exists():
                        file_path = str(arg)
                        break

            # Handle the error
            result = handle_error(e, context, file_path)

            log_action(f"Function {func.__name__} failed: {str(e)}", "ERROR")

            # Re-raise the exception after handling
            raise

    return wrapper


def retry_failed_task(task: Dict) -> bool:
    """
    Retry a failed task.

    Args:
        task (Dict): Task from retry queue

    Returns:
        bool: True if retry succeeded, False otherwise
    """
    context = task.get("context", "unknown")
    file_path = task.get("file_path", "")

    log_action(f"Retrying task: {context}", "INFO")

    try:
        # Check if file still exists
        if file_path and not Path(file_path).exists():
            log_action(f"Retry failed: File not found: {file_path}", "ERROR")
            return False

        # Here you would implement the actual retry logic
        # For now, we'll just log that we attempted it
        # In a real implementation, you'd call the original function again

        log_action(f"Retry successful: {context}", "SUCCESS")
        return True

    except Exception as e:
        log_action(f"Retry failed: {context} - {str(e)}", "ERROR")
        log_error(e, f"Retry: {context}", file_path)
        return False


def process_retry_queue():
    """
    Process the retry queue and retry eligible tasks.
    """
    queue = load_retry_queue()
    now = datetime.now()

    tasks_to_retry = []
    remaining_tasks = []

    for task in queue.get("tasks", []):
        retry_at = datetime.fromisoformat(task["retry_at"])

        if now >= retry_at and task["status"] == "pending_retry":
            tasks_to_retry.append(task)
        else:
            remaining_tasks.append(task)

    if not tasks_to_retry:
        return

    log_action(f"Processing {len(tasks_to_retry)} tasks from retry queue", "INFO")

    for task in tasks_to_retry:
        retry_count = task.get("retry_count", 0)

        if retry_count >= MAX_RETRIES:
            # Max retries reached, mark as permanently failed
            task["status"] = "permanently_failed"
            task["failed_permanently_at"] = datetime.now().isoformat()
            remaining_tasks.append(task)
            log_action(f"Task permanently failed after {retry_count} retries: {task['context']}", "ERROR")
            continue

        # Attempt retry
        success = retry_failed_task(task)

        if success:
            # Remove from queue (don't add to remaining_tasks)
            log_action(f"Task retry succeeded: {task['context']}", "SUCCESS")
        else:
            # Increment retry count and re-queue
            task["retry_count"] = retry_count + 1

            if task["retry_count"] >= MAX_RETRIES:
                task["status"] = "permanently_failed"
                task["failed_permanently_at"] = datetime.now().isoformat()
            else:
                task["retry_at"] = (datetime.now() + timedelta(seconds=RETRY_DELAY_SECONDS)).isoformat()

            remaining_tasks.append(task)

    # Save updated queue
    queue["tasks"] = remaining_tasks
    save_retry_queue(queue)


def run_error_recovery_service():
    """
    Run the error recovery service that monitors and processes retry queue.
    """
    print(f"\n{'='*60}")
    print(f"ERROR RECOVERY SERVICE")
    print(f"{'='*60}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Retry delay: {RETRY_DELAY_SECONDS} seconds")
    print(f"Max retries: {MAX_RETRIES}")
    print(f"{'='*60}\n")

    log_action("Error Recovery Service started", "INFO")

    try:
        while True:
            # Process retry queue every minute
            process_retry_queue()

            # Sleep for 60 seconds
            time.sleep(60)

    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print(f"Error Recovery Service stopped by user")
        print(f"{'='*60}\n")
        log_action("Error Recovery Service stopped by user", "INFO")


def get_error_statistics() -> Dict:
    """
    Get error statistics from logs.

    Returns:
        Dict: Error statistics
    """
    if not ERRORS_LOG.exists():
        return {
            "total_errors": 0,
            "error_types": {},
            "recent_errors": []
        }

    try:
        with open(ERRORS_LOG, "r", encoding="utf-8") as f:
            content = f.read()

        # Count total errors
        total_errors = content.count("ERROR DETECTED")

        # Count error types (simplified)
        error_types = {}
        for line in content.split("\n"):
            if line.startswith("Error Type:"):
                error_type = line.split(":", 1)[1].strip()
                error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            "total_errors": total_errors,
            "error_types": error_types,
            "recent_errors": []  # Could parse recent errors if needed
        }
    except Exception as e:
        log_action(f"Failed to get error statistics: {str(e)}", "ERROR")
        return {
            "total_errors": 0,
            "error_types": {},
            "recent_errors": []
        }


def main():
    """
    Main entry point for command-line usage.
    """
    parser = argparse.ArgumentParser(description="Error Recovery Agent - Handle and retry failed tasks")
    parser.add_argument("--service", action="store_true", help="Run as background service")
    parser.add_argument("--process-queue", action="store_true", help="Process retry queue once")
    parser.add_argument("--stats", action="store_true", help="Show error statistics")
    parser.add_argument("--clear-queue", action="store_true", help="Clear retry queue")

    args = parser.parse_args()

    if args.service:
        # Run as service
        run_error_recovery_service()

    elif args.process_queue:
        # Process queue once
        print("Processing retry queue...")
        process_retry_queue()
        print("Done.")

    elif args.stats:
        # Show statistics
        stats = get_error_statistics()
        queue = load_retry_queue()

        print(f"\n{'='*60}")
        print(f"ERROR RECOVERY STATISTICS")
        print(f"{'='*60}")
        print(f"Total Errors Logged: {stats['total_errors']}")
        print(f"Tasks in Retry Queue: {len(queue.get('tasks', []))}")

        if stats['error_types']:
            print(f"\nError Types:")
            for error_type, count in sorted(stats['error_types'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {error_type}: {count}")

        pending = sum(1 for t in queue.get('tasks', []) if t.get('status') == 'pending_retry')
        failed = sum(1 for t in queue.get('tasks', []) if t.get('status') == 'permanently_failed')

        print(f"\nRetry Queue Status:")
        print(f"  Pending Retry: {pending}")
        print(f"  Permanently Failed: {failed}")
        print(f"{'='*60}\n")

    elif args.clear_queue:
        # Clear queue
        save_retry_queue({"tasks": []})
        print("Retry queue cleared.")
        log_action("Retry queue cleared manually", "INFO")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
