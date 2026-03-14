# Health Monitoring - Quick Reference

## Quick Commands

### Check System Health
```bash
python scripts/health_check.py
```
Or double-click: `scripts\run_health_check.bat`

### Start Watchdog (Continuous Monitoring)
```bash
python scripts/watchdog.py
```
Or double-click: `scripts\run_watchdog.bat`

### Run Watchdog Once
```bash
python scripts/watchdog.py --once
```

## What Gets Monitored

### Local Processes
- watch_gmail.py (auto-restart enabled)
- watch_inbox.py (auto-restart enabled)

### GitHub Actions Workflows
- cloud-agent.yml (every 15 min)
- health-monitor.yml (every 5 min)
- vault-sync.yml (every 2 min)
- ceo-briefing.yml (Sundays 9am)

### Vault Metrics
- Pending approvals (email/social)
- Needs action (email/social)
- In progress (cloud/local)
- Completed today

### System Status
- Last vault sync time
- Errors in last hour
- Total pending actions

## Health Report Location

```
AI_Employee_Vault/Logs/system_health.md
```

View with:
```bash
cat AI_Employee_Vault/Logs/system_health.md
```

## Logs

```bash
# Watchdog log
cat AI_Employee_Vault/Logs/watchdog.log

# Cloud agent log
cat AI_Employee_Vault/Logs/cloud_agent.log

# Local agent log
cat AI_Employee_Vault/Logs/local_agent.log

# Follow in real-time
tail -f AI_Employee_Vault/Logs/watchdog.log
```

## Alerts

### High Error Rate
**Threshold:** >10 errors/hour
**Action:** Check logs for error details

### High Pending Approvals
**Threshold:** >20 items
**Action:** Run local agent

### Stuck Tasks
**Threshold:** >10 in progress
**Action:** Check In_Progress folders

### Process Stopped
**Action:** Auto-restart + alert

### Workflow Failed
**Action:** Check GitHub Actions logs

## Troubleshooting

### Start Watchdog
```bash
python scripts/watchdog.py
```

### Check Process Status
```bash
# Windows
tasklist | findstr python

# Linux/Mac
ps aux | grep watchdog
```

### View Recent Errors
```bash
grep ERROR AI_Employee_Vault/Logs/*.log | tail -20
```

### Manually Update Health Report
```bash
python scripts/watchdog.py --once
```

## Full Documentation

See: `docs/HEALTH_MONITORING_GUIDE.md`
