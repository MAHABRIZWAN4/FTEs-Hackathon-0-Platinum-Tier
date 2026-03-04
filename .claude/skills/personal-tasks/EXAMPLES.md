# Personal Task Handler - Examples

## Basic Usage

### Create Tasks

```python
from personal_tasks import create_task

# Simple task
result = create_task(
    title="Buy groceries"
)

# Task with description
result = create_task(
    title="Buy groceries",
    description="Milk, eggs, bread, coffee, bananas"
)

# Task with priority
result = create_task(
    title="Finish project report",
    description="Complete Q1 analysis and recommendations",
    priority="high"
)

# Task with due date
result = create_task(
    title="Doctor appointment",
    description="Annual checkup at 2 PM",
    priority="high",
    due_date="2026-03-10"
)

# Task with tags
result = create_task(
    title="Buy birthday gift",
    description="For Mom's birthday next week",
    priority="medium",
    due_date="2026-03-08",
    tags=["shopping", "family", "birthday"]
)

# Task with reminder
result = create_task(
    title="Pay rent",
    description="Monthly rent payment",
    priority="high",
    due_date="2026-03-01",
    reminder="2026-02-28",
    tags=["finance", "monthly"]
)
```

### List Tasks

```python
from personal_tasks import list_tasks

# Get all tasks
all_tasks = list_tasks()

# Get pending tasks
pending = list_tasks(status="pending")

# Get high priority tasks
urgent = list_tasks(priority="high")

# Get tasks with specific tag
shopping = list_tasks(tag="shopping")

# Get tasks due soon (within 7 days)
upcoming = list_tasks(due_soon=True)

# Combine filters
urgent_pending = list_tasks(status="pending", priority="high")

# Display tasks
for task in pending:
    print(f"[{task['priority'].upper()}] {task['title']}")
    if task.get('due_date'):
        print(f"  Due: {task['due_date']}")
    print()
```

### Get Specific Task

```python
from personal_tasks import get_task

# Get task by ID
task = get_task("task_20260303_120000")

if task:
    print(f"Title: {task['title']}")
    print(f"Description: {task['description']}")
    print(f"Priority: {task['priority']}")
    print(f"Status: {task['status']}")
    print(f"Due: {task.get('due_date', 'No due date')}")
else:
    print("Task not found")
```

### Update Tasks

```python
from personal_tasks import update_task

# Update title
update_task(
    task_id="task_20260303_120000",
    title="Buy groceries and household items"
)

# Update priority
update_task(
    task_id="task_20260303_120000",
    priority="high"
)

# Update status
update_task(
    task_id="task_20260303_120000",
    status="in_progress"
)

# Update multiple fields
update_task(
    task_id="task_20260303_120000",
    title="Buy groceries",
    description="Updated list: milk, eggs, bread, coffee, fruit",
    priority="medium",
    due_date="2026-03-05",
    tags=["shopping", "urgent"]
)
```

### Complete Tasks

```python
from personal_tasks import complete_task

# Simple completion
result = complete_task("task_20260303_120000")

# Completion with notes
result = complete_task(
    task_id="task_20260303_120000",
    notes="Completed at Whole Foods. Spent $85."
)

print(result['message'])
```

### Delete Tasks

```python
from personal_tasks import delete_task

# Delete a task
result = delete_task("task_20260303_120000")

if result['status'] == 'success':
    print(f"Deleted: {result['message']}")
else:
    print(f"Error: {result['message']}")
```

### Get Statistics

```python
from personal_tasks import get_statistics

stats = get_statistics()

print(f"Active Tasks: {stats['total_active']}")
print(f"Completed Tasks: {stats['total_completed']}")
print(f"\nBy Status:")
print(f"  Pending: {stats['pending']}")
print(f"  In Progress: {stats['in_progress']}")
print(f"\nBy Priority:")
print(f"  High: {stats['high_priority']}")
print(f"  Medium: {stats['medium_priority']}")
print(f"  Low: {stats['low_priority']}")
print(f"\nOverdue: {stats['overdue']}")
```

### Check Reminders

