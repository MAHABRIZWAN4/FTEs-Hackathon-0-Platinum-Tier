#!/usr/bin/env python3
"""
Personal Task Handler - Gold Tier AI Employee

Manages personal tasks, reminders, and to-dos in the Personal domain.

Features:
- Create and manage personal tasks
- Set reminders and due dates
- Priority levels (low, medium, high)
- Task completion tracking
- Integration with scheduler
- Plan workflow integration
- Comprehensive logging

Usage:
    from personal_tasks import create_task, list_tasks, complete_task

    # Create a task
    create_task(
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority="medium",
        due_date="2026-03-05"
    )

    # List tasks
    tasks = list_tasks(status="pending")

    # Complete a task
    complete_task(task_id="task_123")
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
PERSONAL_DIR = Path(os.getenv("PERSONAL_DIR", "AI_Employee_Vault/Personal"))
LOGS_DIR = Path(os.getenv("LOGS_DIR", "logs"))
ACTIONS_LOG = LOGS_DIR / "actions.log"

# Task files
TASKS_FILE = PERSONAL_DIR / "tasks.json"
REMINDERS_FILE = PERSONAL_DIR / "reminders.json"
COMPLETED_FILE = PERSONAL_DIR / "completed.json"

# Ensure directories exist
PERSONAL_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log_action(message: str, level: str = "INFO"):
    """
    Log an action to logs/actions.log.

    Args:
        message (str): Log message
        level (str): Log level (INFO, ERROR, WARNING, SUCCESS)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [PERSONAL_TASKS] {message}\n"

    try:
        with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[{level}] {message}")
    except Exception as e:
        print(f"[ERROR] Failed to write to log: {e}")


def load_tasks() -> Dict:
    """
    Load tasks from tasks.json.

    Returns:
        dict: Tasks data structure
    """
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_action(f"Failed to load tasks: {str(e)}", "ERROR")
            return {"tasks": []}
    return {"tasks": []}


def save_tasks(tasks_data: Dict):
    """
    Save tasks to tasks.json.

    Args:
        tasks_data (dict): Tasks data structure
    """
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log_action(f"Failed to save tasks: {str(e)}", "ERROR")


def load_completed() -> Dict:
    """
    Load completed tasks from completed.json.

    Returns:
        dict: Completed tasks data structure
    """
    if COMPLETED_FILE.exists():
        try:
            with open(COMPLETED_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_action(f"Failed to load completed tasks: {str(e)}", "ERROR")
            return {"completed": []}
    return {"completed": []}


def save_completed(completed_data: Dict):
    """
    Save completed tasks to completed.json.

    Args:
        completed_data (dict): Completed tasks data structure
    """
    try:
        with open(COMPLETED_FILE, "w", encoding="utf-8") as f:
            json.dump(completed_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log_action(f"Failed to save completed tasks: {str(e)}", "ERROR")


def generate_task_id() -> str:
    """
    Generate a unique task ID.

    Returns:
        str: Task ID in format task_YYYYMMDD_HHMMSS
    """
    return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    reminder: Optional[str] = None
) -> Dict:
    """
    Create a new personal task.

    Args:
        title (str): Task title
        description (str): Task description
        priority (str): Priority level (low, medium, high)
        due_date (str, optional): Due date in YYYY-MM-DD format
        tags (list, optional): List of tags
        reminder (str, optional): Reminder date in YYYY-MM-DD format

    Returns:
        dict: Created task data

    Example:
        create_task(
            title="Buy groceries",
            description="Milk, eggs, bread",
            priority="medium",
            due_date="2026-03-05",
            tags=["shopping", "personal"]
        )
    """
    try:
        # Validate priority
        if priority not in ["low", "medium", "high"]:
            log_action(f"Invalid priority '{priority}', using 'medium'", "WARNING")
            priority = "medium"

        # Generate task ID
        task_id = generate_task_id()

        # Create task object
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "due_date": due_date,
            "tags": tags or [],
            "reminder": reminder
        }

        # Load existing tasks
        tasks_data = load_tasks()

        # Add new task
        tasks_data["tasks"].append(task)

        # Save tasks
        save_tasks(tasks_data)

        log_action(f"Created task: {title} (ID: {task_id})", "SUCCESS")

        return {
            "status": "success",
            "task_id": task_id,
            "task": task,
            "message": f"Task created successfully: {title}"
        }

    except Exception as e:
        log_action(f"Failed to create task: {str(e)}", "ERROR")
        return {
            "status": "error",
            "message": f"Failed to create task: {str(e)}"
        }


