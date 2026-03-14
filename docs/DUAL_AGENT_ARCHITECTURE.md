# Dual-Agent Architecture - Cloud vs Local Work Zones

## Overview

The Platinum Tier AI Employee uses a **dual-agent architecture** with clear separation of responsibilities between cloud and local environments.

```
┌─────────────────────────────────────────────────────────────────┐
│                     DUAL-AGENT SYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐         ┌──────────────────────┐     │
│  │   CLOUD AGENT        │         │   LOCAL AGENT        │     │
│  │   (GitHub Actions)   │         │   (Your Machine)     │     │
│  ├──────────────────────┤         ├──────────────────────┤     │
│  │ • Email triage       │         │ • Approvals          │     │
│  │ • Draft replies      │────────>│ • Final send/post    │     │
│  │ • Draft social posts │         │ • WhatsApp           │     │
│  │ • Write to vault     │         │ • Payments/banking   │     │
│  │ • NEVER sends        │         │ • Dashboard updates  │     │
│  └──────────────────────┘         └──────────────────────┘     │
│           │                                 │                    │
│           └────────────┬────────────────────┘                    │
│                        │                                         │
│                   ┌────▼─────┐                                  │
│                   │  VAULT   │                                  │
│                   │  (Git)   │                                  │
│                   └──────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture Principles

### 1. Claim-by-Move Rule
Tasks are claimed by **moving files** between folders, not by locking mechanisms.

```
Needs_Action/email/task.json
    ↓ (Agent claims by moving)
In_Progress/cloud/task.json
    ↓ (Agent completes)
Pending_Approval/email/task.json
```

**Why?** Git naturally handles file moves atomically. If two agents try to move the same file, one will fail gracefully.

### 2. Single-Writer Rule
Only **one agent** writes to each file to prevent conflicts.

- **Dashboard.md**: Only Local Agent writes
- **Cloud updates**: Written to `/Updates/` folder
- **Dashboard Updater**: Merges updates into Dashboard.md

**Why?** Prevents merge conflicts in Git. Cloud writes updates to separate files, Local merges them.

### 3. Draft-Only Cloud
Cloud agent **never** sends emails or posts to social media directly.

- Cloud creates drafts
- Cloud writes approval requests
- Local executes final actions

**Why?** Keeps sensitive operations (sending emails, posting) on your local machine where you have control.

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/                      # New items (both agents read)
├── Needs_Action/
│   ├── email/                  # Email drafts ready for action
│   └── social/                 # Social post drafts ready for action
├── Pending_Approval/
│   ├── email/                  # Email drafts awaiting approval
│   └── social/                 # Social post drafts awaiting approval
├── Approved/                   # Approved items (temporary)
├── In_Progress/
│   ├── cloud/                  # Cloud agent working on these
│   └── local/                  # Local agent working on these
├── Done/                       # Completed tasks
├── Updates/                    # Cloud status updates (for Dashboard)
├── Signals/                    # Inter-agent communication
├── Logs/                       # Agent logs
└── Briefings/                  # CEO briefings
```

## Cloud Agent Responsibilities

**Script:** `scripts/cloud_agent.py`
**Runs:** GitHub Actions every 15 minutes
**Workflow:** `.github/workflows/cloud-agent.yml`

### What Cloud Does

1. **Email Triage**
   - Reads new emails from Inbox
   - Uses Claude to analyze priority and category
   - Generates draft replies
   - Writes to `Pending_Approval/email/` or `Needs_Action/email/`

2. **Social Post Generation**
   - Reads social post requests from Plans
   - Uses Claude to generate engaging content
   - Writes to `Pending_Approval/social/` or `Needs_Action/social/`

3. **Status Updates**
   - Writes activity to `Updates/` folder
   - Never writes to Dashboard.md directly

### What Cloud NEVER Does

- ❌ Send emails
- ❌ Post to social media
- ❌ Access WhatsApp
- ❌ Make payments
- ❌ Update Dashboard.md directly

### Claim-by-Move Example (Cloud)

```python
# Cloud agent claims task
task_file = Path("Inbox/email_123.json")
claimed_path = Path("In_Progress/cloud/email_123.json")

# Atomic move (claim)
shutil.move(task_file, claimed_path)

# Process task...

# Release to Pending_Approval
final_path = Path("Pending_Approval/email/email_123.json")
shutil.move(claimed_path, final_path)
```

## Local Agent Responsibilities

