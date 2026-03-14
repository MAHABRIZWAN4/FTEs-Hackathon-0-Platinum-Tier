# Health Monitoring System - Platinum Tier

## Overview

The Platinum Tier AI Employee includes a comprehensive health monitoring system that tracks all agents, workflows, and system metrics.

```
┌─────────────────────────────────────────────────────────────────┐
│                  HEALTH MONITORING SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐         ┌──────────────────────┐     │
│  │   WATCHDOG           │         │   HEALTH CHECK       │     │
│  │   (Continuous)       │         │   (On-Demand)        │     │
│  ├──────────────────────┤         ├──────────────────────┤     │
│  │ • Monitors processes │         │ • Quick status       │     │
│  │ • Auto-restarts      │         │ • Pending tasks      │     │
│  │ • Every 5 minutes    │         │ • GitHub Actions     │     │
│  │ • Writes health.md   │         │ • Rich UI output     │     │
│  └──────────────────────┘         └──────────────────────┘     │
│           │                                 │                    │
│           └────────────┬────────────────────┘                    │
│                        │                                         │
│                   ┌────▼─────┐                                  │
│                   │  HEALTH  │                                  │
│                   │  REPORT  │                                  │
│                   └──────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Watchdog (`scripts/watchdog.py`)

**Purpose:** Continuous process monitoring with auto-restart

**What it monitors:**
- Local Python processes (watch_gmail.py, watch_inbox.py)
- GitHub Actions workflows (via gh CLI)
- Vault folder metrics
- Error counts from logs

**Features:**
- Auto-restart stopped processes
- Runs every 5 minutes
- Writes comprehensive health report
- Logs all actions to `AI_Employee_Vault/Logs/watchdog.log`

**Usage:**
```bash
# Run continuously (recommended)
python scripts/watchdog.py

# Run once and exit
python scripts/watchdog.py --once
```

### 2. Health Check (`scripts/health_check.py`)

**Purpose:** Quick on-demand system status check

**What it shows:**
- GitHub Actions workflow status
- Pending task counts
- Last vault sync time
- System alerts

**Features:**
- Rich UI with tables and colors
- Quick overview of system health
- No auto-restart (read-only)
- Instant feedback

**Usage:**
```bash
python scripts/health_check.py
```

### 3. GitHub Actions Health Monitor

**Workflow:** `.github/workflows/health-monitor.yml`
**Schedule:** Every 5 minutes

**What it does:**
- Runs health_check.py in cloud
- Commits health status to repository
- Provides cloud-side monitoring

## Health Report Format

**Location:** `AI_Employee_Vault/Logs/system_health.md`

**Sections:**

1. **Local Processes**
   - Process name
   - Status (RUNNING/STOPPED)
   - Auto-restart enabled

2. **GitHub Actions Workflows**
   - Workflow name
   - Status (success/failure/in_progress)

3. **Vault Metrics**
   - Pending approvals (email/social)
   - Needs action (email/social)
   - In progress (cloud/local)
   - Completed today

4. **System Status**
   - Last vault sync time
   - Errors in last hour
   - Total pending actions
   - Total in progress

5. **Alerts**
   - High error rate warnings
   - High pending approval warnings
   - Stuck task warnings
   - Process/workflow failures

## Running the System

### Start Watchdog (Recommended)

**Windows:**
```bash
# Start in background
start /B python scripts/watchdog.py
```

**Linux/Mac:**
```bash
# Start in background
nohup python scripts/watchdog.py &
```

**Keep running:**
The watchdog should run continuously in the background. It will:
- Check system health every 5 minutes
- Auto-restart stopped processes
- Write health reports
- Log all actions

### Quick Health Check

```bash
# Run anytime for instant status
python scripts/health_check.py
```

**Output example:**
```
═══════════════════════════════════════════════════
  System Health Check - Platinum Tier AI Employee
═══════════════════════════════════════════════════

☁️ GitHub Actions Workflows
┌─────────────────┬──────────┬─────────────────────┐
│ Workflow        │ Status   │ Last Run            │
├─────────────────┼──────────┼─────────────────────┤
│ Cloud Agent     │ ✓ Success│ 2026-03-14 09:30:00 │
│ Health Monitor  │ ✓ Success│ 2026-03-14 09:35:00 │
│ Vault Sync      │ ✓ Success│ 2026-03-14 09:36:00 │
└─────────────────┴──────────┴─────────────────────┘