```python
from personal_tasks import check_reminders

reminders = check_reminders()

if reminders:
    print(f"{len(reminders)} reminders due today:")
    for task in reminders:
        print(f"  - {task['title']}")
        if task.get('description'):
            print(f"    {task['description']}")
else:
    print("No reminders due today")
```

---

## Command-Line Examples

### Create Tasks

```bash
# Basic task
python .claude/skills/personal-tasks/personal_tasks.py create "Buy groceries"

# With description
python .claude/skills/personal-tasks/personal_tasks.py create "Buy groceries" \
  --description "Milk, eggs, bread"

# With priority
python .claude/skills/personal-tasks/personal_tasks.py create "Finish report" \
  --priority high

# With due date
python .claude/skills/personal-tasks/personal_tasks.py create "Doctor appointment" \
  --due-date 2026-03-10

# With tags
python .claude/skills/personal-tasks/personal_tasks.py create "Buy gift" \
  --tags shopping family birthday

# Complete example
python .claude/skills/personal-tasks/personal_tasks.py create "Pay rent" \
  --description "Monthly rent payment" \
  --priority high \
  --due-date 2026-03-01 \
  --tags finance monthly
```

### List Tasks

```bash
# All tasks
python .claude/skills/personal-tasks/personal_tasks.py list

# Pending tasks
python .claude/skills/personal-tasks/personal_tasks.py list --status pending

# High priority tasks
python .claude/skills/personal-tasks/personal_tasks.py list --priority high

# Tasks due soon
python .claude/skills/personal-tasks/personal_tasks.py list --due-soon

# Combine filters
python .claude/skills/personal-tasks/personal_tasks.py list \
  --status pending \
  --priority high
```

### Complete Tasks

```bash
# Simple completion
python .claude/skills/personal-tasks/personal_tasks.py complete task_20260303_120000

# With notes
python .claude/skills/personal-tasks/personal_tasks.py complete task_20260303_120000 \
  --notes "Completed at Whole Foods"
```

### Delete Tasks

```bash
python .claude/skills/personal-tasks/personal_tasks.py delete task_20260303_120000
```

### Statistics

```bash
python .claude/skills/personal-tasks/personal_tasks.py stats
```

### Reminders

```bash
python .claude/skills/personal-tasks/personal_tasks.py reminders
```

---

## Integration Examples

### Scheduler Integration

Add to `scripts/ceo_briefing_scheduler.py`:

```python
import sys
from pathlib import Path

# Add personal tasks to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "personal-tasks"))
from personal_tasks import check_reminders, get_statistics, list_tasks

# Check reminders every morning at 8 AM
schedule.every().day.at("08:00").do(check_reminders_job)

# Generate daily task summary at 9 AM
schedule.every().day.at("09:00").do(daily_task_summary)

def check_reminders_job():
    """Check and display reminders due today."""
    reminders = check_reminders()

    if reminders:
        print(f"\n{'='*60}")
        print(f"REMINDERS DUE TODAY ({len(reminders)})")
        print(f"{'='*60}")

        for task in reminders:
            print(f"\n[{task['priority'].upper()}] {task['title']}")
            if task.get('description'):
                print(f"  {task['description']}")
            if task.get('due_date'):
                print(f"  Due: {task['due_date']}")

        print(f"\n{'='*60}\n")

def daily_task_summary():
    """Generate daily task summary."""
    stats = get_statistics()
    high_priority = list_tasks(priority="high", status="pending")
    due_soon = list_tasks(due_soon=True)

    print(f"\n{'='*60}")
    print(f"DAILY TASK SUMMARY")
    print(f"{'='*60}")
    print(f"Active Tasks: {stats['total_active']}")
    print(f"High Priority: {stats['high_priority']}")
    print(f"Due Soon: {len(due_soon)}")
    print(f"Overdue: {stats['overdue']}")

    if high_priority:
        print(f"\nHigh Priority Tasks:")
        for task in high_priority[:5]:
            print(f"  - {task['title']}")

    print(f"{'='*60}\n")
```

### CEO Briefing Integration

Add to `scripts/ceo_briefing.py`:

