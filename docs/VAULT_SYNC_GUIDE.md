# Vault Synchronization Guide - Platinum Tier

## Overview

Your Platinum Tier AI Employee uses a **Git-based vault synchronization system** to keep data synchronized between your local machine and the cloud (GitHub Actions).

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│  Local Machine  │ ◄─────► │    GitHub    │ ◄─────► │  Cloud Actions  │
│                 │  Push   │  Repository  │  Pull   │                 │
│  Manual Sync    │  Pull   │              │  Auto   │  Every 2 min    │
└─────────────────┘         └──────────────┘         └─────────────────┘
```

## How It Works

### Cloud (GitHub Actions)
**Workflow:** `.github/workflows/vault-sync.yml`
**Schedule:** Every 2 minutes
**Purpose:** Pull latest changes from repository

**What it does:**
1. Fetches latest changes from remote
2. Pulls with rebase to avoid merge commits
3. Verifies no sensitive files are tracked
4. Pushes any changes made by other workflows

### Local Machine
**Script:** `scripts/vault_sync.py`
**Trigger:** Manual (run `scripts/vault_push.bat`)
**Purpose:** Push local vault changes to repository

**What it does:**
1. Pulls latest changes from remote (with conflict resolution)
2. Stages changes in `AI_Employee_Vault/`
3. Creates timestamped commit
4. Pushes to remote repository
5. Logs all operations to `logs/sync.log`

## Sync Strategy

### Pull-Before-Push
Both local and cloud use **pull-before-push** to prevent conflicts:

```
1. Pull latest changes
2. Resolve any conflicts (if needed)
3. Stage local changes
4. Commit changes
5. Push to remote
```

### Conflict Resolution
When conflicts occur, the system uses this strategy:

- **Vault files** (`AI_Employee_Vault/*`): Accept **remote version** (cloud is source of truth)
- **Other files**: Accept **local version** (preserve local work)

This ensures vault data from cloud workflows takes precedence while protecting local code changes.

## Usage

### Local Sync (Windows)

**Option 1: Double-click batch file**
```
scripts\vault_push.bat
```

**Option 2: Run Python script directly**
```bash
python scripts/vault_sync.py
```

**Option 3: Command line**
```bash
cd "F:\FTEs\Platinum Tier"
python scripts\vault_sync.py
```

### Cloud Sync (Automatic)

Cloud sync runs automatically every 2 minutes via GitHub Actions.

**Manual trigger:**
```bash
gh workflow run vault-sync.yml
```

**View sync status:**
```bash
gh run list --workflow=vault-sync.yml --limit 5
```

## What Gets Synced

### ✅ Synced to Repository

- `AI_Employee_Vault/` - All vault contents
  - `Inbox/` - Incoming tasks
  - `Needs_Action/` - Pending actions
  - `Needs_Approval/` - Awaiting approval
  - `Done/` - Completed tasks
  - `Logs/` - Activity logs
  - `Plans/` - Task plans
  - `Reports/` - Generated reports
  - `Accounting/` - Financial data
  - `Personal/` - Personal tasks

- `scripts/` - Python scripts
- `docs/` - Documentation
- `.github/workflows/` - GitHub Actions
- `README.md` - Project documentation

### ❌ Never Synced (Security)

- `.env` - Environment variables
- `*.token` - Authentication tokens
- `token.json` - OAuth tokens
- `credentials.json` - API credentials
- `*_session*` - Session files
- `logs/browser_profile/` - Browser session data
- `logs/screenshots/` - May contain sensitive info
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python

These are blocked by `.gitignore` and will never be committed.

## Security Rules

### 🔒 Critical Security Practices

1. **Never commit secrets**
   - All credentials stay in `.env`
   - Use GitHub Secrets for cloud workflows
   - Check `.gitignore` before committing

2. **Verify before pushing**
   - Script automatically checks for sensitive files
   - Unstages any detected sensitive files
   - Logs warnings to `logs/sync.log`

3. **Rotate credentials regularly**
   - Change API keys every 90 days
   - Update GitHub Secrets when rotating
   - Never share `.env` file

4. **Monitor sync logs**
   - Check `logs/sync.log` for errors
   - Review GitHub Actions logs
   - Watch for unauthorized access

## Sync Logs

### Local Logs
**Location:** `logs/sync.log`

**Example:**
```
[2026-03-14 10:30:15] [INFO] Starting vault sync...
[2026-03-14 10:30:16] [INFO] Pulling latest changes from remote...
[2026-03-14 10:30:18] [SUCCESS] Successfully pulled latest changes
[2026-03-14 10:30:18] [INFO] Staging changes in AI_Employee_Vault/...
[2026-03-14 10:30:19] [SUCCESS] Changes staged successfully
[2026-03-14 10:30:19] [INFO] Creating commit...
[2026-03-14 10:30:20] [SUCCESS] Commit created successfully
[2026-03-14 10:30:20] [INFO] Pushing changes to remote...
[2026-03-14 10:30:22] [SUCCESS] Changes pushed successfully
[2026-03-14 10:30:22] [SUCCESS] Vault sync completed successfully!
```

### Cloud Logs
**Location:** GitHub Actions → vault-sync.yml → View logs

**Access:**
```bash
gh run list --workflow=vault-sync.yml
gh run view RUN_ID --log
```

## Troubleshooting

### Sync Failed: Merge Conflict

**Symptom:** Script reports merge conflict
**Solution:** Script auto-resolves using remote version for vault files

If auto-resolution fails:
```bash
# Abort current sync
git rebase --abort

# Pull with merge instead
git pull origin main

# Manually resolve conflicts
git status
# Edit conflicted files
git add .
git commit -m "Resolve merge conflict"

# Run sync again
python scripts/vault_sync.py
```

### Sync Failed: Authentication Error

**Symptom:** "Permission denied" or "Authentication failed"
**Solution:**

1. Check Git credentials:
```bash
git config --list | grep user
```

2. Re-authenticate:
```bash
gh auth login
```

3. Verify remote URL:
```bash
git remote -v
```

### Sync Failed: Sensitive File Detected

**Symptom:** Script reports sensitive file staged
**Solution:** Script automatically unstages the file

To manually check:
```bash
git status
git reset HEAD .env
git reset HEAD *.token
```

### Cloud Sync Not Running

**Symptom:** No recent runs in GitHub Actions
**Solution:**

1. Check if Actions are enabled:
   - Go to repository → Settings → Actions
   - Ensure "Allow all actions" is selected

2. Verify workflow file:
```bash
cat .github/workflows/vault-sync.yml
```

3. Manually trigger:
```bash
gh workflow run vault-sync.yml
```

### Local Sync Hangs

**Symptom:** Script doesn't complete
**Solution:**

1. Check network connection
2. Verify Git is installed: `git --version`
3. Check for large files: `git status`
4. Cancel with Ctrl+C and retry

## Best Practices

### When to Sync Locally

- **After making changes** to vault files
- **Before starting work** (pull latest)
- **End of work session** (push changes)
- **Before running cloud workflows** (ensure latest data)

### Sync Frequency

- **Local:** As needed (manual)
- **Cloud:** Every 2 minutes (automatic)
- **Recommended:** Sync locally 2-3 times per day

### Workflow Integration

1. **Morning:** Pull latest changes
   ```bash
   git pull origin main
   ```

2. **During work:** Make changes to vault
   ```
   AI_Employee_Vault/Needs_Action/task.md
   ```

3. **End of day:** Push changes
   ```bash
   scripts\vault_push.bat
   ```

4. **Cloud:** Automatically syncs every 2 minutes

## Monitoring Sync Health

### Check Last Sync Time

**Local:**
```bash
git log -1 --format="%ai %s"
```

**Cloud:**
```bash
gh run list --workflow=vault-sync.yml --limit 1
```

### View Sync History

**Local:**
```bash
git log --oneline --grep="Vault sync" -10
```

**Cloud:**
```bash
gh run list --workflow=vault-sync.yml --limit 10
```

### Check Sync Status

**Local:**
```bash
git status
```

**Cloud:**
Check `vault/Logs/system_health.md` for workflow status

## Advanced Configuration

### Change Sync Interval (Cloud)

Edit `.github/workflows/vault-sync.yml`:
```yaml
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes (instead of 2)
```

### Customize Conflict Resolution

Edit `scripts/vault_sync.py`:
```python
# Line ~120: Change conflict resolution strategy
if file.startswith(VAULT_DIR):
    # Accept local version instead
    run_command(f'git checkout --ours "{file}"')
```

### Add Pre-Sync Hook

Create `scripts/pre_sync.py`:
```python
# Run before sync
# Example: Backup vault, validate data, etc.
```

Update `vault_sync.py`:
```python
# Add before main sync
import pre_sync
pre_sync.run()
```

## FAQ

**Q: What happens if local and cloud sync at the same time?**
A: Git handles this automatically. The second push will be rejected and will pull-rebase-push.

**Q: Can I disable cloud sync temporarily?**
A: Yes, disable the workflow in GitHub Actions settings or delete the workflow file.

**Q: What if I accidentally commit a secret?**
A: Remove it immediately:
```bash
git rm --cached .env
git commit -m "Remove secret"
git push
# Then rotate the compromised credential
```

**Q: How do I sync from multiple machines?**
A: Run `vault_sync.py` on each machine. Always pull before making changes.

**Q: Can I use this with other Git providers (GitLab, Bitbucket)?**
A: Yes, but you'll need to adapt the GitHub Actions workflows to your provider's CI/CD system.

## Summary

- **Cloud pulls** every 2 minutes (automatic)
- **Local pushes** manually via `vault_push.bat`
- **Pull-before-push** prevents conflicts
- **Auto-resolution** handles merge conflicts
- **Security checks** prevent committing secrets
- **Logs everything** to `logs/sync.log`

Your vault stays synchronized 24/7 between local and cloud! 🚀
