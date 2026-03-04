# CEO Briefing Agent Skill

## Description
Automated weekly executive summary report generator for the Gold Tier AI Employee. Aggregates data from all systems (tasks, social media, finances, system health) into a comprehensive CEO briefing document.

## Trigger
- **Scheduled:** Automatically runs every Monday at 9:00 AM
- **Manual:** `python scripts/ceo_briefing.py`
- **Command:** `/ceo-briefing`
- **Programmatic:** Import and call `generate_ceo_briefing()`

## Capabilities
- Aggregate completed tasks from Done directory
- Track pending tasks from Needs_Action directory
- Monitor pending approvals from Needs_Approval directory
- Count LinkedIn posts from logs
- Summarize income/expenses from accounting ledger
- Calculate system health metrics from logs
- Generate actionable recommendations
- Auto-schedule weekly generation
- Archive historical reports

## Output

### Primary Report
**Location:** `AI_Employee_Vault/Reports/CEO_Weekly.md`

This file is always the latest briefing and gets overwritten each week.

### Archived Reports
**Location:** `AI_Employee_Vault/Reports/CEO_Weekly_YYYY-MM-DD.md`

Each week's report is also saved with a date stamp for historical reference.

## Report Structure

```markdown
# CEO Weekly Briefing

**Week of March 02 - March 08, 2026**
**Generated:** 2026-03-03 15:45:00

---

## Executive Summary
Brief overview of the week's performance

---

## 📋 Tasks & Productivity
- Completed tasks (with titles and dates)
- Pending tasks (grouped by priority)

---

## 🔔 Pending Approvals
- Items awaiting approval
- Days pending

---

## 📱 Social Media Activity
- LinkedIn posts count
- Post dates and times

---

## 💰 Financial Summary
- Total income
- Total expenses
- Net profit
- Profit margin

---

## 🔧 System Health
- Total operations
- Success rate
- Errors and warnings

---

## 📊 Key Metrics
Table with all key metrics at a glance

---

## 🎯 Recommendations
Actionable recommendations based on data

---

## 📁 Detailed Reports
Links to source data locations
```

## Data Sources

The CEO Briefing aggregates data from:

1. **Tasks Completed:** `AI_Employee_Vault/Done/*.md`
   - Files modified within the week
   - Extracts task titles and completion dates

2. **Pending Tasks:** `AI_Employee_Vault/Needs_Action/*.md`
   - Current pending tasks
   - Extracts priorities

3. **Pending Approvals:** `AI_Employee_Vault/Needs_Approval/*.md`
   - Items awaiting approval
   - Tracks how long they've been pending

4. **LinkedIn Posts:** `logs/actions.log`
   - Searches for `[LINKEDIN]` entries
   - Counts posts within the week

5. **Financial Data:** `AI_Employee_Vault/Accounting/Current_Month.md`
   - Extracts income, expenses, net profit
   - Counts transactions

6. **System Health:** `logs/actions.log`
   - Counts total operations
   - Tracks errors and warnings
   - Calculates success rate

## Functions

### generate_ceo_briefing(date=None)

Generate CEO weekly briefing report.

**Parameters:**
- `date` (datetime, optional): Reference date for the week (default: today)

**Returns:**
- `str`: Path to generated report

**Example:**
```python
from scripts.ceo_briefing import generate_ceo_briefing
from datetime import datetime

# Generate for current week
report_path = generate_ceo_briefing()

# Generate for specific week
specific_date = datetime(2026, 3, 3)
report_path = generate_ceo_briefing(specific_date)
```

### get_week_range(date=None)

Get the start and end dates for a week.

**Parameters:**
- `date` (datetime, optional): Reference date (default: today)

**Returns:**
- `Tuple[datetime, datetime]`: (week_start, week_end)

### get_completed_tasks(week_start, week_end)

Get tasks completed within a date range.

**Parameters:**
- `week_start` (datetime): Start of week
- `week_end` (datetime): End of week

**Returns:**
- `List[Dict]`: List of completed tasks

### get_financial_summary()

Get financial summary from accounting ledger.

**Returns:**
- `Dict`: Financial metrics (income, expenses, net profit)

### get_system_health()

Get system health metrics from logs.

**Returns:**
- `Dict`: Health metrics (operations, errors, success rate)

## Automated Scheduling

### Windows Task Scheduler

Create a scheduled task to run every Monday at 9:00 AM:

1. Open Task Scheduler
2. Create Basic Task
3. Name: "CEO Weekly Briefing"
4. Trigger: Weekly, Monday, 9:00 AM
5. Action: Start a program
6. Program: `python`
7. Arguments: `F:\FTEs\Gold Tier\scripts\ceo_briefing.py`
8. Start in: `F:\FTEs\Gold Tier`

### Linux/Mac Cron

Add to crontab:
```bash
# Run every Monday at 9:00 AM
0 9 * * 1 cd /path/to/project && python scripts/ceo_briefing.py
```

### Python Scheduler (Included)

Use the included scheduler script:
```bash
python scripts/ceo_briefing_scheduler.py
```

