# Vault Sync - Quick Reference

## Local Sync (Windows)

### One-Click Sync
```
Double-click: scripts\vault_push.bat
```

### Command Line
```bash
python scripts/vault_sync.py
```

## What It Does

1. ✓ Pulls latest changes from GitHub
2. ✓ Auto-resolves merge conflicts (cloud wins for vault files)
3. ✓ Stages AI_Employee_Vault/ changes
4. ✓ Blocks sensitive files (.env, tokens)
5. ✓ Creates timestamped commit
6. ✓ Pushes to GitHub
7. ✓ Logs everything to logs/sync.log

## Cloud Sync (Automatic)

- Runs every 2 minutes via GitHub Actions
- Workflow: `.github/workflows/vault-sync.yml`
- Manual trigger: `gh workflow run vault-sync.yml`

## Security

### Never Synced (Blocked by .gitignore)
- `.env` - Environment variables
- `*.token` - Authentication tokens
- `token.json` - OAuth tokens
- `credentials.json` - API credentials
- `*_session*` - Session files
- `logs/browser_profile/` - Browser data
- `logs/screenshots/` - May contain sensitive info

### Auto-Detection
Script automatically detects and blocks sensitive files before commit.

## Logs

**Location:** `logs/sync.log`

**View recent syncs:**
```bash
tail -20 logs/sync.log
```

## Troubleshooting

### Merge Conflict
Script auto-resolves using remote version for vault files.

### Authentication Error
```bash
gh auth login
```

### Sensitive File Detected
Script automatically unstages and warns you.

## Full Documentation

See: `docs/VAULT_SYNC_GUIDE.md`
