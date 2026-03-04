#!/usr/bin/env python3
"""
Ralph Wiggum Autonomous Loop - Validation Test Suite

Tests all core functionality of the Ralph Loop system.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.ralph_loop import (
    get_pending_tasks,
    analyze_task,
    assess_risk,
    extract_steps,
    create_plan,
    requires_approval,
    execute_task,
    VAULT_DIR,
    NEEDS_ACTION_DIR,
    NEEDS_APPROVAL_DIR,
    DONE_DIR,
    PLANS_DIR
)


class TestRalphLoop:
    """Test suite for Ralph Loop functionality."""

    def __init__(self):
        self.test_dir = VAULT_DIR / "Test"
        self.passed = 0
        self.failed = 0
        self.tests_run = 0

    def setup(self):
        """Set up test environment."""
        print("\n" + "="*60)
        print("RALPH LOOP VALIDATION TEST SUITE")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Create test directory
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def teardown(self):
        """Clean up test environment."""
        # Clean up test files
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
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
        """Test that all required directories exist."""
        print("\n[TEST] Directory Structure")
        print("-" * 60)

        self.assert_true(VAULT_DIR.exists(), "AI_Employee_Vault exists")
        self.assert_true(NEEDS_ACTION_DIR.exists(), "Needs_Action directory exists")
        self.assert_true(NEEDS_APPROVAL_DIR.exists(), "Needs_Approval directory exists")
        self.assert_true(DONE_DIR.exists(), "Done directory exists")
        self.assert_true(PLANS_DIR.exists(), "Plans directory exists")

    def test_risk_assessment(self):
        """Test risk assessment functionality."""
        print("\n[TEST] Risk Assessment")
        print("-" * 60)

        # Low risk content
        low_risk = "Update documentation and add new features"
        self.assert_equal(assess_risk(low_risk), "low", "Low risk assessment")

        # Medium risk content (1-2 keywords)
        medium_risk = "Remove old files from the system"
        self.assert_equal(assess_risk(medium_risk), "medium", "Medium risk assessment")

        # High risk content (3+ keywords)
        high_risk = "Delete all files, remove database, and drop tables"
        self.assert_equal(assess_risk(high_risk), "high", "High risk assessment")

    def test_step_extraction(self):
        """Test step extraction from task content."""
        print("\n[TEST] Step Extraction")
        print("-" * 60)

        # Numbered steps
        content_numbered = """
# Test Task

## Steps

1. First step
2. Second step
3. Third step
"""
        steps = extract_steps(content_numbered)
        self.assert_equal(len(steps), 3, "Extract 3 numbered steps")
        self.assert_equal(steps[0], "First step", "First step extracted correctly")

        # Bullet points
        content_bullets = """
# Test Task

## Steps

- First step
- Second step
- Third step
"""
        steps = extract_steps(content_bullets)
        self.assert_equal(len(steps), 3, "Extract 3 bullet point steps")

        # No steps (should generate default)
        content_no_steps = "Just a description with no steps"
        steps = extract_steps(content_no_steps)
        self.assert_true(len(steps) > 0, "Generate default steps when none found")

    def test_task_analysis(self):
        """Test task analysis functionality."""
        print("\n[TEST] Task Analysis")
        print("-" * 60)

        # Create test task file
        test_task = self.test_dir / "test_analysis.md"
        test_content = """# Test Task - Update Documentation

Update the project documentation.

## Steps

1. Review current docs
2. Update outdated sections
3. Commit changes

## Priority

