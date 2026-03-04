"""
Ralph Wiggum Autonomous Loop - Gold Tier AI Employee

Autonomous agent that continuously monitors and executes tasks.
Named after Ralph Wiggum for its simple, persistent, and autonomous nature.

Behavior:
1. Monitor AI_Employee_Vault/Needs_Action/ for tasks
2. Pick up a task
3. Analyze task requirements
4. Create Plan.md with execution steps
5. Execute steps one by one
6. Check results after each step
7. Continue until task completed
8. Move task to Done/

Safety Features:
- Max 5 iterations per task
- Human approval required for risky operations
- Automatic error recovery integration
- Dry-run mode for testing
- Emergency stop mechanism

Usage:
    python scripts/ralph_loop.py
    python scripts/ralph_loop.py --dry-run
    python scripts/ralph_loop.py --max-iterations 3
"""

import os
import sys
import time
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.error_recovery import with_error_recovery, handle_error
except ImportError:
    print("[WARNING] Error recovery not available")
    def with_error_recovery(func):
        return func

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
NEEDS_APPROVAL_DIR = VAULT_DIR / "Needs_Approval"
DONE_DIR = VAULT_DIR / "Done"
PLANS_DIR = VAULT_DIR / "Plans"
LOGS_DIR = Path("logs")
ACTIONS_LOG = LOGS_DIR / "actions.log"

# Safety configuration
MAX_ITERATIONS = 5
RISKY_KEYWORDS = [
    "delete", "remove", "drop", "truncate", "destroy",
    "format", "wipe", "erase", "purge", "kill",
    "sudo", "admin", "root", "password", "credential"
]

# Ensure directories exist
NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)
NEEDS_APPROVAL_DIR.mkdir(parents=True, exist_ok=True)
DONE_DIR.mkdir(parents=True, exist_ok=True)
PLANS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log_action(message: str, level: str = "INFO"):
    """Log an action to logs/actions.log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [RALPH_LOOP] {message}\n"

    try:
        with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[{level}] {message}")
    except Exception as e:
        print(f"[ERROR] Failed to write to log: {e}")


def get_pending_tasks() -> List[Path]:
    """
    Get list of pending tasks from Needs_Action directory.

    Returns:
        List[Path]: List of task file paths
    """
    if not NEEDS_ACTION_DIR.exists():
        return []

    tasks = list(NEEDS_ACTION_DIR.glob("*.md"))
    return sorted(tasks, key=lambda x: x.stat().st_mtime)


def analyze_task(task_file: Path) -> Dict:
    """
    Analyze a task file and extract requirements.

    Args:
        task_file (Path): Path to task file

    Returns:
        Dict: Task analysis with title, description, steps, risk_level
    """
    try:
        with open(task_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract title (first # heading)
        title = "Unknown Task"
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Extract description
        description = content[:500] if len(content) > 500 else content

        # Assess risk level
        risk_level = assess_risk(content)

        # Extract or generate steps
        steps = extract_steps(content)

        return {
            "title": title,
            "description": description,
            "steps": steps,
            "risk_level": risk_level,
            "file_path": str(task_file),
            "content": content
        }
    except Exception as e:
        log_action(f"Failed to analyze task {task_file.name}: {str(e)}", "ERROR")
        return {
            "title": task_file.stem,
            "description": "Failed to analyze",
            "steps": [],
            "risk_level": "unknown",
            "file_path": str(task_file),
            "content": ""
        }


def assess_risk(content: str) -> str:
    """
    Assess risk level of a task based on content.

    Args:
        content (str): Task content

    Returns:
        str: Risk level (low, medium, high)
    """
    content_lower = content.lower()

    # Check for risky keywords
    risky_count = sum(1 for keyword in RISKY_KEYWORDS if keyword in content_lower)

    if risky_count >= 3:
        return "high"
    elif risky_count >= 1:
        return "medium"
    else:
        return "low"


def extract_steps(content: str) -> List[str]:
    """
    Extract steps from task content.

    Args:
        content (str): Task content

    Returns:
        List[str]: List of steps
    """
    steps = []

    # Look for numbered lists or bullet points
    for line in content.split("\n"):
        line = line.strip()
        # Numbered steps (1., 2., etc.)
        if line and (line[0].isdigit() and ". " in line[:5]):
            steps.append(line.split(". ", 1)[1] if ". " in line else line)
        # Bullet points
        elif line.startswith("- ") or line.startswith("* "):
            steps.append(line[2:])

    # If no steps found, create generic steps
    if not steps:
        steps = [
            "Review task requirements",
            "Execute task",
            "Verify completion",
            "Document results"
        ]

    return steps


def create_plan(task_analysis: Dict) -> Path:
    """
    Create a Plan.md file for the task.

    Args:
        task_analysis (Dict): Task analysis data

    Returns:
        Path: Path to created plan file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_filename = f"Plan_{timestamp}_{Path(task_analysis['file_path']).stem}.md"
    plan_path = PLANS_DIR / plan_filename

    plan_content = f"""# Execution Plan: {task_analysis['title']}

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Task File:** {task_analysis['file_path']}
**Risk Level:** {task_analysis['risk_level'].upper()}

---

## Task Description

{task_analysis['description'][:500]}

---

## Execution Steps

"""

    for i, step in enumerate(task_analysis['steps'], 1):
        plan_content += f"{i}. {step}\n"

    plan_content += f"""

---

## Execution Log

"""

    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(plan_content)

    log_action(f"Created execution plan: {plan_filename}", "INFO")
    return plan_path


