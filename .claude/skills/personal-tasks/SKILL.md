# Personal Task Handler Skill

## Description

Comprehensive personal task management system for the Gold Tier AI Employee. Manages personal tasks, reminders, to-dos, and priorities in the Personal domain with full integration into the existing infrastructure.

## Trigger

**Programmatic:** Import and call from other skills
```python
from personal_tasks import create_task, list_tasks, complete_task
```

**Command-line:**
```bash
python .claude/skills/personal-tasks/personal_tasks.py create "Task title"
python .claude/skills/personal-tasks/personal_tasks.py list
python .claude/skills/personal-tasks/personal_tasks.py complete task_123
```

## Capabilities

- Create and manage personal tasks
- Set priorities (low, medium, high)
- Due date tracking
- Reminder system
- Tag-based organization
- Task completion tracking
- Statistics and reporting
- Integration with scheduler
- Plan workflow integration
- Comprehensive logging

## File Structure

```
.claude/skills/personal-tasks/
  ├── personal_tasks.py          # Main implementation
  ├── SKILL.md                   # This file
  ├── EXAMPLES.md                # Usage examples
  ├── requirements.txt           # Dependencies
  ├── test.py                    # Validation tests
  └── STATUS.md                  # Implementation status

AI_Employee_Vault/Personal/
  ├── tasks.json                 # Active tasks
  ├── completed.json             # Completed tasks
  └── reminders.json             # Reminders (future)

logs/
  └── actions.log                # Activity logging
```

## Core Functions

### create_task()

Create a new personal task.

```python
def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
    reminder: Optional[str] = None
) -> Dict
```

**Parameters:**
- `title` (str): Task title (required)
- `description` (str): Task description
- `priority` (str): Priority level (low, medium, high)
- `due_date` (str): Due date in YYYY-MM-DD format
- `tags` (list): List of tags for organization
- `reminder` (str): Reminder date in YYYY-MM-DD format

**Returns:**
- `dict`: Result with status, task_id, task data, and message

**Example:**
```python
result = create_task(
    title="Buy groceries",
    description="Milk, eggs, bread, coffee",
    priority="medium",
    due_date="2026-03-05",
    tags=["shopping", "personal"]
)
```

### list_tasks()

List tasks with optional filtering.

```python
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    due_soon: bool = False
) -> List[Dict]
```

**Parameters:**
- `status` (str): Filter by status (pending, in_progress, completed)
- `priority` (str): Filter by priority (low, medium, high)
- `tag` (str): Filter by tag
- `due_soon` (bool): Show only tasks due within 7 days

**Returns:**
- `list`: List of tasks matching filters

**Example:**
```python
# Get all pending tasks
pending = list_tasks(status="pending")

# Get high priority tasks
urgent = list_tasks(priority="high")

# Get tasks due soon
upcoming = list_tasks(due_soon=True)
```

### get_task()

Get a specific task by ID.

```python
def get_task(task_id: str) -> Optional[Dict]
```

**Parameters:**
- `task_id` (str): Task ID

**Returns:**
- `dict`: Task data or None if not found

### update_task()

Update an existing task.

```python
def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict
```

**Parameters:**
- `task_id` (str): Task ID (required)
- Other parameters: Optional fields to update

**Returns:**
- `dict`: Update result with status and message

### complete_task()

Mark a task as completed.

```python
def complete_task(task_id: str, notes: Optional[str] = None) -> Dict
```

**Parameters:**
- `task_id` (str): Task ID
- `notes` (str): Optional completion notes

**Returns:**
- `dict`: Completion result

**Example:**
```python
result = complete_task(
    task_id="task_20260303_120000",
    notes="Completed at Whole Foods"
)
```

### delete_task()

Delete a task permanently.

```python
def delete_task(task_id: str) -> Dict
```

**Parameters:**
- `task_id` (str): Task ID

**Returns:**
- `dict`: Deletion result

### get_statistics()

Get task statistics.