Low
"""
        with open(test_task, "w", encoding="utf-8") as f:
            f.write(test_content)

        # Analyze task
        analysis = analyze_task(test_task)

        self.assert_equal(analysis['title'], "Test Task - Update Documentation", "Task title extracted")
        self.assert_true(len(analysis['steps']) == 3, "3 steps extracted")
        self.assert_equal(analysis['risk_level'], "low", "Risk level assessed as low")
        self.assert_true('file_path' in analysis, "File path included in analysis")

    def test_approval_requirement(self):
        """Test approval requirement logic."""
        print("\n[TEST] Approval Requirement")
        print("-" * 60)

        # Low risk - no approval
        low_risk_analysis = {'risk_level': 'low'}
        self.assert_true(not requires_approval(low_risk_analysis), "Low risk doesn't require approval")

        # Medium risk - requires approval
        medium_risk_analysis = {'risk_level': 'medium'}
        self.assert_true(requires_approval(medium_risk_analysis), "Medium risk requires approval")

        # High risk - requires approval
        high_risk_analysis = {'risk_level': 'high'}
        self.assert_true(requires_approval(high_risk_analysis), "High risk requires approval")

    def test_plan_creation(self):
        """Test execution plan creation."""
        print("\n[TEST] Plan Creation")
        print("-" * 60)

        # Create test analysis
        test_analysis = {
            'title': 'Test Task',
            'description': 'Test description',
            'steps': ['Step 1', 'Step 2', 'Step 3'],
            'risk_level': 'low',
            'file_path': str(self.test_dir / "test.md")
        }

        # Create plan
        plan_path = create_plan(test_analysis)

        self.assert_true(plan_path.exists(), "Plan file created")
        self.assert_true(plan_path.name.startswith("Plan_"), "Plan filename correct format")

        # Verify plan content
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assert_true("Test Task" in content, "Plan contains task title")
        self.assert_true("Step 1" in content, "Plan contains steps")
        self.assert_true("Execution Log" in content, "Plan has execution log section")

    def test_pending_tasks(self):
        """Test pending task retrieval."""
        print("\n[TEST] Pending Tasks")
        print("-" * 60)

        # Count current pending tasks
        initial_count = len(get_pending_tasks())

        # Create test task in Needs_Action
        test_task = NEEDS_ACTION_DIR / "test_pending.md"
        with open(test_task, "w", encoding="utf-8") as f:
            f.write("# Test Task\n\nTest content")

        # Get pending tasks
        tasks = get_pending_tasks()
        new_count = len(tasks)

        self.assert_true(new_count == initial_count + 1, "New task detected in pending tasks")

        # Clean up
        test_task.unlink()

    def test_dry_run_execution(self):
        """Test dry-run task execution."""
        print("\n[TEST] Dry-Run Execution")
        print("-" * 60)

        # Create test task
        test_task = NEEDS_ACTION_DIR / "test_dryrun.md"
        test_content = """# Test Task - Dry Run

Test dry-run execution.

## Steps

1. Step 1
2. Step 2
"""
        with open(test_task, "w", encoding="utf-8") as f:
            f.write(test_content)

        # Execute in dry-run mode
        success = execute_task(test_task, dry_run=True, max_iterations=5)

        self.assert_true(success, "Dry-run execution completed")
        self.assert_true(test_task.exists(), "Task file not moved in dry-run")

        # Clean up
        test_task.unlink()

        # Clean up any plans created
        for plan in PLANS_DIR.glob("Plan_*test_dryrun*.md"):
            plan.unlink()

    def test_max_iterations(self):
        """Test max iterations limit."""
        print("\n[TEST] Max Iterations Limit")
        print("-" * 60)

        # Create task with many steps
        test_task = NEEDS_ACTION_DIR / "test_maxiter.md"
        test_content = """# Test Task - Max Iterations

Test max iterations.

## Steps

1. Step 1
2. Step 2
3. Step 3
4. Step 4
5. Step 5
6. Step 6
7. Step 7
8. Step 8
"""
        with open(test_task, "w", encoding="utf-8") as f:
            f.write(test_content)

        # Execute with low max iterations
        success = execute_task(test_task, dry_run=True, max_iterations=3)

        self.assert_true(not success, "Task stopped at max iterations")

        # Clean up
        test_task.unlink()

        # Clean up any plans created
        for plan in PLANS_DIR.glob("Plan_*test_maxiter*.md"):
            plan.unlink()

    def test_risky_task_approval(self):
        """Test that risky tasks require approval."""
        print("\n[TEST] Risky Task Approval")
        print("-" * 60)

        # Create risky task
        test_task = NEEDS_ACTION_DIR / "test_risky.md"
        test_content = """# Test Task - Risky

Delete all old files and remove database.

## Steps

1. Delete files
2. Drop database
"""
        with open(test_task, "w", encoding="utf-8") as f:
            f.write(test_content)

        # Execute (should move to approval)
        success = execute_task(test_task, dry_run=False, max_iterations=5)

        self.assert_true(not success, "Risky task not auto-executed")

        # Check if moved to approval
        approval_file = NEEDS_APPROVAL_DIR / "test_risky.md"
        self.assert_true(approval_file.exists(), "Risky task moved to Needs_Approval")

        # Clean up
        if test_task.exists():
            test_task.unlink()
        if approval_file.exists():
            approval_file.unlink()

    def run_all_tests(self):
        """Run all tests."""
        self.setup()

        try:
            self.test_directory_structure()
            self.test_risk_assessment()
            self.test_step_extraction()
            self.test_task_analysis()
            self.test_approval_requirement()
            self.test_plan_creation()
            self.test_pending_tasks()
            self.test_dry_run_execution()
            self.test_max_iterations()
            self.test_risky_task_approval()
        except Exception as e:
            print(f"\n[ERROR] Test suite failed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.teardown()

        return self.failed == 0


def main():
    """Main entry point."""
    test_suite = TestRalphLoop()
    success = test_suite.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