**Script:** `scripts/local_agent.py`
**Runs:** Manually on your machine
**Command:** `python scripts/local_agent.py`

### What Local Does

1. **Approval Workflow**
   - Monitors `Pending_Approval/` folders
   - Shows approval requests with Rich UI
   - Requests user approval
   - Executes approved actions

2. **Final Execution**
   - Sends approved emails via `send_email.py`
   - Posts approved content via platform scripts
   - Handles WhatsApp (local session required)
   - Manages payments/banking (local credentials)

3. **Dashboard Management**
   - Runs `dashboard_updater.py`
   - Merges cloud updates from `Updates/`
   - Writes final Dashboard.md (single-writer)

### What Local NEVER Does

- ❌ Run in cloud (requires local credentials)
- ❌ Auto-send without approval
- ❌ Process tasks already claimed by cloud

### Claim-by-Move Example (Local)

```python
# Local agent claims approval task
task_file = Path("Pending_Approval/email/email_123.json")
claimed_path = Path("In_Progress/local/email_123.json")

# Atomic move (claim)
shutil.move(task_file, claimed_path)

# Show approval UI and get user decision...

if approved:
    # Move to Approved
    approved_path = Path("Approved/email_123.json")
    shutil.move(claimed_path, approved_path)

    # Execute send
    send_email(draft_data)

    # Move to Done
    done_path = Path("Done/email_123.json")
    shutil.move(approved_path, done_path)
else:
    # Rejected - move back to Pending
    shutil.move(claimed_path, task_file)
```

## Dashboard Updater

**Script:** `scripts/dashboard_updater.py`
**Called by:** Local Agent
**Purpose:** Single-writer rule enforcement

### How It Works

1. **Collect Updates**
   - Reads all files from `Updates/` folder
   - Each file is a cloud agent status update

2. **Merge Updates**
   - Combines cloud updates with local status
   - Counts pending items across folders
   - Generates activity timeline

3. **Write Dashboard**
   - Writes final Dashboard.md (single-writer)
   - Archives processed updates to `Updates/processed/`

### Single-Writer Rule

```
Cloud Agent                    Local Agent
     │                              │
     ├─> Updates/cloud_001.json     │
     ├─> Updates/cloud_002.json     │
     │                              │
     │                         ┌────▼────┐
     │                         │Dashboard│
     │                         │ Updater │
     │                         └────┬────┘
     │                              │
     │                         Dashboard.md
```

**Why?** Only one writer prevents merge conflicts. Cloud writes to separate update files, Local merges them.

## Task Lifecycle

### Email Task Lifecycle

```
1. Email arrives
   └─> Inbox/email_123.json

2. Cloud claims and triages
   └─> In_Progress/cloud/email_123.json
   └─> (Cloud processes with Claude)

3. Cloud creates draft
   └─> Pending_Approval/email/email_123.json

4. Local claims for approval
   └─> In_Progress/local/email_123.json
   └─> (User reviews and approves)

5. Local executes send
   └─> Approved/email_123.json
   └─> (Send via send_email.py)

6. Complete
   └─> Done/email_123.json
```

### Social Post Task Lifecycle

```
1. Post request created
   └─> Plans/social_request_123.json

2. Cloud claims and generates
   └─> In_Progress/cloud/social_request_123.json
   └─> (Cloud generates with Claude)

3. Cloud creates draft
   └─> Pending_Approval/social/social_linkedin_123.json

4. Local claims for approval
   └─> In_Progress/local/social_linkedin_123.json
   └─> (User reviews and approves)

5. Local executes post
   └─> Approved/social_linkedin_123.json
   └─> (Post via post_linkedin.py)

6. Complete
   └─> Done/social_linkedin_123.json
```

## Conflict Resolution

### Race Conditions
**Problem:** Two agents try to claim the same task

**Solution:** Claim-by-move is atomic
```python
try:
    shutil.move(task_file, claimed_path)
    # Success - we claimed it
except FileNotFoundError:
    # Another agent claimed it first
    return None
```

### Merge Conflicts
**Problem:** Both agents modify the same file

**Solution:** Single-writer rule
- Cloud writes to `Updates/`
- Local writes to `Dashboard.md`
- Never both write to same file

### Lost Updates
**Problem:** Update file not processed

**Solution:** Archive processed updates
```
Updates/cloud_001.json
    ↓ (After processing)
Updates/processed/cloud_001.json
```

