# CEO Briefing - Quick Reference

## Generate Briefing

### Automatic (Every Sunday 9am UTC)
Runs automatically via GitHub Actions

### Manual Generation
```bash
python scripts/platinum_ceo_briefing.py
```

## View Briefings

### Latest Briefing
```bash
# List all briefings
ls -t AI_Employee_Vault/Briefings/

# View latest
cat AI_Employee_Vault/Briefings/$(ls -t AI_Employee_Vault/Briefings/ | head -1)
```

### Specific Briefing
```bash
cat AI_Employee_Vault/Briefings/2026-03-14_CEO_Briefing.md
```

## Data Sources

1. **Completed Tasks** - `AI_Employee_Vault/Done/`
   - Tasks completed in last 7 days
   - Email and social metrics

2. **Accounting** - `AI_Employee_Vault/Accounting/Current_Month.md`
   - Revenue, expenses, profit

3. **System Health** - `AI_Employee_Vault/Logs/system_health.md`
   - Errors, alerts, status

## Briefing Sections

1. Executive Summary
2. Key Metrics
3. Operational Highlights
4. Financial Summary
5. System Health
6. Action Items
7. Outlook

## Troubleshooting

### Briefing Not Generated
```bash
# Check workflow
gh run list --workflow=ceo-briefing.yml

# Trigger manually
gh workflow run ceo-briefing.yml

# Check logs
gh run view --log
```

### Missing Data
```bash
# Check Done folder
ls AI_Employee_Vault/Done/

# Check accounting
cat AI_Employee_Vault/Accounting/Current_Month.md

# Check health
cat AI_Employee_Vault/Logs/system_health.md
```

### API Error
- Verify ANTHROPIC_API_KEY in GitHub Secrets
- Check API quota at console.anthropic.com
- Script uses fallback if API fails

## Customization

### Change Schedule
Edit `.github/workflows/ceo-briefing.yml`:
```yaml
cron: '0 9 * * 0'  # Sunday 9am
# Change to:
cron: '0 9 * * 1'  # Monday 9am
```

### Add Custom Metrics
Edit `scripts/platinum_ceo_briefing.py`:
```python
def read_custom_data(self):
    # Add your custom data source
    pass
```

## Full Documentation

See: `docs/CEO_BRIEFING_GUIDE.md`
