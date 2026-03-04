#!/usr/bin/env python3
"""
Personal Task Handler - Validation Test Suite

Tests all core functionality of the Personal Task Handler system.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add skill directory to path
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from personal_tasks import (
    create_task,
    list_tasks,
    get_task,
    update_task,
    complete_task,
    delete_task,
    get_statistics,
    check_reminders,
    PERSONAL_DIR,
    TASKS_FILE,
    COMPLETED_FILE
)


class TestPersonalTasks:
    """Test suite for Personal Task Handler functionality."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests_run = 0
        self.backup_dir = None
        self.test_tasks = []

    def setup(self):
        """Set up test environment."""
        print("\n" + "="*60)
        print("PERSONAL TASK HANDLER VALIDATION TEST SUITE")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Backup existing files
        if PERSONAL_DIR.exists():
            self.backup_dir = PERSONAL_DIR.parent / "Personal_backup"
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            shutil.copytree(PERSONAL_DIR, self.backup_dir)
            print(f"[INFO] Backed up existing Personal directory\n")

        # Clean test environment
        if TASKS_FILE.exists():
            TASKS_FILE.unlink()
        if COMPLETED_FILE.exists():
            COMPLETED_FILE.unlink()

    def teardown(self):
        """Clean up test environment."""
        # Clean up test tasks
        for task_id in self.test_tasks:
            try:
                delete_task(task_id)
            except:
                pass

        # Restore backup
        if self.backup_dir and self.backup_dir.exists():
            if PERSONAL_DIR.exists():
                shutil.rmtree(PERSONAL_DIR)
            shutil.copytree(self.backup_dir, PERSONAL_DIR)
            shutil.rmtree(self.backup_dir)
            print(f"\n[INFO] Restored original Personal directory")

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

        self.assert_true(PERSONAL_DIR.exists(), "Personal directory exists")

    def test_create_task_basic(self):
        """Test basic task creation."""
        print("\n[TEST] Create Task - Basic")
        print("-" * 60)

        result = create_task(title="Test Task 1")

        self.assert_equal(result['status'], 'success', "Task creation successful")
        self.assert_true('task_id' in result, "Task ID returned")
        self.assert_true('task' in result, "Task data returned")

        if result['status'] == 'success':
            self.test_tasks.append(result['task_id'])

    def test_create_task_full(self):
        """Test task creation with all parameters."""
        print("\n[TEST] Create Task - Full Parameters")
        print("-" * 60)

        result = create_task(
            title="Test Task 2",
            description="Test description",
            priority="high",
            due_date="2026-03-10",
            tags=["test", "important"],
            reminder="2026-03-09"
        )

        self.assert_equal(result['status'], 'success', "Full task creation successful")

        if result['status'] == 'success':
            task_id = result['task_id']
            self.test_tasks.append(task_id)

            task = result['task']
            self.assert_equal(task['title'], "Test Task 2", "Title correct")
            self.assert_equal(task['description'], "Test description", "Description correct")
            self.assert_equal(task['priority'], "high", "Priority correct")
            self.assert_equal(task['due_date'], "2026-03-10", "Due date correct")
            self.assert_equal(len(task['tags']), 2, "Tags correct")

    def test_create_task_priority_validation(self):
        """Test priority validation."""
        print("\n[TEST] Create Task - Priority Validation")
        print("-" * 60)

        result = create_task(
            title="Test Task 3",
            priority="invalid"
        )

        self.assert_equal(result['status'], 'success', "Task created with invalid priority")

        if result['status'] == 'success':
            task_id = result['task_id']
            self.test_tasks.append(task_id)

            task = result['task']
            self.assert_equal(task['priority'], "medium", "Invalid priority defaults to medium")

    def test_list_tasks_all(self):
        """Test listing all tasks."""
        print("\n[TEST] List Tasks - All")
        print("-" * 60)

        # Create test tasks
        create_task(title="List Test 1", priority="high")
        create_task(title="List Test 2", priority="medium")
        create_task(title="List Test 3", priority="low")

        tasks = list_tasks()
        self.assert_true(len(tasks) >= 3, f"At least 3 tasks listed (found {len(tasks)})")

    def test_list_tasks_filter_status(self):
        """Test filtering tasks by status."""
        print("\n[TEST] List Tasks - Filter by Status")
        print("-" * 60)

        pending = list_tasks(status="pending")
        self.assert_true(len(pending) > 0, "Pending tasks found")

        for task in pending:
            self.assert_equal(task['status'], "pending", f"Task {task['id']} is pending")
            break  # Just check first one

    def test_list_tasks_filter_priority(self):
        """Test filtering tasks by priority."""
        print("\n[TEST] List Tasks - Filter by Priority")
        print("-" * 60)

        # Create high priority task
        result = create_task(title="High Priority Test", priority="high")
        if result['status'] == 'success':
            self.test_tasks.append(result['task_id'])

        high_priority = list_tasks(priority="high")
        self.assert_true(len(high_priority) > 0, "High priority tasks found")

        for task in high_priority:
            self.assert_equal(task['priority'], "high", f"Task {task['id']} is high priority")
            break  # Just check first one

    def test_list_tasks_filter_tag(self):
        """Test filtering tasks by tag."""
        print("\n[TEST] List Tasks - Filter by Tag")
        print("-" * 60)

        # Create task with tag
        result = create_task(
            title="Tagged Test",
            tags=["test-tag", "important"]
        )
        if result['status'] == 'success':
            self.test_tasks.append(result['task_id'])

        tagged = list_tasks(tag="test-tag")
        self.assert_true(len(tagged) > 0, "Tagged tasks found")

    def test_get_task(self):
        """Test getting a specific task."""
        print("\n[TEST] Get Task")
        print("-" * 60)

        # Create task
        result = create_task(title="Get Test Task")
        if result['status'] == 'success':
            task_id = result['task_id']
            self.test_tasks.append(task_id)

            # Get task
            task = get_task(task_id)
            self.assert_true(task is not None, "Task retrieved")
            if task:
                self.assert_equal(task['id'], task_id, "Task ID matches")
                self.assert_equal(task['title'], "Get Test Task", "Task title matches")

        # Test non-existent task
        non_existent = get_task("task_nonexistent")
        self.assert_true(non_existent is None, "Non-existent task returns None")

    def test_update_task(self):
        """Test updating a task."""
        print("\n[TEST] Update Task")
        print("-" * 60)

        # Create task
        result = create_task(title="Update Test Task", priority="low")
        if result['status'] == 'success':
            task_id = result['task_id']
            self.test_tasks.append(task_id)

            # Update task
            update_result = update_task(
                task_id=task_id,
                title="Updated Title",
                priority="high"
            )

            self.assert_equal(update_result['status'], 'success', "Update successful")

            # Verify update
            task = get_task(task_id)
            if task:
                self.assert_equal(task['title'], "Updated Title", "Title updated")
                self.assert_equal(task['priority'], "high", "Priority updated")

    def test_complete_task(self):
        """Test completing a task."""
        print("\n[TEST] Complete Task")
        print("-" * 60)

        # Create task
        result = create_task(title="Complete Test Task")
        if result['status'] == 'success':
            task_id = result['task_id']

            # Complete task
            complete_result = complete_task(task_id, notes="Test completion")

            self.assert_equal(complete_result['status'], 'success', "Completion successful")

            # Verify task moved to completed
            task = get_task(task_id)
            self.assert_true(task is None, "Task removed from active tasks")

            # Verify in completed file
            if COMPLETED_FILE.exists():
                with open(COMPLETED_FILE, 'r', encoding='utf-8') as f:
                    completed_data = json.load(f)
                    completed_ids = [t['id'] for t in completed_data.get('completed', [])]
                    self.assert_true(task_id in completed_ids, "Task in completed file")

    def test_delete_task(self):
        """Test deleting a task."""
        print("\n[TEST] Delete Task")
        print("-" * 60)

        # Create task
        result = create_task(title="Delete Test Task")
        if result['status'] == 'success':
            task_id = result['task_id']

            # Delete task
            delete_result = delete_task(task_id)

            self.assert_equal(delete_result['status'], 'success', "Deletion successful")

            # Verify task deleted
            task = get_task(task_id)
            self.assert_true(task is None, "Task deleted")

    def test_statistics(self):
        """Test statistics generation."""
        print("\n[TEST] Statistics")
        print("-" * 60)

        # Create test tasks
        create_task(title="Stats Test 1", priority="high")
        create_task(title="Stats Test 2", priority="medium")
        create_task(title="Stats Test 3", priority="low")

        stats = get_statistics()

        self.assert_true('total_active' in stats, "total_active in stats")
        self.assert_true('total_completed' in stats, "total_completed in stats")
        self.assert_true('pending' in stats, "pending in stats")
        self.assert_true('high_priority' in stats, "high_priority in stats")
        self.assert_true('medium_priority' in stats, "medium_priority in stats")
        self.assert_true('low_priority' in stats, "low_priority in stats")
        self.assert_true('overdue' in stats, "overdue in stats")

        self.assert_true(stats['total_active'] > 0, "Has active tasks")

    def test_check_reminders(self):
        """Test reminder checking."""
        print("\n[TEST] Check Reminders")
        print("-" * 60)

        # Create task with reminder for today
        today = datetime.now().date().isoformat()
        result = create_task(
            title="Reminder Test Task",
            reminder=today
        )

        if result['status'] == 'success':
            self.test_tasks.append(result['task_id'])

        # Check reminders
        reminders = check_reminders()

        self.assert_true(isinstance(reminders, list), "Reminders is a list")
        self.assert_true(len(reminders) > 0, "Found reminders due today")

    def test_due_soon_filter(self):
        """Test due soon filtering."""
        print("\n[TEST] Due Soon Filter")
        print("-" * 60)

        # Create task due in 3 days
        due_date = (datetime.now() + timedelta(days=3)).date().isoformat()
        result = create_task(
            title="Due Soon Test",
            due_date=due_date
        )

        if result['status'] == 'success':
            self.test_tasks.append(result['task_id'])

        # Get tasks due soon
        due_soon = list_tasks(due_soon=True)

        self.assert_true(len(due_soon) > 0, "Found tasks due soon")

    def test_overdue_detection(self):
        """Test overdue task detection."""
        print("\n[TEST] Overdue Detection")
        print("-" * 60)

        # Create overdue task
        past_date = (datetime.now() - timedelta(days=1)).date().isoformat()
        result = create_task(
            title="Overdue Test",
            due_date=past_date
        )

        if result['status'] == 'success':
            self.test_tasks.append(result['task_id'])

        # Get statistics
        stats = get_statistics()

        self.assert_true(stats['overdue'] > 0, "Detected overdue tasks")

    def test_task_persistence(self):
        """Test that tasks persist to file."""
        print("\n[TEST] Task Persistence")
        print("-" * 60)

        # Create task
        result = create_task(title="Persistence Test")
        if result['status'] == 'success':
            task_id = result['task_id']
            self.test_tasks.append(task_id)

            # Verify file exists
            self.assert_true(TASKS_FILE.exists(), "Tasks file created")

            # Verify task in file
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                task_ids = [t['id'] for t in data.get('tasks', [])]
                self.assert_true(task_id in task_ids, "Task persisted to file")

    def run_all_tests(self):
        """Run all tests."""
        self.setup()

        try:
            self.test_directory_structure()
            self.test_create_task_basic()
            self.test_create_task_full()
            self.test_create_task_priority_validation()
            self.test_list_tasks_all()
            self.test_list_tasks_filter_status()
            self.test_list_tasks_filter_priority()
            self.test_list_tasks_filter_tag()
            self.test_get_task()
            self.test_update_task()
            self.test_complete_task()
            self.test_delete_task()
            self.test_statistics()
            self.test_check_reminders()
            self.test_due_soon_filter()
            self.test_overdue_detection()
            self.test_task_persistence()
        except Exception as e:
            print(f"\n[ERROR] Test suite failed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.teardown()

        return self.failed == 0


def main():
    """Main entry point."""
    test_suite = TestPersonalTasks()
    success = test_suite.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