📋 Pending Tasks
┌──────────────────────────┬───────┐
│ Category                 │ Count │
├──────────────────────────┼───────┤
│ Pending Approval (Email) │     3 │
│ Pending Approval (Social)│     1 │
│ Needs Action (Email)     │     0 │
│ Needs Action (Social)    │     0 │
│ In Progress (Cloud)      │     0 │
│ In Progress (Local)      │     0 │
│                          │       │
│ Total Pending Approval   │     4 │
│ Total Needs Action       │     0 │
│ Total In Progress        │     0 │
└──────────────────────────┴───────┘

🚨 Alerts:
  ✅ All clear - No pending tasks
```

## Monitored Processes

### Local Processes

| Process | Script | Auto-Restart | Critical |
|---------|--------|--------------|----------|
| watch_gmail | scripts/watch_gmail.py | ✓ | No |
| watch_inbox | scripts/watch_inbox.py | ✓ | No |

**Note:** Cloud agent and local agent are NOT monitored by watchdog because:
- Cloud agent runs via GitHub Actions (monitored separately)
- Local agent runs on-demand (not a background service)

### GitHub Actions Workflows

| Workflow | Schedule | Monitored |
|----------|----------|-----------|
| cloud-agent | Every 15 min | ✓ |
| health-monitor | Every 5 min | ✓ |
| vault-sync | Every 2 min | ✓ |
| ceo-briefing | Sundays 9am | ✓ |

## Auto-Restart Behavior

### When Watchdog Restarts a Process

1. **Detection:** Watchdog checks if process is running
2. **Restart:** If stopped and auto-restart enabled, starts process
3. **Verification:** Waits 2 seconds and verifies process started
4. **Logging:** Logs restart action to watchdog.log

**Example log:**
```
[2026-03-14 09:30:15] [WARNING] watch_gmail is stopped, attempting restart...
[2026-03-14 09:30:17] [SUCCESS] Started watch_gmail (PID: 12345)
```

### When NOT to Auto-Restart

Watchdog will NOT restart:
- Processes that are intentionally stopped
- Processes that crash repeatedly (manual intervention needed)
- Processes not in MONITORED_PROCESSES config

## Alerts and Thresholds

### High Error Rate
**Threshold:** More than 10 errors in last hour
**Action:** Alert in health report
**Resolution:** Check logs for error details

### High Pending Approvals
**Threshold:** More than 20 items awaiting approval
**Action:** Alert in health report
**Resolution:** Run local agent to process approvals

### Stuck Tasks
**Threshold:** More than 10 tasks in progress
**Action:** Alert in health report
**Resolution:** Check In_Progress folders, move stuck tasks

### Process Stopped
**Threshold:** Any monitored process not running
**Action:** Auto-restart + alert
**Resolution:** Check process logs for crash reason

### Workflow Failed
**Threshold:** Any GitHub Actions workflow failed
**Action:** Alert in health report
**Resolution:** Check GitHub Actions logs

## Viewing Health Reports

### Latest Health Report
```bash
cat AI_Employee_Vault/Logs/system_health.md
```

### Watchdog Log
```bash
# View full log
cat AI_Employee_Vault/Logs/watchdog.log

# View last 20 lines
tail -20 AI_Employee_Vault/Logs/watchdog.log

# Follow log in real-time
tail -f AI_Employee_Vault/Logs/watchdog.log
```

### Cloud Agent Log
```bash
cat AI_Employee_Vault/Logs/cloud_agent.log
```

### Local Agent Log
```bash
cat AI_Employee_Vault/Logs/local_agent.log
```

## Troubleshooting

### Watchdog Not Running

**Check if running:**
```bash
# Windows
tasklist | findstr python

# Linux/Mac
ps aux | grep watchdog
```

**Start watchdog:**
```bash
python scripts/watchdog.py
```

### Process Won't Stay Running

**Check process log:**
```bash
cat AI_Employee_Vault/Logs/watch_gmail.log
```

**Common issues:**
- Missing credentials (.env file)
- Port already in use
- Permission denied
- Missing dependencies

**Fix:**
```bash
# Install dependencies
pip install -r requirements.txt

