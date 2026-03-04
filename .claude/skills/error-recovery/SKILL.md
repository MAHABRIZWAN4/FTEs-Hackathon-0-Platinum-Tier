# Error Recovery Agent Skill

## Description
Automated error handling and recovery system for the Gold Tier AI Employee. Detects failures, logs errors, quarantines failed files, and automatically retries operations after a delay.

## Trigger
- **Automatic:** Use as decorator on any function
- **Service:** `python scripts/error_recovery.py --service`
- **Manual:** Import and call error handling functions
- **Command:** `/error-recovery`

## Capabilities
- Automatic error detection and logging
- Comprehensive error tracking to logs/errors.log
- Failed file quarantine to AI_Employee_Vault/Errors/
- Automatic retry after 5 minutes (once)
- Retry queue management
- Error statistics and reporting
- Decorator for easy integration
- Background service mode
- Permanent failure tracking

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. Error Occurs in Any Task                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Error Handler Activated                             │
│     - Capture exception details                         │
│     - Extract stack trace                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Log Error to logs/errors.log                        │
│     - Timestamp                                          │
│     - Error type and message                            │
│     - Context/operation                                 │
│     - Full stack trace                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Move Failed File (if applicable)                    │
│     - Move to AI_Employee_Vault/Errors/                 │
│     - Add timestamp to filename                         │
│     - Preserve original file                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. Add to Retry Queue                                  │
│     - Schedule retry in 5 minutes                       │
│     - Track retry count                                 │
│     - Store task context                                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  6. Wait 5 Minutes                                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  7. Retry Task (Once)                                   │
│     - Attempt operation again                           │
│     - If success: Remove from queue                     │
│     - If fail: Mark permanently failed                  │
└─────────────────────────────────────────────────────────┘
```

## Functions

### with_error_recovery (Decorator)

Wrap any function with automatic error handling.

**Usage:**
```python
from scripts.error_recovery import with_error_recovery

@with_error_recovery
def risky_operation(file_path):
    # Your code that might fail
    process_file(file_path)
```

**Features:**
- Automatic error logging
- File quarantine if file_path provided
- Retry queue addition
- Stack trace capture

### handle_error(error, context, file_path, add_to_queue)

Manually handle an error.

**Parameters:**
- `error` (Exception): The exception that occurred
- `context` (str): Context/operation name
- `file_path` (str, optional): Path to failed file
- `add_to_queue` (bool): Whether to add to retry queue

**Returns:**
- `dict`: Error handling result

**Example:**
```python
from scripts.error_recovery import handle_error

try:
    dangerous_operation()
except Exception as e:
    result = handle_error(
        e,
        context="data_processing",
        file_path="data/input.csv",
        add_to_queue=True
    )
```

### process_retry_queue()

Process the retry queue and retry eligible tasks.

**Example:**
```python
from scripts.error_recovery import process_retry_queue

# Process queue once
process_retry_queue()
```

### get_error_statistics()

Get error statistics from logs.

**Returns:**
- `dict`: Statistics with total errors, error types, etc.

**Example:**
```python
from scripts.error_recovery import get_error_statistics

stats = get_error_statistics()
print(f"Total errors: {stats['total_errors']}")
```

## Configuration

### Retry Settings

Edit `scripts/error_recovery.py`:

```python
RETRY_DELAY_SECONDS = 300  # 5 minutes
MAX_RETRIES = 1            # Retry once
```

### File Locations

- **Error Log:** `logs/errors.log`
- **Retry Queue:** `logs/retry_queue.json`
- **Failed Files:** `AI_Employee_Vault/Errors/`
- **Actions Log:** `logs/actions.log`

## Usage Examples

### As Decorator

```python
from scripts.error_recovery import with_error_recovery

@with_error_recovery
def process_invoice(invoice_file):
    # Process invoice
    data = read_invoice(invoice_file)
    validate_data(data)
    save_to_database(data)
```

### Manual Error Handling

```python
from scripts.error_recovery import handle_error

def complex_operation():
    try:
        step1()
        step2()
        step3()
    except Exception as e:
        handle_error(
            e,
            context="complex_operation",
            file_path="data/input.txt"
        )
        raise  # Re-raise if needed
```

### Run as Service

```bash
# Start error recovery service (monitors retry queue)
python scripts/error_recovery.py --service
```

The service runs in the background and:
- Checks retry queue every minute
- Retries eligible tasks
- Marks permanently failed tasks
- Logs all activity

### Process Queue Manually

```bash
# Process retry queue once
python scripts/error_recovery.py --process-queue
```

### View Statistics

```bash
# Show error statistics
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
  KeyError: 2
  TypeError: 1

Retry Queue Status:
  Pending Retry: 2
  Permanently Failed: 1
============================================================
```

### Clear Retry Queue

```bash
# Clear all tasks from retry queue
python scripts/error_recovery.py --clear-queue
```

## Error Log Format

Errors are logged to `logs/errors.log`:

```
================================================================================
[2026-03-03 16:00:00] ERROR DETECTED
================================================================================
Context: data_processing.process_file
Error Type: FileNotFoundError
Error Message: [Errno 2] No such file or directory: 'data/input.csv'
File: data/input.csv

Stack Trace:
Traceback (most recent call last):
  File "scripts/data_processing.py", line 45, in process_file
    with open(file_path, 'r') as f:
FileNotFoundError: [Errno 2] No such file or directory: 'data/input.csv'
================================================================================
```

## Retry Queue Format

Retry queue stored in `logs/retry_queue.json`:

```json
{
  "tasks": [
    {
      "id": "data_processing_20260303160000",
      "context": "data_processing.process_file",
      "error_message": "File not found",
      "file_path": "AI_Employee_Vault/Errors/20260303_160000_input.csv",
      "retry_count": 0,
      "failed_at": "2026-03-03T16:00:00",
      "retry_at": "2026-03-03T16:05:00",
      "status": "pending_retry"
    }
  ]
}
```

## Integration with Existing Skills

### Accounting Manager

```python
from scripts.error_recovery import with_error_recovery
from scripts.accounting_manager import add_transaction

@with_error_recovery
def safe_add_transaction(date, title, type, amount, description):
    return add_transaction(date, title, type, amount, description)
```

### CEO Briefing

```python
from scripts.error_recovery import with_error_recovery
from scripts.ceo_briefing import generate_ceo_briefing

@with_error_recovery
def safe_generate_briefing():
    return generate_ceo_briefing()
```

### Email Sending

```python
from scripts.error_recovery import handle_error

def send_email_with_recovery(to, subject, body):
    try:
        send_email(to, subject, body)
    except Exception as e:
        handle_error(e, context="email_sending")
        # Optionally notify admin
        notify_admin(f"Email failed: {to}")
```

## Error Recovery Service

### Start Service

```bash
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
[ERROR] Task permanently failed after 1 retries: email_sending.send_email
```

### Service Features

- Runs continuously in background
- Checks retry queue every 60 seconds
- Automatically retries eligible tasks
- Marks permanently failed tasks
- Comprehensive logging
- Graceful shutdown on Ctrl+C

## Failed File Management

Files that cause errors are moved to `AI_Employee_Vault/Errors/`:

```
AI_Employee_Vault/Errors/
├── 20260303_160000_input.csv
├── 20260303_160530_data.json
└── 20260303_161200_report.md
```

Filename format: `YYYYMMDD_HHMMSS_originalname.ext`

This allows:
- Easy identification of when file failed
- Preservation of original filename
- Chronological sorting
- Manual inspection and recovery

## Error Types Handled

The system handles all Python exceptions:

- **FileNotFoundError** - Missing files
- **PermissionError** - Access denied
- **ValueError** - Invalid values
- **TypeError** - Type mismatches
- **KeyError** - Missing dictionary keys
- **ConnectionError** - Network failures
- **TimeoutError** - Operation timeouts
- **Exception** - All other errors

## Retry Logic

### First Attempt
1. Error occurs
2. Log to errors.log
3. Move file to Errors/
4. Add to retry queue
5. Schedule retry in 5 minutes

### Retry Attempt (After 5 Minutes)
1. Check if file still exists
2. Attempt operation again
3. If success: Remove from queue
4. If fail: Mark permanently failed

### Permanent Failure
- After 1 retry attempt fails
- Task marked as "permanently_failed"
- Remains in queue for audit
- Logged for manual review

## Monitoring

### Check Error Log

```bash
# View recent errors
tail -50 logs/errors.log

# Watch errors in real-time
tail -f logs/errors.log
```

### Check Retry Queue

```bash
# View retry queue
cat logs/retry_queue.json

# Pretty print
python -m json.tool logs/retry_queue.json
```

### Check Failed Files

```bash
# List failed files
ls -lh AI_Employee_Vault/Errors/

# Count failed files
ls AI_Employee_Vault/Errors/ | wc -l
```

## Performance

- **CPU Usage:** Minimal (event-driven)
- **Memory Usage:** Low (< 50MB)
- **Disk I/O:** Minimal (log writes only)
- **Service Overhead:** ~1% CPU when idle
- **Retry Delay:** 5 minutes (configurable)

## Security Considerations

- **Error Logs:** May contain sensitive data (secure logs/)
- **Failed Files:** Quarantined but not encrypted
- **Stack Traces:** May reveal code structure
- **Retry Queue:** Contains task context
- **Access Control:** Restrict access to Errors directory

## Troubleshooting

### Service Won't Start
- Check Python version (3.7+)
- Verify directories exist
- Check file permissions
- Review logs/actions.log

### Retries Not Working
- Verify service is running
- Check retry_queue.json exists
- Ensure retry_at time has passed
- Review error logs for details

### Files Not Moving to Errors
- Check file exists before error
- Verify write permissions on Errors/
- Check disk space
- Review logs/actions.log

### Queue Growing Too Large
- Review permanently failed tasks
- Clear old tasks: `--clear-queue`
- Investigate root causes
- Fix underlying issues

## Dependencies

- Python 3.7+
- Standard library only (no external dependencies)
- Compatible with all existing AI Employee systems

## Future Enhancements

- Email notifications on permanent failures
- Slack/Teams integration for alerts
- Configurable retry strategies (exponential backoff)
- Error pattern detection
- Automatic root cause analysis
- Dashboard for error visualization
- Custom retry handlers per error type
- Error recovery playbooks

## Notes

- Designed for production reliability
- Zero external dependencies
- Minimal performance overhead
- Integrates seamlessly with existing skills
- Comprehensive logging and tracking
- Easy to monitor and debug
- Graceful degradation on failures