## Running the System

### Cloud Agent (Automatic)

Runs automatically via GitHub Actions every 15 minutes.

**Manual trigger:**
```bash
gh workflow run cloud-agent.yml
```

**View logs:**
```bash
gh run list --workflow=cloud-agent.yml
gh run view RUN_ID --log
```

### Local Agent (Manual)

Run on your local machine when you want to process approvals.

**Command:**
```bash
python scripts/local_agent.py
```

**What happens:**
1. Shows pending email approvals
2. Shows pending social post approvals
3. Requests your approval for each
4. Executes approved actions
5. Updates dashboard

### Dashboard Updater (Automatic)

Called automatically by Local Agent.

**Manual run:**
```bash
python scripts/dashboard_updater.py
```

## Security Model

### Cloud Environment
- Has ANTHROPIC_API_KEY (for Claude)
- Has GMAIL_CREDENTIALS (read-only)
- **NO** send permissions
- **NO** social media tokens
- **NO** payment credentials

### Local Environment
- Has all credentials
- Has send permissions
- Has social media tokens
- Has payment access
- **Requires user approval** for sensitive actions

### Why This Split?

1. **Reduced attack surface**: Cloud can't send/post even if compromised
2. **User control**: All final actions require local approval
3. **Credential isolation**: Sensitive tokens stay on local machine
4. **Audit trail**: All actions logged and approved

## Monitoring

### Check Cloud Agent Status
```bash
# View recent runs
gh run list --workflow=cloud-agent.yml --limit 5

# View cloud agent log
cat AI_Employee_Vault/Logs/cloud_agent.log
```

### Check Local Agent Status
```bash
# View local agent log
cat AI_Employee_Vault/Logs/local_agent.log

# View dashboard
cat AI_Employee_Vault/Dashboard.md
```

### Check Pending Items
```bash
# Count pending approvals
ls AI_Employee_Vault/Pending_Approval/email/ | wc -l
ls AI_Employee_Vault/Pending_Approval/social/ | wc -l

# Count needs action
ls AI_Employee_Vault/Needs_Action/email/ | wc -l
ls AI_Employee_Vault/Needs_Action/social/ | wc -l
```

## Troubleshooting

### Cloud Agent Not Creating Drafts

**Check:**
1. Is ANTHROPIC_API_KEY set in GitHub Secrets?
2. Are there items in Inbox?
3. Check cloud agent logs

**Fix:**
```bash
gh workflow run cloud-agent.yml
gh run view --log
```

### Local Agent Not Showing Approvals

**Check:**
1. Are there files in Pending_Approval/?
2. Is local agent running?
3. Check local agent logs

**Fix:**
```bash
python scripts/local_agent.py
```

### Dashboard Not Updating

**Check:**
1. Is dashboard_updater.py being called?
2. Are there updates in Updates/ folder?
3. Check dashboard updater logs

**Fix:**
```bash
python scripts/dashboard_updater.py
```

### Task Stuck in In_Progress

**Problem:** Task claimed but not completed

**Fix:**
```bash
# Move back to appropriate folder
mv AI_Employee_Vault/In_Progress/cloud/task.json AI_Employee_Vault/Inbox/
# or
mv AI_Employee_Vault/In_Progress/local/task.json AI_Employee_Vault/Pending_Approval/email/
```

## Best Practices

1. **Run Local Agent Regularly**
   - Check for approvals 2-3 times per day
   - Don't let approvals pile up

2. **Monitor Logs**
   - Check cloud agent logs for errors
   - Review local agent logs after runs

3. **Clean Up Done Folder**
   - Archive old completed tasks monthly
   - Keep Done folder manageable

4. **Test Before Production**
   - Test email sends with test accounts
   - Test social posts with test content

5. **Backup Vault**
   - Git automatically backs up vault
   - Keep local copy of sensitive data

## Summary

| Feature | Cloud Agent | Local Agent |
|---------|-------------|-------------|
| **Location** | GitHub Actions | Your machine |
| **Frequency** | Every 15 min | Manual |
| **Email** | Triage & draft | Approve & send |
| **Social** | Generate drafts | Approve & post |
| **Credentials** | Read-only | Full access |
| **Approval** | Never | Always required |
| **Dashboard** | Write to Updates/ | Write to Dashboard.md |

The dual-agent architecture provides **security**, **control**, and **automation** while keeping you in the loop for all important decisions.
