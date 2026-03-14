# GitHub Actions Setup Guide - 24/7 Cloud Automation

## Overview

Your Platinum Tier AI Employee now runs 24/7 in the cloud via GitHub Actions:

- **Cloud Agent** (every 15 min): Email triage + social post drafts
- **Health Monitor** (every 5 min): System status checks
- **CEO Briefing** (Sundays 9am): Weekly summary reports
- **Vault Sync** (every 2 min): Repository synchronization

## Required GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

### 1. ANTHROPIC_API_KEY (Required)
- Your Claude API key from console.anthropic.com
- Used by all AI workflows

### 2. GMAIL_CREDENTIALS (Optional - for email triage)
- Your Gmail OAuth credentials JSON
- Get from Google Cloud Console
- Base64 encode before adding: `cat credentials.json | base64`

### 3. GMAIL_TOKEN (Optional - for email triage)
- Your Gmail OAuth token JSON
- Generated after first authentication
- Base64 encode before adding: `cat token.json | base64`

## Workflow Details

### 🤖 Cloud Agent (`cloud-agent.yml`)
**Schedule:** Every 15 minutes
**Purpose:** Autonomous email and social media management

**What it does:**
1. Checks Gmail for new emails
2. Triages emails using Claude
3. Creates draft replies in `/Needs_Action/email/`
4. Generates social post ideas in `/Needs_Action/social/`
5. Commits drafts to repository

**Manual trigger:**
```bash
gh workflow run cloud-agent.yml
```

### 📊 Health Monitor (`health-monitor.yml`)
**Schedule:** Every 5 minutes
**Purpose:** System health monitoring

**What it does:**
1. Checks status of all workflows
2. Queries GitHub Actions API
3. Writes status to `/vault/Logs/system_health.md`
4. Commits health report

**Manual trigger:**
```bash
gh workflow run health-monitor.yml
```

### 📈 CEO Briefing (`ceo-briefing.yml`)
**Schedule:** Every Sunday at 9:00 AM UTC
**Purpose:** Weekly executive summary

**What it does:**
1. Reads completed tasks from `/Done` folder
2. Analyzes weekly accomplishments
3. Generates executive briefing with Claude
4. Saves to `/vault/Briefings/YYYY-WXX.md`
5. Commits briefing

**Manual trigger:**
```bash
gh workflow run ceo-briefing.yml
```

### 🔄 Vault Sync (`vault-sync.yml`)
**Schedule:** Every 2 minutes
**Purpose:** Keep repository synchronized

**What it does:**
1. Pulls latest changes from remote
2. Prevents merge conflicts with rebase
3. Verifies no sensitive files (.env, tokens) are tracked
4. Pushes any local changes
5. Maintains clean git history

**Manual trigger:**
```bash
gh workflow run vault-sync.yml
```

## Setup Steps

### Step 1: Add ANTHROPIC_API_KEY
```bash
# Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions
# Click "New repository secret"
# Name: ANTHROPIC_API_KEY
# Value: sk-ant-api03-...
```

### Step 2: Enable GitHub Actions
1. Go to repository → Actions tab
2. Click "I understand my workflows, go ahead and enable them"
3. Workflows will start running on schedule

### Step 3: Test Workflows Manually
```bash
# Test cloud agent
gh workflow run cloud-agent.yml

# Test health monitor
gh workflow run health-monitor.yml

# Test vault sync
gh workflow run vault-sync.yml

# Test CEO briefing
gh workflow run ceo-briefing.yml
```

### Step 4: Monitor Workflow Runs
```bash
# View all workflow runs
gh run list

# View specific workflow
gh run list --workflow=cloud-agent.yml

# Watch a running workflow
gh run watch
```

## Monitoring & Logs

### View System Health
Check `/vault/Logs/system_health.md` for real-time status of all workflows.

### View Workflow Logs
```bash
# List recent runs
gh run list --limit 5

# View logs for specific run
gh run view RUN_ID --log
```

### GitHub Actions Dashboard
Visit: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`

## Troubleshooting

### Workflow Not Running
- Check if Actions are enabled in repository settings
- Verify cron schedule syntax
- Check workflow file syntax with `yamllint`

### API Key Issues
```bash
# Verify secret is set
gh secret list

# Update secret
gh secret set ANTHROPIC_API_KEY < api_key.txt
```

### Permission Issues
- Ensure `GITHUB_TOKEN` has write permissions
- Go to Settings → Actions → General → Workflow permissions
- Select "Read and write permissions"

### Email Triage Not Working
- Add `GMAIL_CREDENTIALS` and `GMAIL_TOKEN` secrets
- Ensure credentials are base64 encoded
- Check workflow logs for authentication errors

## Cost Considerations

### GitHub Actions
- Free tier: 2,000 minutes/month for private repos
- Public repos: Unlimited free minutes
- Each workflow run ~1-2 minutes

**Estimated monthly usage:**
- Cloud Agent: 2,880 runs × 2 min = 5,760 min
- Health Monitor: 8,640 runs × 1 min = 8,640 min
- Vault Sync: 21,600 runs × 1 min = 21,600 min
- CEO Briefing: 4 runs × 2 min = 8 min
- **Total: ~36,000 minutes/month**

**Recommendation:** Use a public repository or upgrade to GitHub Pro/Team.

### Claude API
- Cloud Agent: ~2,880 API calls/month
- CEO Briefing: ~4 API calls/month
- Estimated cost: $50-100/month depending on usage

## Customization

### Change Schedule
Edit the cron expression in workflow files:

```yaml
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
```

Cron syntax:
- `*/15 * * * *` - Every 15 minutes
- `0 */2 * * *` - Every 2 hours
- `0 9 * * 0` - Every Sunday at 9am
- `0 0 * * *` - Daily at midnight

### Disable Workflow
Add to workflow file:
```yaml
on:
  workflow_dispatch:  # Manual only, no schedule
```

### Add Notifications
Add Slack/Discord webhook step:
```yaml
- name: Notify completion
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -d '{"text":"Cloud agent completed"}'
```

## Security Best Practices

1. **Never commit secrets** - Always use GitHub Secrets
2. **Rotate API keys** - Change keys every 90 days
3. **Monitor usage** - Check Actions tab regularly
4. **Limit permissions** - Use minimal token scopes
5. **Review logs** - Check for suspicious activity

## Next Steps

1. ✅ Add `ANTHROPIC_API_KEY` to GitHub Secrets
2. ✅ Enable GitHub Actions in repository
3. ✅ Test workflows manually
4. ✅ Monitor first automated runs
5. ✅ Review `/Needs_Action/` for generated drafts
6. ✅ Check `/vault/Logs/system_health.md` for status

Your Platinum Tier AI Employee is now running 24/7 in the cloud! 🚀