```python
def get_statistics() -> Dict
```

**Returns:**
- `dict`: Statistics including:
  - total_active: Number of active tasks
  - total_completed: Number of completed tasks
  - pending: Number of pending tasks
  - in_progress: Number of in-progress tasks
  - high_priority: Number of high priority tasks
  - medium_priority: Number of medium priority tasks
  - low_priority: Number of low priority tasks
  - overdue: Number of overdue tasks

### check_reminders()

Check for tasks with reminders due today.

```python
def check_reminders() -> List[Dict]
```

**Returns:**
- `list`: Tasks with reminders due today

## Task Data Structure

```json
{
  "id": "task_20260303_120000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, coffee",
  "priority": "medium",
  "status": "pending",
  "created_at": "2026-03-03T12:00:00",
  "updated_at": "2026-03-03T12:30:00",
  "due_date": "2026-03-05",
  "tags": ["shopping", "personal"],
  "reminder": "2026-03-05"
}
```

## Priority Levels

- **high**: Urgent tasks requiring immediate attention
- **medium**: Normal priority tasks (default)
- **low**: Tasks that can be done when time permits

## Status Values

- **pending**: Task created but not started
- **in_progress**: Task currently being worked on
- **completed**: Task finished

## Command-Line Usage

### Create a Task

```bash
# Basic task
python .claude/skills/personal-tasks/personal_tasks.py create "Buy groceries"

# With options
python .claude/skills/personal-tasks/personal_tasks.py create "Buy groceries" \
  --description "Milk, eggs, bread" \
  --priority high \
  --due-date 2026-03-05 \
  --tags shopping personal
```

### List Tasks

```bash
# All tasks
python .claude/skills/personal-tasks/personal_tasks.py list

# Filter by status
python .claude/skills/personal-tasks/personal_tasks.py list --status pending

# Filter by priority
python .claude/skills/personal-tasks/personal_tasks.py list --priority high

# Tasks due soon
python .claude/skills/personal-tasks/personal_tasks.py list --due-soon
```

### Complete a Task

```bash
python .claude/skills/personal-tasks/personal_tasks.py complete task_20260303_120000 \
  --notes "Completed at Whole Foods"
```

### Delete a Task

```bash
python .claude/skills/personal-tasks/personal_tasks.py delete task_20260303_120000
```

### View Statistics

```bash
python .claude/skills/personal-tasks/personal_tasks.py stats
```

Output:
```
Task Statistics:
========================================
Total Active: 5
Total Completed: 12

By Status:
  Pending: 3
  In Progress: 2

By Priority:
  High: 1
  Medium: 3
  Low: 1

Overdue: 0
========================================
```

### Check Reminders

```bash
python .claude/skills/personal-tasks/personal_tasks.py reminders
```

## Scheduler Integration

Add to `scripts/ceo_briefing_scheduler.py`:

```python
import sys
from pathlib import Path

# Add personal tasks to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "skills" / "personal-tasks"))
from personal_tasks import check_reminders, get_statistics

# Check reminders every morning at 8 AM
schedule.every().day.at("08:00").do(check_reminders_job)

def check_reminders_job():
    """Check and log reminders due today."""
    reminders = check_reminders()
    if reminders:
        print(f"[REMINDER] {len(reminders)} tasks due today:")
        for task in reminders:
            print(f"  - {task['title']}")
```

## Plan Workflow Integration

Create tasks from Plan.md files:

```python
from personal_tasks import create_task

def process_plan_file(plan_path):
    """Extract tasks from Plan.md and create personal tasks."""
    with open(plan_path, 'r') as f:
        content = f.read()

    # Parse plan and extract action items
    # Create personal tasks for each action item
    for action in extract_actions(content):
        create_task(
            title=action['title'],
            description=action['description'],
            priority="high",
            tags=["plan", "work"]
        )
```

## CEO Briefing Integration

Add personal tasks section to CEO briefing:

```python
from personal_tasks import get_statistics, list_tasks

def generate_personal_section():
    """Generate personal tasks section for CEO briefing."""

    stats = get_statistics()

    section = "\n## Personal Tasks\n\n"
    section += f"**Active Tasks:** {stats['total_active']}\n"
    section += f"**Completed This Week:** {stats['total_completed']}\n"
    section += f"**High Priority:** {stats['high_priority']}\n"
    section += f"**Overdue:** {stats['overdue']}\n\n"

    # List high priority tasks
    high_priority = list_tasks(priority="high", status="pending")
    if high_priority:
        section += "**High Priority Tasks:**\n"
        for task in high_priority[:5]:
            section += f"- {task['title']}"
            if task.get('due_date'):
                section += f" (Due: {task['due_date']})"
            section += "\n"

    return section
```

## Environment Variables

Configure via `.env` file:

```bash
# Personal tasks configuration
PERSONAL_DIR=AI_Employee_Vault/Personal
LOGS_DIR=logs
```

## Error Handling

The skill includes comprehensive error handling:

- ✅ File I/O errors caught and logged
- ✅ Invalid parameters handled gracefully
- ✅ Failed operations return error status
- ✅ All errors logged to logs/actions.log
- ✅ JSON parsing errors handled
- ✅ Missing files auto-created

## Logging

All operations are logged to `logs/actions.log`:

```
[2026-03-03 12:00:00] [SUCCESS] [PERSONAL_TASKS] Created task: Buy groceries (ID: task_20260303_120000)
[2026-03-03 12:30:00] [SUCCESS] [PERSONAL_TASKS] Completed task: Buy groceries (ID: task_20260303_120000)
[2026-03-03 13:00:00] [INFO] [PERSONAL_TASKS] Found 2 reminders due today
```

## Use Cases

### Daily Task Management
Track daily to-dos, errands, and personal responsibilities.

### Project Planning
Break down personal projects into manageable tasks with priorities.

### Reminder System
Set reminders for important dates, appointments, and deadlines.

### Goal Tracking
Track progress on personal goals with completion statistics.

### Shopping Lists
Manage shopping lists with tags and priorities.

## Benefits

1. **Centralized Management:** All personal tasks in one place
2. **Priority-Based:** Focus on what matters most
3. **Due Date Tracking:** Never miss a deadline
4. **Tag Organization:** Flexible categorization
5. **Statistics:** Track productivity and completion rates
6. **Scheduler Integration:** Automated reminder checks
7. **CEO Briefing Integration:** Personal tasks in executive reports
8. **Zero Dependencies:** Python stdlib only
9. **Production-Ready:** Comprehensive error handling and logging
10. **Extensible:** Easy to add new features

## Limitations

- No recurring tasks (yet)
- No subtasks or task dependencies
- No time-of-day for reminders (date only)
- No collaboration features
- No mobile app integration

## Future Enhancements

- Recurring tasks (daily, weekly, monthly)
- Subtasks and task hierarchies
- Task dependencies
- Time-based reminders
- Email/SMS notifications
- Calendar integration
- Mobile app sync
- Voice input support
- AI-powered task suggestions

## Dependencies

- Python 3.7+
- Standard library only (no external packages)
- python-dotenv (optional, for .env support)

## Troubleshooting

### Tasks Not Saving
**Solution:** Check file permissions on AI_Employee_Vault/Personal/ directory

### Statistics Not Accurate
**Solution:** Verify tasks.json and completed.json are valid JSON

### Reminders Not Working
**Solution:** Ensure reminder dates are in YYYY-MM-DD format

## Security

- ✅ No sensitive data stored
- ✅ Local file storage only
- ✅ No external API calls
- ✅ File permissions respect system settings

## Support

For issues or questions:
1. Check EXAMPLES.md for usage patterns
2. Review logs/actions.log for error details
3. Verify AI_Employee_Vault/Personal/ exists
4. Run test.py to validate installation
