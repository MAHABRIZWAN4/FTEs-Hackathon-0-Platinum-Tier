# Dual-Agent System - Quick Reference

## Architecture Overview

```
CLOUD AGENT (GitHub Actions)     LOCAL AGENT (Your Machine)
     │                                    │
     ├─> Drafts emails                   ├─> Approves & sends
     ├─> Drafts social posts             ├─> Approves & posts
     ├─> NEVER sends directly            ├─> Executes actions
     └─> Writes to vault                 └─> Updates dashboard
```

## Quick Commands

### Run Local Agent (Windows)
```
Double-click: scripts\run_local_agent.bat
```

### Run Local Agent (Command Line)
```bash
python scripts/local_agent.py
```

### Update Dashboard
```bash
python scripts/dashboard_updater.py
```

### Trigger Cloud Agent Manually
```bash
gh workflow run cloud-agent.yml
```

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/                      # New items
├── Needs_Action/
│   ├── email/                  # Email drafts (no approval needed)
│   └── social/                 # Social drafts (no approval needed)
├── Pending_Approval/
│   ├── email/                  # Email drafts awaiting approval
│   └── social/                 # Social drafts awaiting approval
├── In_Progress/
│   ├── cloud/                  # Cloud agent working
│   └── local/                  # Local agent working
├── Done/                       # Completed tasks
└── Updates/                    # Cloud status updates
```

## Task Flow

### Email Flow
```
1. Email arrives → Inbox/
2. Cloud triages → In_Progress/cloud/
3. Cloud drafts → Pending_Approval/email/
4. Local approves → In_Progress/local/
5. Local sends → Done/
```

### Social Post Flow
```
1. Request created → Plans/
2. Cloud generates → In_Progress/cloud/
3. Cloud drafts → Pending_Approval/social/
4. Local approves → In_Progress/local/
5. Local posts → Done/
```

## Key Principles

### 1. Claim-by-Move
Tasks are claimed by **moving files** between folders.
- Atomic operation (no race conditions)
- Git-friendly (no lock files)

### 2. Single-Writer Rule
Only **one agent** writes to each file.
- Cloud writes to `Updates/`
- Local writes to `Dashboard.md`
- Dashboard Updater merges them

### 3. Draft-Only Cloud
Cloud **never** sends or posts directly.
- Creates drafts only
- Writes approval requests
- Local executes final actions

## Responsibilities

### Cloud Agent
✅ Email triage
✅ Draft replies
✅ Generate social posts
✅ Write to vault
❌ Never sends/posts

### Local Agent
✅ Show approvals
✅ Execute sends/posts
✅ WhatsApp (local session)
✅ Payments (local credentials)
✅ Update dashboard

## Monitoring

### Check Pending Approvals
```bash
ls AI_Employee_Vault/Pending_Approval/email/
ls AI_Employee_Vault/Pending_Approval/social/
```

### View Logs
```bash
# Cloud agent log
cat AI_Employee_Vault/Logs/cloud_agent.log

# Local agent log
cat AI_Employee_Vault/Logs/local_agent.log

# Dashboard updater log
cat AI_Employee_Vault/Logs/dashboard_updater.log
```

### View Dashboard
```bash
cat AI_Employee_Vault/Dashboard.md
```

## Troubleshooting

### No Approvals Showing
- Check if files exist in `Pending_Approval/`
- Run local agent: `python scripts/local_agent.py`

### Cloud Not Creating Drafts
- Check ANTHROPIC_API_KEY in GitHub Secrets
- View workflow logs: `gh run list --workflow=cloud-agent.yml`

### Task Stuck in In_Progress
- Move back manually: `mv In_Progress/cloud/task.json Inbox/`

## Full Documentation

See: `docs/DUAL_AGENT_ARCHITECTURE.md`