```python
import sys
from pathlib import Path

# Add personal tasks to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "personal-tasks"))
from personal_tasks import get_statistics, list_tasks

def generate_personal_tasks_section():
    """Generate personal tasks section for CEO briefing."""

    stats = get_statistics()
    high_priority = list_tasks(priority="high", status="pending")
    overdue = list_tasks(status="pending")

    # Filter overdue tasks
    from datetime import datetime
    overdue_tasks = []
    for task in overdue:
        if task.get('due_date'):
            try:
                due = datetime.fromisoformat(task['due_date'])
                if due < datetime.now():
                    overdue_tasks.append(task)
            except:
                pass

    section = "\n## Personal Tasks\n\n"
    section += f"**Active Tasks:** {stats['total_active']}\n"
    section += f"**Completed:** {stats['total_completed']}\n"
    section += f"**High Priority:** {stats['high_priority']}\n"
    section += f"**Overdue:** {len(overdue_tasks)}\n\n"

    # High priority tasks
    if high_priority:
        section += "**High Priority Tasks:**\n"
        for task in high_priority[:5]:
            section += f"- {task['title']}"
            if task.get('due_date'):
                section += f" (Due: {task['due_date']})"
            section += "\n"
        section += "\n"

    # Overdue tasks
    if overdue_tasks:
        section += "**Overdue Tasks:**\n"
        for task in overdue_tasks[:3]:
            section += f"- {task['title']} (Due: {task['due_date']})\n"
        section += "\n"

    return section

# In main briefing generation
def generate_briefing():
    briefing = "# CEO Weekly Briefing\n\n"

    # ... other sections ...

    # Add personal tasks section
    briefing += generate_personal_tasks_section()

    # ... rest of briefing ...

    return briefing
```

### Plan Workflow Integration

Extract tasks from Plan.md files:

```python
import sys
from pathlib import Path
import re

# Add personal tasks to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "personal-tasks"))
from personal_tasks import create_task

def extract_tasks_from_plan(plan_path):
    """Extract action items from Plan.md and create personal tasks."""

    with open(plan_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract numbered steps
    steps = re.findall(r'^\d+\.\s+(.+)$', content, re.MULTILINE)

    created_tasks = []

    for step in steps:
        # Create task for each step
        result = create_task(
            title=step,
            priority="high",
            tags=["plan", "work", "project"]
        )

        if result['status'] == 'success':
            created_tasks.append(result['task_id'])

    return created_tasks

# Usage
plan_file = Path("AI_Employee_Vault/Plans/Plan_20260303_120000.md")
task_ids = extract_tasks_from_plan(plan_file)
print(f"Created {len(task_ids)} tasks from plan")
```

### Ralph Loop Integration

Integrate with Ralph Wiggum Autonomous Loop:

```python
import sys
from pathlib import Path

# Add personal tasks to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "personal-tasks"))
from personal_tasks import create_task, complete_task

def create_task_from_vault_file(vault_file):
    """Create personal task from vault file."""

    with open(vault_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title (first # heading)
    title = "Unknown Task"
    for line in content.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # Create task
    result = create_task(
        title=title,
        description=content[:200],
        priority="medium",
        tags=["vault", "automated"]
    )

    return result

def mark_vault_task_complete(task_id, vault_file):
    """Mark task complete when vault file is processed."""

    result = complete_task(
        task_id=task_id,
        notes=f"Completed via Ralph Loop: {vault_file.name}"
    )

    return result
```

---

## Workflow Examples

### Morning Routine

```python
from personal_tasks import check_reminders, list_tasks, get_statistics

def morning_routine():
    """Morning task review routine."""

    print("\n" + "="*60)
    print("MORNING TASK REVIEW")
    print("="*60 + "\n")

    # Check reminders
    reminders = check_reminders()
    if reminders:
        print(f"Reminders Due Today ({len(reminders)}):")
        for task in reminders:
            print(f"  - {task['title']}")
        print()

    # High priority tasks
    high_priority = list_tasks(priority="high", status="pending")
    if high_priority:
        print(f"High Priority Tasks ({len(high_priority)}):")
        for task in high_priority:
            print(f"  - {task['title']}")
        print()

    # Tasks due soon
    due_soon = list_tasks(due_soon=True)
    if due_soon:
        print(f"Tasks Due Soon ({len(due_soon)}):")
        for task in due_soon:
            print(f"  - {task['title']} (Due: {task['due_date']})")
        print()

    # Statistics
    stats = get_statistics()
    print(f"Total Active: {stats['total_active']}")
    print(f"Overdue: {stats['overdue']}")
    print("\n" + "="*60 + "\n")

# Run morning routine
morning_routine()
```

