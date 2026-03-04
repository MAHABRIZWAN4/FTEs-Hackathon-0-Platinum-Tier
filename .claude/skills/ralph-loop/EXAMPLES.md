# Ralph Loop - Quick Examples

## Start Autonomous Loop

```bash
# Run continuously (checks every 60 seconds)
python scripts/ralph_loop.py
```

## Process Single Task

```bash
# Process one task and exit
python scripts/ralph_loop.py --single
```

## Dry-Run Mode (Safe Testing)

```bash
# Test without making changes
python scripts/ralph_loop.py --dry-run --single
```

## Custom Max Iterations

```bash
# Allow up to 10 steps per task
python scripts/ralph_loop.py --max-iterations 10
```

## Create a Test Task

Create `AI_Employee_Vault/Needs_Action/test_task.md`:

```markdown
# Test Task - Update Documentation

Update the project README with recent changes.

## Steps

1. Review current README.md
2. Add new features section
3. Update installation instructions
4. Verify all links work
5. Commit changes

## Priority

Low

## Notes

This is a test task for Ralph Loop validation.
```

## Run Test Task

```bash
# Process the test task
python scripts/ralph_loop.py --single --dry-run
```

## Monitor Loop Activity

```bash
# Watch logs in real-time
tail -f logs/actions.log | grep RALPH_LOOP

# View execution plans
ls -lt AI_Employee_Vault/Plans/ | head -5

# Check completed tasks
ls -lt AI_Employee_Vault/Done/ | head -5
```

## Integration with Scheduler

### Option 1: Standalone Scheduler

Create `scripts/ralph_scheduler.py`:

```python
#!/usr/bin/env python3
import schedule
import time
from ralph_loop import run_autonomous_loop

# Run every 15 minutes
schedule.every(15).minutes.do(
    lambda: run_autonomous_loop(single_run=True)
)

print("Ralph Loop Scheduler started")
print("Running every 15 minutes...")

while True:
    schedule.run_pending()
    time.sleep(60)
```

Run it:
```bash
python scripts/ralph_scheduler.py
```

### Option 2: Add to Existing Scheduler

Add to `scripts/ceo_briefing_scheduler.py`:

```python
from ralph_loop import run_autonomous_loop

# Run Ralph Loop every 15 minutes
schedule.every(15).minutes.do(
    lambda: run_autonomous_loop(single_run=True)
)
```

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Ralph Autonomous Loop"
4. Trigger: Every 15 minutes
5. Action: Start a program
6. Program: `python`
7. Arguments: `F:\FTEs\Gold Tier\scripts\ralph_loop.py --single`
8. Start in: `F:\FTEs\Gold Tier`

### Option 4: Linux/Mac Cron

```bash
# Edit crontab
crontab -e

# Add this line (runs every 15 minutes)
*/15 * * * * cd /path/to/project && python scripts/ralph_loop.py --single >> logs/ralph_cron.log 2>&1
```

## Approval Workflow Example

### Create Risky Task

Create `AI_Employee_Vault/Needs_Action/cleanup_task.md`:

```markdown
# Cleanup Old Files

Remove temporary files older than 30 days.

## Steps

1. Find files in temp/ older than 30 days
2. Delete identified files
3. Verify disk space freed
4. Log cleanup results

## Priority

Medium
```

### Run Ralph Loop

```bash
python scripts/ralph_loop.py --single
```

### Result

Task moved to `Needs_Approval/` because it contains "delete" (risky keyword).

### Approve Task

```bash
# Move back to Needs_Action to approve
mv AI_Employee_Vault/Needs_Approval/cleanup_task.md AI_Employee_Vault/Needs_Action/

# Run again
python scripts/ralph_loop.py --single
```

## View Execution Plan

```bash
# Find latest plan
LATEST_PLAN=$(ls -t AI_Employee_Vault/Plans/ | head -1)

# View it
cat "AI_Employee_Vault/Plans/$LATEST_PLAN"
```

Output:
```markdown
# Execution Plan: Test Task - Update Documentation

**Created:** 2026-03-03 16:45:00
**Task File:** AI_Employee_Vault/Needs_Action/test_task.md
**Risk Level:** LOW

---

## Task Description

Update the project README with recent changes.

---

## Execution Steps

1. Review current README.md
2. Add new features section
3. Update installation instructions
4. Verify all links work
5. Commit changes

---

## Execution Log

### Step 1: SUCCESS
**Time:** 2026-03-03 16:45:05
**Result:** Step 1 completed: Review current README.md

### Step 2: SUCCESS
**Time:** 2026-03-03 16:45:10
**Result:** Step 2 completed: Add new features section
...
```

## Check Task Status

```bash
# Count pending tasks
ls AI_Employee_Vault/Needs_Action/*.md 2>/dev/null | wc -l

# Count tasks needing approval
ls AI_Employee_Vault/Needs_Approval/*.md 2>/dev/null | wc -l

# Count completed tasks
ls AI_Employee_Vault/Done/*.md 2>/dev/null | wc -l

# Count execution plans
ls AI_Employee_Vault/Plans/*.md 2>/dev/null | wc -l
```

## Error Recovery Integration

Ralph Loop automatically integrates with Error Recovery:

```python
from scripts.ralph_loop import execute_task
from pathlib import Path

# Execute task with automatic error recovery
task_file = Path("AI_Employee_Vault/Needs_Action/my_task.md")
success = execute_task(task_file)

if not success:
    print("Task failed - check logs/errors.log")
    print("Task added to retry queue")
```

## Programmatic Usage

```python
from scripts.ralph_loop import (
    get_pending_tasks,
    analyze_task,
    create_plan,
    execute_task
)

# Get pending tasks
tasks = get_pending_tasks()
print(f"Found {len(tasks)} pending tasks")

# Analyze a task
if tasks:
    analysis = analyze_task(tasks[0])
    print(f"Task: {analysis['title']}")
    print(f"Risk: {analysis['risk_level']}")
    print(f"Steps: {len(analysis['steps'])}")

    # Create plan
    plan_path = create_plan(analysis)
    print(f"Plan created: {plan_path}")

    # Execute task
    success = execute_task(tasks[0], dry_run=True)
    print(f"Success: {success}")
```

## Statistics

```python
from pathlib import Path

vault = Path("AI_Employee_Vault")

stats = {
    "pending": len(list((vault / "Needs_Action").glob("*.md"))),
    "approval": len(list((vault / "Needs_Approval").glob("*.md"))),
    "completed": len(list((vault / "Done").glob("*.md"))),
    "plans": len(list((vault / "Plans").glob("*.md")))
}

print(f"Pending: {stats['pending']}")
print(f"Needs Approval: {stats['approval']}")
print(f"Completed: {stats['completed']}")
print(f"Plans Created: {stats['plans']}")
```

## Batch Processing

```bash
# Process all pending tasks (one at a time)
while [ $(ls AI_Employee_Vault/Needs_Action/*.md 2>/dev/null | wc -l) -gt 0 ]; do
    python scripts/ralph_loop.py --single
    sleep 5
done
```

## Debug Mode

```bash
# Run with verbose output
python scripts/ralph_loop.py --single 2>&1 | tee ralph_debug.log
```

## Clean Up

```bash
# Archive old plans (older than 30 days)
find AI_Employee_Vault/Plans/ -name "*.md" -mtime +30 -exec mv {} AI_Employee_Vault/Plans/Archive/ \;

# Clean up old completed tasks
find AI_Employee_Vault/Done/ -name "*.md" -mtime +90 -exec rm {} \;
```