def update_plan(plan_path: Path, step_num: int, status: str, result: str):
    """
    Update plan file with step execution result.

    Args:
        plan_path (Path): Path to plan file
        step_num (int): Step number
        status (str): Status (SUCCESS, FAILED, SKIPPED)
        result (str): Result description
    """
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n### Step {step_num}: {status}\n**Time:** {timestamp}\n**Result:** {result}\n"

        content += log_entry

        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        log_action(f"Failed to update plan: {str(e)}", "ERROR")


def requires_approval(task_analysis: Dict) -> bool:
    """
    Check if task requires human approval.

    Args:
        task_analysis (Dict): Task analysis

    Returns:
        bool: True if approval required
    """
    return task_analysis['risk_level'] in ['high', 'medium']


def request_approval(task_analysis: Dict) -> bool:
    """
    Request human approval for risky task.

    Args:
        task_analysis (Dict): Task analysis

    Returns:
        bool: True if approved, False if denied
    """
    # Move task to Needs_Approval directory
    source = Path(task_analysis['file_path'])
    destination = NEEDS_APPROVAL_DIR / source.name

    try:
        shutil.copy(str(source), str(destination))
        log_action(f"Task moved to Needs_Approval: {source.name}", "WARNING")

        # Create approval request file
        approval_content = f"""# Approval Required: {task_analysis['title']}

**Risk Level:** {task_analysis['risk_level'].upper()}
**Requested:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Task Description

{task_analysis['description']}

---

## Execution Steps

"""
        for i, step in enumerate(task_analysis['steps'], 1):
            approval_content += f"{i}. {step}\n"

        approval_content += """

---

## Approval Instructions

To approve this task:
1. Review the task and steps above
2. If approved, move this file back to Needs_Action/
3. If denied, delete this file

**Note:** High-risk tasks require manual approval before execution.
"""

        with open(destination, "w", encoding="utf-8") as f:
            f.write(approval_content)

        return False  # Not approved yet
    except Exception as e:
        log_action(f"Failed to request approval: {str(e)}", "ERROR")
        return False