def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    due_soon: bool = False
) -> List[Dict]:
    """
    List personal tasks with optional filtering.

    Args:
        status (str, optional): Filter by status (pending, in_progress, completed)
        priority (str, optional): Filter by priority (low, medium, high)
        tag (str, optional): Filter by tag
        due_soon (bool): Show only tasks due within 7 days

    Returns:
        list: List of tasks matching filters

    Example:
        # Get all pending tasks
        tasks = list_tasks(status="pending")

        # Get high priority tasks
        tasks = list_tasks(priority="high")

        # Get tasks due soon
        tasks = list_tasks(due_soon=True)
    """
    try:
        tasks_data = load_tasks()
        tasks = tasks_data.get("tasks", [])

        # Apply filters
        filtered_tasks = []

        for task in tasks:
            # Status filter
            if status and task.get("status") != status:
                continue

            # Priority filter
            if priority and task.get("priority") != priority:
                continue

            # Tag filter
            if tag and tag not in task.get("tags", []):
                continue

            # Due soon filter
            if due_soon:
                due_date = task.get("due_date")
                if due_date:
                    try:
                        due = datetime.fromisoformat(due_date)
                        now = datetime.now()
                        days_until_due = (due - now).days

                        if days_until_due > 7 or days_until_due < 0:
                            continue
                    except:
                        continue
                else:
                    continue

            filtered_tasks.append(task)

        return filtered_tasks

    except Exception as e:
        log_action(f"Failed to list tasks: {str(e)}", "ERROR")
        return []


def get_task(task_id: str) -> Optional[Dict]:
    """
    Get a specific task by ID.

    Args:
        task_id (str): Task ID

    Returns:
        dict: Task data or None if not found
    """
    try:
        tasks_data = load_tasks()
        tasks = tasks_data.get("tasks", [])

        for task in tasks:
            if task.get("id") == task_id:
                return task

        return None

    except Exception as e:
        log_action(f"Failed to get task: {str(e)}", "ERROR")
        return None


def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict:
    """
    Update an existing task.

    Args:
        task_id (str): Task ID
        title (str, optional): New title
        description (str, optional): New description
        priority (str, optional): New priority
        status (str, optional): New status
        due_date (str, optional): New due date
        tags (list, optional): New tags

    Returns:
        dict: Update result
    """
    try:
        tasks_data = load_tasks()
        tasks = tasks_data.get("tasks", [])

        # Find task
        task_found = False
        for task in tasks:
            if task.get("id") == task_id:
                task_found = True

                # Update fields
                if title is not None:
                    task["title"] = title
                if description is not None:
                    task["description"] = description
                if priority is not None:
                    task["priority"] = priority
                if status is not None:
                    task["status"] = status
                if due_date is not None:
                    task["due_date"] = due_date
                if tags is not None:
                    task["tags"] = tags

                task["updated_at"] = datetime.now().isoformat()
                break

        if not task_found:
            return {
                "status": "error",
                "message": f"Task not found: {task_id}"
            }

        # Save tasks
        save_tasks(tasks_data)

        log_action(f"Updated task: {task_id}", "SUCCESS")

        return {
            "status": "success",
            "task_id": task_id,
            "message": "Task updated successfully"
        }

    except Exception as e:
        log_action(f"Failed to update task: {str(e)}", "ERROR")
        return {
            "status": "error",
            "message": f"Failed to update task: {str(e)}"
        }


def complete_task(task_id: str, notes: Optional[str] = None) -> Dict:
    """
    Mark a task as completed.

    Args:
        task_id (str): Task ID
        notes (str, optional): Completion notes

    Returns:
        dict: Completion result
    """
    try:
        tasks_data = load_tasks()
        tasks = tasks_data.get("tasks", [])

        # Find and remove task
        task_to_complete = None
        for i, task in enumerate(tasks):
            if task.get("id") == task_id:
                task_to_complete = tasks.pop(i)
                break

        if not task_to_complete:
            return {
                "status": "error",
                "message": f"Task not found: {task_id}"
            }

        # Mark as completed
        task_to_complete["status"] = "completed"
        task_to_complete["completed_at"] = datetime.now().isoformat()
        if notes:
            task_to_complete["completion_notes"] = notes

        # Save updated tasks
        save_tasks(tasks_data)

        # Add to completed tasks
        completed_data = load_completed()
        completed_data["completed"].append(task_to_complete)
        save_completed(completed_data)

        log_action(f"Completed task: {task_to_complete['title']} (ID: {task_id})", "SUCCESS")

        return {
            "status": "success",
            "task_id": task_id,
            "message": f"Task completed: {task_to_complete['title']}"
        }

    except Exception as e:
        log_action(f"Failed to complete task: {str(e)}", "ERROR")
        return {
            "status": "error",
            "message": f"Failed to complete task: {str(e)}"
        }


def delete_task(task_id: str) -> Dict:
    """
    Delete a task permanently.

    Args:
        task_id (str): Task ID

    Returns:
        dict: Deletion result
    """
    try:
        tasks_data = load_tasks()
        tasks = tasks_data.get("tasks", [])

        # Find and remove task
        task_found = False
        for i, task in enumerate(tasks):
            if task.get("id") == task_id:
                deleted_task = tasks.pop(i)
                task_found = True
                break

        if not task_found:
            return {
                "status": "error",
                "message": f"Task not found: {task_id}"
            }

        # Save tasks
        save_tasks(tasks_data)

        log_action(f"Deleted task: {deleted_task['title']} (ID: {task_id})", "SUCCESS")

        return {
            "status": "success",
            "task_id": task_id,
            "message": f"Task deleted: {deleted_task['title']}"
        }

    except Exception as e:
        log_action(f"Failed to delete task: {str(e)}", "ERROR")
        return {
            "status": "error",
            "message": f"Failed to delete task: {str(e)}"
        }