### Weekly Review

```python
from personal_tasks import get_statistics, list_tasks

def weekly_review():
    """Weekly task review and planning."""

    stats = get_statistics()

    print("\n" + "="*60)
    print("WEEKLY TASK REVIEW")
    print("="*60 + "\n")

    print(f"Completed This Week: {stats['total_completed']}")
    print(f"Active Tasks: {stats['total_active']}")
    print(f"Overdue: {stats['overdue']}")
    print()

    # Review by priority
    print("By Priority:")
    print(f"  High: {stats['high_priority']}")
    print(f"  Medium: {stats['medium_priority']}")
    print(f"  Low: {stats['low_priority']}")
    print()

    # List all pending tasks
    pending = list_tasks(status="pending")
    if pending:
        print(f"Pending Tasks ({len(pending)}):")
        for task in pending:
            print(f"  [{task['priority'].upper()}] {task['title']}")
            if task.get('due_date'):
                print(f"      Due: {task['due_date']}")
        print()

    print("="*60 + "\n")

# Run weekly review
weekly_review()
```

### Batch Operations

```python
from personal_tasks import list_tasks, update_task, complete_task

# Mark all low priority tasks as in_progress
low_priority = list_tasks(priority="low", status="pending")
for task in low_priority:
    update_task(task['id'], status="in_progress")

# Complete all tasks with specific tag
shopping_tasks = list_tasks(tag="shopping")
for task in shopping_tasks:
    if task['status'] != 'completed':
        complete_task(task['id'], notes="Batch completion")

# Update priority for overdue tasks
from datetime import datetime
all_tasks = list_tasks(status="pending")
for task in all_tasks:
    if task.get('due_date'):
        try:
            due = datetime.fromisoformat(task['due_date'])
            if due < datetime.now():
                update_task(task['id'], priority="high")
        except:
            pass
```

---

## Error Handling Examples

```python
from personal_tasks import create_task, complete_task, get_task

# Safe task creation
def safe_create_task(title, **kwargs):
    """Create task with error handling."""
    try:
        result = create_task(title, **kwargs)
        if result['status'] == 'success':
            print(f"Created: {result['task_id']}")
            return result['task_id']
        else:
            print(f"Error: {result['message']}")
            return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

# Safe task completion
def safe_complete_task(task_id, notes=None):
    """Complete task with error handling."""
    try:
        # Check if task exists
        task = get_task(task_id)
        if not task:
            print(f"Task not found: {task_id}")
            return False

        # Complete task
        result = complete_task(task_id, notes)
        if result['status'] == 'success':
            print(f"Completed: {result['message']}")
            return True
        else:
            print(f"Error: {result['message']}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False
```

---

## Testing Examples

```python
from personal_tasks import create_task, list_tasks, complete_task, get_statistics

# Test task creation
print("Testing task creation...")
result = create_task(
    title="Test Task",
    description="This is a test",
    priority="high"
)
assert result['status'] == 'success'
task_id = result['task_id']
print(f"Created task: {task_id}")

# Test task listing
print("\nTesting task listing...")
tasks = list_tasks(priority="high")
assert len(tasks) > 0
print(f"Found {len(tasks)} high priority tasks")

# Test task completion
print("\nTesting task completion...")
result = complete_task(task_id)
assert result['status'] == 'success'
print("Task completed successfully")

# Test statistics
print("\nTesting statistics...")
stats = get_statistics()
assert 'total_active' in stats
assert 'total_completed' in stats
print(f"Stats: {stats['total_active']} active, {stats['total_completed']} completed")

print("\nAll tests passed!")
```
