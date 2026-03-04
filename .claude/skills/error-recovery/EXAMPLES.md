# Error Recovery - Quick Examples

## Basic Usage with Decorator

```python
from scripts.error_recovery import with_error_recovery

@with_error_recovery
def process_data(file_path):
    """Process data file with automatic error recovery."""
    with open(file_path, 'r') as f:
        data = f.read()

    # Process data
    result = transform_data(data)
    save_result(result)

    return result

# Use the function - errors are automatically handled
process_data("data/input.csv")
```

## Manual Error Handling

```python
from scripts.error_recovery import handle_error

def complex_operation():
    try:
        step1()
        step2()
        step3()
    except Exception as e:
        # Handle error manually
        result = handle_error(
            e,
            context="complex_operation",
            file_path="data/input.txt",
            add_to_queue=True
        )

        print(f"Error handled: {result['error_type']}")
        print(f"File moved to: {result['moved_to']}")
```

## Run Error Recovery Service

```bash
# Start service (monitors retry queue every minute)
python scripts/error_recovery.py --service
```

Output:
```
============================================================
ERROR RECOVERY SERVICE
============================================================
Started: 2026-03-03 16:00:00
Retry delay: 300 seconds
Max retries: 1
============================================================

[INFO] Error Recovery Service started
[INFO] Processing 2 tasks from retry queue
[SUCCESS] Task retry succeeded: data_processing.process_file
[ERROR] Task permanently failed after 1 retries: email_sending
```

## Process Retry Queue Manually

```bash
# Process queue once
python scripts/error_recovery.py --process-queue
```

## View Error Statistics

```bash
python scripts/error_recovery.py --stats
```

Output:
```
============================================================
ERROR RECOVERY STATISTICS
============================================================
Total Errors Logged: 15
Tasks in Retry Queue: 3

Error Types:
  FileNotFoundError: 5
  ValueError: 4
  ConnectionError: 3

Retry Queue Status:
  Pending Retry: 2
  Permanently Failed: 1
============================================================
```

## Clear Retry Queue

```bash
python scripts/error_recovery.py --clear-queue
```

## Integration with Accounting Manager

```python
from scripts.error_recovery import with_error_recovery
from scripts.accounting_manager import add_transaction

@with_error_recovery
def safe_add_transaction(date, title, type, amount, description):
    """Add transaction with error recovery."""
    return add_transaction(date, title, type, amount, description)

# Use it
try:
    safe_add_transaction(
        date="2026-03-03",
        title="Client Payment",
        type="income",
        amount=5000.00,
        description="Monthly retainer"
    )
except Exception as e:
    print(f"Transaction failed but error was handled: {e}")
```

## Integration with CEO Briefing

```python
from scripts.error_recovery import with_error_recovery
from scripts.ceo_briefing import generate_ceo_briefing

@with_error_recovery
def safe_generate_briefing():
    """Generate CEO briefing with error recovery."""
    return generate_ceo_briefing()

# Schedule with error recovery
import schedule

schedule.every().monday.at("09:00").do(safe_generate_briefing)
```

## Custom Retry Logic

```python
from scripts.error_recovery import handle_error, load_retry_queue

def custom_retry_handler(task):
    """Custom retry logic for specific task types."""
    context = task.get("context")

    if "email" in context:
        # Custom email retry logic
        retry_email(task)
    elif "database" in context:
        # Custom database retry logic
        retry_database(task)
    else:
        # Default retry
        retry_default(task)

# Process queue with custom handler
queue = load_retry_queue()
for task in queue["tasks"]:
    if task["status"] == "pending_retry":
        custom_retry_handler(task)
```

## Monitor Error Logs

```bash
# View recent errors
tail -50 logs/errors.log

# Watch errors in real-time
tail -f logs/errors.log

# Search for specific error type
grep "FileNotFoundError" logs/errors.log

# Count errors by type
grep "Error Type:" logs/errors.log | sort | uniq -c
```

## Check Failed Files

```bash
# List failed files
ls -lh AI_Employee_Vault/Errors/

# Count failed files
ls AI_Employee_Vault/Errors/ | wc -l

# Find files from today
find AI_Employee_Vault/Errors/ -name "$(date +%Y%m%d)*"

# View a failed file
cat AI_Employee_Vault/Errors/20260303_160000_input.csv
```

## Inspect Retry Queue

```bash
# View retry queue
cat logs/retry_queue.json

# Pretty print
python -m json.tool logs/retry_queue.json

# Count pending retries
python -c "import json; q=json.load(open('logs/retry_queue.json')); print(sum(1 for t in q['tasks'] if t['status']=='pending_retry'))"
```

## Programmatic Error Statistics

```python
from scripts.error_recovery import get_error_statistics

stats = get_error_statistics()

print(f"Total Errors: {stats['total_errors']}")
print(f"\nError Breakdown:")
for error_type, count in stats['error_types'].items():
    print(f"  {error_type}: {count}")

# Alert if too many errors
if stats['total_errors'] > 100:
    send_alert("High error count detected!")
```

## Wrap Existing Functions

```python
from scripts.error_recovery import with_error_recovery

# Wrap third-party functions
safe_requests_get = with_error_recovery(requests.get)
safe_json_load = with_error_recovery(json.load)

# Use wrapped versions
response = safe_requests_get("https://api.example.com/data")
data = safe_json_load(open("config.json"))
```

## Error Recovery in Scripts

```python
#!/usr/bin/env python3
from scripts.error_recovery import with_error_recovery, handle_error

@with_error_recovery
def main():
    """Main script with error recovery."""
    try:
        # Your main logic
        process_all_files()
        generate_reports()
        send_notifications()
    except Exception as e:
        # Additional error handling if needed
        print(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Test Error Recovery

```bash
# Run validation tests
python .claude/skills/error-recovery/test.py
```

## Windows Service Setup

Create a batch file `error_recovery_service.bat`:

```batch
@echo off
cd /d F:\FTEs\Gold Tier
python scripts\error_recovery.py --service
```

Then create a Windows Service or Task Scheduler task to run it at startup.

## Linux/Mac Service Setup

Create systemd service `/etc/systemd/system/error-recovery.service`:

```ini
[Unit]
Description=Error Recovery Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 scripts/error_recovery.py --service
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable error-recovery
sudo systemctl start error-recovery
sudo systemctl status error-recovery
```

## Cron Job for Queue Processing

```bash
# Add to crontab (process queue every 5 minutes)
*/5 * * * * cd /path/to/project && python scripts/error_recovery.py --process-queue
```

## Email Notifications on Errors

```python
from scripts.error_recovery import with_error_recovery
from scripts.send_email import send_email

@with_error_recovery
def critical_operation():
    """Operation that sends email on failure."""
    try:
        perform_critical_task()
    except Exception as e:
        # Send alert email
        send_email(
            to="admin@company.com",
            subject="Critical Operation Failed",
            body=f"Error: {str(e)}\n\nCheck logs/errors.log for details"
        )
        raise  # Re-raise to trigger error recovery
```

## Dashboard Integration

```python
from scripts.error_recovery import get_error_statistics, load_retry_queue

def get_error_dashboard_data():
    """Get data for error dashboard."""
    stats = get_error_statistics()
    queue = load_retry_queue()

    return {
        "total_errors": stats["total_errors"],
        "error_types": stats["error_types"],
        "pending_retries": sum(1 for t in queue["tasks"] if t["status"] == "pending_retry"),
        "permanent_failures": sum(1 for t in queue["tasks"] if t["status"] == "permanently_failed"),
        "last_error": get_last_error_time()
    }
```