def get_statistics() -> Dict:
    """
    Get task statistics.

    Returns:
        dict: Statistics including counts by status, priority, etc.
    """
    try:
        tasks_data = load_tasks()
        completed_data = load_completed()

        tasks = tasks_data.get("tasks", [])
        completed = completed_data.get("completed", [])

        # Count by status
        pending = sum(1 for t in tasks if t.get("status") == "pending")
        in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")

        # Count by priority
        high_priority = sum(1 for t in tasks if t.get("priority") == "high")
        medium_priority = sum(1 for t in tasks if t.get("priority") == "medium")
        low_priority = sum(1 for t in tasks if t.get("priority") == "low")

        # Count overdue
        overdue = 0
        for task in tasks:
            due_date = task.get("due_date")
            if due_date:
                try:
                    due = datetime.fromisoformat(due_date)
                    if due < datetime.now():
                        overdue += 1
                except:
                    pass

        return {
            "total_active": len(tasks),
            "total_completed": len(completed),
            "pending": pending,
            "in_progress": in_progress,
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "overdue": overdue
        }

    except Exception as e:
        log_action(f"Failed to get statistics: {str(e)}", "ERROR")
        return {}


def check_reminders() -> List[Dict]:
    """
    Check for tasks with reminders due today.

    Returns:
        list: Tasks with reminders due today
    """
    try:
        tasks_data = load_tasks()
        tasks = tasks_data.get("tasks", [])

        today = datetime.now().date().isoformat()
        reminders_due = []

        for task in tasks:
            reminder = task.get("reminder")
            if reminder and reminder == today:
                reminders_due.append(task)

        if reminders_due:
            log_action(f"Found {len(reminders_due)} reminders due today", "INFO")

        return reminders_due

    except Exception as e:
        log_action(f"Failed to check reminders: {str(e)}", "ERROR")
        return []


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Personal Task Handler - Manage personal tasks")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create task
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("title", help="Task title")
    create_parser.add_argument("--description", default="", help="Task description")
    create_parser.add_argument("--priority", default="medium", choices=["low", "medium", "high"], help="Priority level")
    create_parser.add_argument("--due-date", help="Due date (YYYY-MM-DD)")
    create_parser.add_argument("--tags", nargs="+", help="Tags")

    # List tasks
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", choices=["pending", "in_progress", "completed"], help="Filter by status")
    list_parser.add_argument("--priority", choices=["low", "medium", "high"], help="Filter by priority")
    list_parser.add_argument("--due-soon", action="store_true", help="Show tasks due within 7 days")

    # Complete task
    complete_parser = subparsers.add_parser("complete", help="Complete a task")
    complete_parser.add_argument("task_id", help="Task ID")
    complete_parser.add_argument("--notes", help="Completion notes")

    # Delete task
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", help="Task ID")

    # Statistics
    subparsers.add_parser("stats", help="Show task statistics")

    # Check reminders
    subparsers.add_parser("reminders", help="Check reminders due today")

    args = parser.parse_args()

    if args.command == "create":
        result = create_task(
            title=args.title,
            description=args.description,
            priority=args.priority,
            due_date=args.due_date,
            tags=args.tags
        )
        print(json.dumps(result, indent=2))

    elif args.command == "list":
        tasks = list_tasks(
            status=args.status,
            priority=args.priority,
            due_soon=args.due_soon
        )
        print(f"\nFound {len(tasks)} tasks:\n")
        for task in tasks:
            print(f"[{task['id']}] {task['title']}")
            print(f"  Priority: {task['priority']} | Status: {task['status']}")
            if task.get('due_date'):
                print(f"  Due: {task['due_date']}")
            print()

    elif args.command == "complete":
        result = complete_task(args.task_id, args.notes)
        print(json.dumps(result, indent=2))

    elif args.command == "delete":
        result = delete_task(args.task_id)
        print(json.dumps(result, indent=2))

    elif args.command == "stats":
        stats = get_statistics()
        print("\nTask Statistics:")
        print("="*40)
        print(f"Total Active: {stats.get('total_active', 0)}")
        print(f"Total Completed: {stats.get('total_completed', 0)}")
        print(f"\nBy Status:")
        print(f"  Pending: {stats.get('pending', 0)}")
        print(f"  In Progress: {stats.get('in_progress', 0)}")
        print(f"\nBy Priority:")
        print(f"  High: {stats.get('high_priority', 0)}")
        print(f"  Medium: {stats.get('medium_priority', 0)}")
        print(f"  Low: {stats.get('low_priority', 0)}")
        print(f"\nOverdue: {stats.get('overdue', 0)}")
        print("="*40 + "\n")

    elif args.command == "reminders":
        reminders = check_reminders()
        if reminders:
            print(f"\n{len(reminders)} reminders due today:\n")
            for task in reminders:
                print(f"[{task['id']}] {task['title']}")
                print(f"  {task.get('description', '')}\n")
        else:
            print("\nNo reminders due today.\n")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