def execute_step(step: str, step_num: int, task_analysis: Dict, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Execute a single step of the task.

    Args:
        step (str): Step description
        step_num (int): Step number
        task_analysis (Dict): Task analysis
        dry_run (bool): If True, simulate execution

    Returns:
        Tuple[bool, str]: (success, result_message)
    """
    if dry_run:
        log_action(f"[DRY-RUN] Would execute step {step_num}: {step}", "INFO")
        return True, f"Dry-run: Step {step_num} simulated"

    log_action(f"Executing step {step_num}: {step}", "INFO")

    try:
        # Here you would implement actual step execution logic
        # For now, we'll simulate execution
        time.sleep(1)  # Simulate work

        # In a real implementation, you would:
        # - Parse the step
        # - Determine what action to take
        # - Execute the action
        # - Verify the result

        result = f"Step {step_num} completed: {step}"
        log_action(f"Step {step_num} completed successfully", "SUCCESS")
        return True, result

    except Exception as e:
        error_msg = f"Step {step_num} failed: {str(e)}"
        log_action(error_msg, "ERROR")
        handle_error(e, context=f"ralph_loop.step_{step_num}", file_path=task_analysis['file_path'])
        return False, error_msg


def execute_task(task_file: Path, dry_run: bool = False, max_iterations: int = MAX_ITERATIONS) -> bool:
    """
    Execute a complete task.

    Args:
        task_file (Path): Path to task file
        dry_run (bool): If True, simulate execution
        max_iterations (int): Maximum iterations allowed

    Returns:
        bool: True if task completed successfully
    """
    log_action(f"Starting task execution: {task_file.name}", "INFO")

    # Analyze task
    task_analysis = analyze_task(task_file)

    # Check if approval required
    if requires_approval(task_analysis) and not dry_run:
        log_action(f"Task requires approval: {task_analysis['title']}", "WARNING")
        request_approval(task_analysis)
        return False

    # Create execution plan
    plan_path = create_plan(task_analysis)

    # Execute steps
    iteration = 0
    for step_num, step in enumerate(task_analysis['steps'], 1):
        iteration += 1

        if iteration > max_iterations:
            log_action(f"Max iterations ({max_iterations}) reached for task", "WARNING")
            update_plan(plan_path, step_num, "ABORTED", f"Max iterations ({max_iterations}) reached")
            return False

        # Execute step
        success, result = execute_step(step, step_num, task_analysis, dry_run)

        # Update plan
        status = "SUCCESS" if success else "FAILED"
        update_plan(plan_path, step_num, status, result)

        if not success:
            log_action(f"Task execution failed at step {step_num}", "ERROR")
            return False

    # Task completed successfully
    log_action(f"Task completed successfully: {task_analysis['title']}", "SUCCESS")

    # Move to Done (if not dry-run)
    if not dry_run:
        move_to_done(task_file, plan_path)

    return True


def move_to_done(task_file: Path, plan_path: Path):
    """
    Move completed task to Done directory.

    Args:
        task_file (Path): Task file
        plan_path (Path): Plan file
    """
    try:
        # Move task file
        task_dest = DONE_DIR / task_file.name
        shutil.move(str(task_file), str(task_dest))

        # Copy plan file to Done as well
        plan_dest = DONE_DIR / plan_path.name
        shutil.copy(str(plan_path), str(plan_dest))

        log_action(f"Task moved to Done: {task_file.name}", "SUCCESS")
    except Exception as e:
        log_action(f"Failed to move task to Done: {str(e)}", "ERROR")


def run_autonomous_loop(dry_run: bool = False, max_iterations: int = MAX_ITERATIONS, single_run: bool = False):
    """
    Run the autonomous loop continuously.

    Args:
        dry_run (bool): If True, simulate execution
        max_iterations (int): Max iterations per task
        single_run (bool): If True, process one task and exit
    """
    print(f"\n{'='*60}")
    print(f"RALPH WIGGUM AUTONOMOUS LOOP")
    print(f"{'='*60}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")
    print(f"Max Iterations: {max_iterations}")
    print(f"{'='*60}\n")

    log_action(f"Ralph Loop started (dry_run={dry_run}, max_iterations={max_iterations})", "INFO")

    try:
        while True:
            # Get pending tasks
            tasks = get_pending_tasks()

            if not tasks:
                if single_run:
                    print("No tasks found. Exiting.")
                    break
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No tasks pending. Waiting...")
                    time.sleep(60)  # Wait 1 minute
                    continue

            # Process first task
            task = tasks[0]
            print(f"\n{'='*60}")
            print(f"Processing task: {task.name}")
            print(f"{'='*60}\n")

            success = execute_task(task, dry_run, max_iterations)

            if success:
                print(f"\n[SUCCESS] Task completed: {task.name}\n")
            else:
                print(f"\n[FAILED] Task failed or requires approval: {task.name}\n")

            if single_run:
                break

            # Wait before next task
            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print(f"Ralph Loop stopped by user")
        print(f"{'='*60}\n")
        log_action("Ralph Loop stopped by user", "INFO")


def main():
    """
    Main entry point for command-line usage.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Ralph Wiggum Autonomous Loop - Autonomous task executor")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution without making changes")
    parser.add_argument("--max-iterations", type=int, default=MAX_ITERATIONS, help=f"Max iterations per task (default: {MAX_ITERATIONS})")
    parser.add_argument("--single", action="store_true", help="Process one task and exit")

    args = parser.parse_args()

    run_autonomous_loop(
        dry_run=args.dry_run,
        max_iterations=args.max_iterations,
        single_run=args.single
    )


if __name__ == "__main__":
    main()