# Check .env file
cat .env

# Check permissions
ls -la scripts/
```

### Health Report Not Updating

**Check watchdog status:**
```bash
tail -20 AI_Employee_Vault/Logs/watchdog.log
```

**Manually trigger update:**
```bash
python scripts/watchdog.py --once
```

### GitHub Actions Not Showing

**Check gh CLI:**
```bash
gh auth status
```

**Login if needed:**
```bash
gh auth login
```

### High Error Count

**View errors:**
```bash
# Search for errors in logs
grep ERROR AI_Employee_Vault/Logs/*.log

# Count errors
grep -c ERROR AI_Employee_Vault/Logs/*.log
```

**Common errors:**
- API rate limits
- Authentication failures
- Network timeouts
- File permission issues

## Best Practices

### 1. Keep Watchdog Running

Run watchdog continuously in the background:
```bash
# Windows (start minimized)
start /MIN python scripts/watchdog.py

# Linux/Mac (with nohup)
nohup python scripts/watchdog.py > /dev/null 2>&1 &
```

### 2. Check Health Daily

Run health check at least once per day:
```bash
python scripts/health_check.py
```

### 3. Review Logs Weekly

Check logs for patterns:
```bash
# Count errors per day
grep ERROR AI_Employee_Vault/Logs/*.log | cut -d' ' -f1 | sort | uniq -c

# Find most common errors
grep ERROR AI_Employee_Vault/Logs/*.log | sort | uniq -c | sort -rn | head -10
```

### 4. Monitor Alerts

Pay attention to alerts in health report:
- High pending approvals → Run local agent
- Stuck tasks → Check In_Progress folders
- Process stopped → Check process logs
- Workflow failed → Check GitHub Actions

### 5. Clean Up Old Logs

Archive old logs monthly:
```bash
# Create archive directory
mkdir -p AI_Employee_Vault/Logs/archive

# Move old logs
mv AI_Employee_Vault/Logs/*.log.old AI_Employee_Vault/Logs/archive/
```

## Integration with Other Systems

### Dashboard Integration

Health metrics are automatically included in Dashboard.md via dashboard_updater.py.

### Slack/Discord Notifications (Optional)

Add webhook to watchdog.py for critical alerts:
```python
# In watchdog.py, add notification function
def send_alert(message):
    webhook_url = os.getenv("SLACK_WEBHOOK")
    if webhook_url:
        requests.post(webhook_url, json={"text": message})
```

### Email Alerts (Optional)

Configure email alerts for critical failures:
```python
# In watchdog.py, add email function
def send_email_alert(subject, body):
    # Use send_email.py to send alert
    pass
```

## Advanced Configuration

### Customize Check Interval

Edit `scripts/watchdog.py`:
```python
CHECK_INTERVAL = 300  # 5 minutes (default)
# Change to:
CHECK_INTERVAL = 600  # 10 minutes
```

### Add New Monitored Process

Edit `scripts/watchdog.py`:
```python
MONITORED_PROCESSES = {
    "watch_gmail": {
        "script": "scripts/watch_gmail.py",
        "auto_restart": True,
        "critical": False
    },
    # Add new process:
    "my_custom_agent": {
        "script": "scripts/my_custom_agent.py",
        "auto_restart": True,
        "critical": True
    }
}
```

### Customize Alert Thresholds

Edit `scripts/watchdog.py`:
```python
# Change thresholds in write_health_report method
if error_count > 10:  # Change to 20
    alerts.append("⚠️ HIGH ERROR RATE")

if metrics['pending_approval_email'] > 20:  # Change to 50
    alerts.append("⚠️ HIGH PENDING APPROVALS")
```

## Summary

The health monitoring system provides:

✅ Continuous process monitoring
✅ Auto-restart capabilities
✅ Comprehensive health reports
✅ Quick status checks
✅ GitHub Actions monitoring
✅ Alert system
✅ Detailed logging

**Quick Commands:**
```bash
# Start watchdog
python scripts/watchdog.py

# Quick health check
python scripts/health_check.py

# View health report
cat AI_Employee_Vault/Logs/system_health.md

# View watchdog log
tail -f AI_Employee_Vault/Logs/watchdog.log
```

Your system health is now fully monitored! 🏥