This runs as a background service and generates the briefing every Monday at 9:00 AM.

## Usage Examples

### Generate Current Week Briefing

```bash
python scripts/ceo_briefing.py
```

### Generate for Specific Week

```bash
python scripts/ceo_briefing.py --date 2026-02-24
```

### View Latest Briefing

```bash
cat AI_Employee_Vault/Reports/CEO_Weekly.md
```

### View Historical Briefing

```bash
cat AI_Employee_Vault/Reports/CEO_Weekly_2026-03-02.md
```

### Programmatic Usage

```python
from scripts.ceo_briefing import generate_ceo_briefing
from datetime import datetime

# Generate briefing
report_path = generate_ceo_briefing()
print(f"Report generated: {report_path}")

# Read the report
with open(report_path, 'r') as f:
    briefing = f.read()
    print(briefing)
```

## Recommendations Engine

The briefing automatically generates recommendations based on:

- **Task Backlog:** Alerts if pending tasks > 10
- **Approvals:** Alerts if items awaiting approval
- **Social Media:** Alerts if no LinkedIn posts this week
- **Finances:** Alerts if net profit is negative
- **System Health:** Alerts if success rate < 95%
- **Productivity:** Alerts if no tasks completed

## Key Metrics Table

The briefing includes a summary table:

| Metric | Value |
|--------|-------|
| Tasks Completed | 15 |
| Tasks Pending | 8 |
| Approvals Needed | 2 |
| LinkedIn Posts | 3 |
| Net Profit | $7,329.50 |
| System Health | 98.5% |

## Integration Points

### Upstream Data Sources
- **Task System:** Done, Needs_Action, Needs_Approval directories
- **Accounting Manager:** Current_Month.md ledger
- **LinkedIn Skill:** Actions log entries
- **System Logs:** All operations logged to actions.log

### Downstream Consumers
- **CEO/Management:** Weekly executive summary
- **Dashboard:** Can display key metrics
- **Email:** Can be sent via email skill
- **Slack/Teams:** Can be posted to channels

## Logging

All briefing generation is logged to `logs/actions.log`:

```
[2026-03-03 15:45:00] [INFO] [CEO_BRIEFING] Generating CEO briefing for week 2026-03-02 to 2026-03-08
[2026-03-03 15:45:01] [SUCCESS] [CEO_BRIEFING] CEO briefing generated: CEO_Weekly_2026-03-02.md
[2026-03-03 15:45:01] [INFO] [CEO_BRIEFING] Summary: 15 tasks completed, 8 pending, $7,329.50 net profit
```

## Error Handling

The skill handles various error scenarios:

- **Missing Directories:** Creates required directories automatically
- **Missing Files:** Returns empty data sets (no crash)
- **Corrupted Data:** Logs warnings and continues
- **Parse Errors:** Skips problematic files and logs warnings
- **Date Errors:** Validates date format and provides clear error messages

## Performance

- **Execution Time:** < 2 seconds for typical data volumes
- **Memory Usage:** Minimal (processes files one at a time)
- **File I/O:** Read-only operations (except report writing)
- **Scalability:** Handles thousands of tasks/transactions efficiently

## Security Considerations

- **Read-Only Access:** Only reads from vault and logs
- **No External APIs:** All data processed locally
- **No Credentials:** No API keys or passwords needed
- **Audit Trail:** All operations logged
- **Data Privacy:** Financial data stays local

## Customization

### Modify Report Sections

Edit `scripts/ceo_briefing.py` to add/remove sections:

```python
# Add custom section
report += """
## 🎯 Custom Section

Your custom content here
"""
```

### Change Week Start Day

Modify `get_week_range()` function:

```python
# Week starts on Sunday instead of Monday
week_start = date - timedelta(days=date.weekday() + 1)
```

### Add More Data Sources

Add new functions to gather data:

```python
def get_custom_metrics():
    # Your custom data gathering logic
    return metrics
```

## Troubleshooting

### "No data found"
- Check that vault directories exist
- Verify files are in correct locations
- Ensure files have proper markdown format

### "Report not generated"
- Check write permissions on Reports directory
- Verify Python has access to vault directories
- Check logs/actions.log for error details

### "Incorrect week range"
- Verify system date/time is correct
- Use --date parameter to specify week
- Check timezone settings

### "Missing financial data"
- Ensure accounting ledger exists
- Verify Current_Month.md has proper format
- Check that transactions are recorded

## Dependencies

- Python 3.7+
- Standard library only (no external dependencies)
- Compatible with existing AI Employee Vault structure

## Future Enhancements

- Email delivery of briefing
- Slack/Teams integration
- PDF export option
- Charts and graphs
- Trend analysis (week-over-week)
- Predictive insights
- Custom metric definitions
- Multi-user support
- Mobile-friendly format
- Interactive dashboard

## Notes

- Week starts on Monday by default
- All dates in YYYY-MM-DD format
- Financial data is month-to-date (not weekly)
- System health is cumulative (all-time)
- Reports are archived automatically
- No external dependencies required
- Production-ready and reliable
