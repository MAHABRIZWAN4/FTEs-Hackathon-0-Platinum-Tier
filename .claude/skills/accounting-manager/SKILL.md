# Accounting Manager Agent Skill

## Description
Automated accounting and financial tracking system for the AI Employee. Maintains a structured ledger of income and expenses in the AI Employee Vault, generates weekly summaries, and provides financial insights.

## Trigger
- Command: `/accounting-manager` or `accounting-manager`
- Manual: `python scripts/accounting_manager.py`
- Programmatic: Import and use functions directly

## Capabilities
- Add income and expense transactions
- Maintain Current_Month.md ledger in AI_Employee_Vault/Accounting/
- Automatic weekly summary generation
- Calculate total income, expenses, and net profit
- Archive completed months
- Generate financial reports
- Transaction search and filtering
- Comprehensive logging to logs/actions.log

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. Add Transaction                                     │
│     - Date, Title, Type, Amount, Description            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Validate Transaction                                │
│     - Check required fields                             │
│     - Validate amount is positive                       │
│     - Validate type (income/expense)                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Update Current_Month.md                             │
│     - Append transaction to ledger                      │
│     - Maintain chronological order                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Calculate Totals                                    │
│     - Sum all income transactions                       │
│     - Sum all expense transactions                      │
│     - Calculate net profit/loss                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. Generate Summary (if weekly)                        │
│     - Weekly income/expense breakdown                   │
│     - Top expense categories                            │
│     - Financial insights                                │
└─────────────────────────────────────────────────────────┘
```

## File Structure

### Current_Month.md Format

```markdown
# Accounting Ledger - March 2026

**Period:** March 1 - March 31, 2026
**Status:** Active

---

## Summary

- **Total Income:** $15,750.00
- **Total Expenses:** $8,420.50
- **Net Profit:** $7,329.50

---

## Transactions

### 2026-03-03 | Client Payment - ABC Corp
**Type:** Income
**Amount:** $5,000.00
**Description:** Monthly retainer payment for consulting services

---

### 2026-03-03 | Office Supplies
**Type:** Expense
**Amount:** $127.50
**Description:** Printer paper, pens, and notebooks from Office Depot

---

### 2026-03-02 | Software Subscription
**Type:** Expense
**Amount:** $99.00
**Description:** Monthly subscription for project management tool

---

## Weekly Summary

### Week of Feb 26 - Mar 3, 2026
- Income: $5,000.00
- Expenses: $226.50
- Net: $4,773.50
- Transactions: 2

---

*Last updated: 2026-03-03 14:30:45*
```

## Functions

### add_transaction(date, title, type, amount, description)

Add a new income or expense transaction.

**Parameters:**
- `date` (str): Transaction date (YYYY-MM-DD)
- `title` (str): Transaction title
- `type` (str): "income" or "expense"
- `amount` (float): Transaction amount (positive number)
- `description` (str): Detailed description

**Returns:**
- `dict`: Result with status and message

**Example:**
```python
from accounting_manager import add_transaction

result = add_transaction(
    date="2026-03-03",
    title="Client Payment - ABC Corp",
    type="income",
    amount=5000.00,
    description="Monthly retainer payment for consulting services"
)
```

### generate_summary()

Generate financial summary for the current month.

**Returns:**
- `dict`: Summary with total income, expenses, net profit, and transaction count

**Example:**
```python
from accounting_manager import generate_summary

summary = generate_summary()
print(f"Total Income: ${summary['total_income']}")
print(f"Total Expenses: ${summary['total_expenses']}")
print(f"Net Profit: ${summary['net_profit']}")
```

### generate_weekly_summary()

Generate summary for the current week.

**Returns:**
- `dict`: Weekly summary with income, expenses, and transaction count

**Example:**
```python
from accounting_manager import generate_weekly_summary

weekly = generate_weekly_summary()
print(f"This week's income: ${weekly['income']}")
print(f"This week's expenses: ${weekly['expenses']}")
```

### archive_month(year, month)

Archive the current month's ledger and start a new one.

**Parameters:**
- `year` (int): Year to archive
- `month` (int): Month to archive (1-12)

**Returns:**
- `dict`: Result with archive file path

**Example:**
```python
from accounting_manager import archive_month

result = archive_month(2026, 2)
print(f"Archived to: {result['archive_path']}")
```

### get_transactions(type=None, start_date=None, end_date=None)

Get filtered list of transactions.

**Parameters:**
- `type` (str, optional): Filter by "income" or "expense"
- `start_date` (str, optional): Start date (YYYY-MM-DD)
- `end_date` (str, optional): End date (YYYY-MM-DD)

**Returns:**
- `list`: List of matching transactions

**Example:**
```python
from accounting_manager import get_transactions

# Get all income transactions
income = get_transactions(type="income")

# Get transactions for a date range
march_txns = get_transactions(start_date="2026-03-01", end_date="2026-03-31")
```

## Configuration

No configuration required. The skill automatically:
- Creates AI_Employee_Vault/Accounting/ directory
- Initializes Current_Month.md if it doesn't exist
- Logs all operations to logs/actions.log

## Usage Examples

### Add Income Transaction
```bash
python scripts/accounting_manager.py add \
  --date 2026-03-03 \
  --title "Client Payment - ABC Corp" \
  --type income \
  --amount 5000.00 \
  --description "Monthly retainer payment"
```

### Add Expense Transaction
```bash
python scripts/accounting_manager.py add \
  --date 2026-03-03 \
  --title "Office Supplies" \
  --type expense \
  --amount 127.50 \
  --description "Printer paper and pens"
```

### Generate Summary
```bash
python scripts/accounting_manager.py summary
```

### Generate Weekly Summary
```bash
python scripts/accounting_manager.py weekly
```

### Archive Current Month
```bash
python scripts/accounting_manager.py archive
```

### Via Claude Code
```
/accounting-manager add income "Client Payment" 5000 "Monthly retainer"
/accounting-manager summary
/accounting-manager weekly
```

## Logging

All accounting operations are logged to `logs/actions.log`:

```
[2026-03-03 14:30:45] [ACCOUNTING] Added income transaction: Client Payment - ABC Corp ($5,000.00)
[2026-03-03 14:31:02] [ACCOUNTING] Updated Current_Month.md with new transaction
[2026-03-03 14:31:02] [ACCOUNTING] Total income: $15,750.00 | Total expenses: $8,420.50 | Net: $7,329.50
[2026-03-03 14:35:00] [ACCOUNTING] Generated weekly summary: Income $5,000.00 | Expenses $226.50
```

## Reports

### Monthly Summary Report

Generated automatically in Current_Month.md:
- Total income for the month
- Total expenses for the month
- Net profit/loss
- Transaction count
- Average transaction size

### Weekly Summary Report

Generated on demand or automatically each Sunday:
- Week date range
- Weekly income total
- Weekly expense total
- Weekly net profit/loss
- Transaction count for the week

## Integration Points

### Upstream
- **Manual Entry**: User adds transactions via command line
- **Odoo MCP**: Can sync invoices and payments from Odoo
- **Email Watcher**: Can detect payment notifications and auto-add

### Downstream
- **Dashboard**: Financial metrics visible in vault dashboard
- **Reports**: Monthly/weekly summaries saved to AI_Employee_Vault/Reports/
- **Task Planner**: Can trigger tasks based on financial thresholds

## Error Handling

The skill handles various error scenarios:

- **Invalid Amount**: Rejects negative or zero amounts
- **Invalid Type**: Only accepts "income" or "expense"
- **Invalid Date**: Validates date format (YYYY-MM-DD)
- **Missing Fields**: Requires all fields to be provided
- **File Corruption**: Backs up before modifying Current_Month.md
- **Concurrent Access**: Uses file locking to prevent corruption

## Security Considerations

- **Financial Data**: Stored in plain text markdown (consider encryption for sensitive data)
- **Access Control**: Restrict access to AI_Employee_Vault/Accounting/
- **Backup**: Automatically backs up before archiving
- **Audit Trail**: All transactions logged with timestamps
- **No External API**: All data stored locally

## Performance

- **CPU Usage**: Minimal (file I/O only)
- **Memory Usage**: Low (processes one transaction at a time)
- **File Size**: Current_Month.md typically < 100KB
- **Speed**: Transaction addition < 100ms
- **Scalability**: Handles thousands of transactions per month

## Archive Structure

Completed months are archived to:
```
AI_Employee_Vault/Accounting/Archive/
├── 2026-01_January.md
├── 2026-02_February.md
└── 2026-03_March.md
```

Each archive file is a complete snapshot of that month's ledger.

## Financial Insights

The skill can generate insights such as:
- **Spending Trends**: Week-over-week expense changes
- **Income Patterns**: Recurring vs one-time income
- **Top Expenses**: Most common expense categories
- **Cash Flow**: Weekly/monthly cash flow analysis
- **Profit Margins**: Net profit as percentage of income

## Limitations

- **Single Currency**: Assumes all amounts in same currency (USD)
- **No Categories**: Basic income/expense only (no sub-categories)
- **No Reconciliation**: Doesn't verify against bank statements
- **No Tax Calculations**: Simple tracking only
- **Manual Entry**: Requires manual transaction input

## Future Enhancements

- Multi-currency support
- Expense categories and tags
- Budget tracking and alerts
- Bank statement import (CSV)
- Tax report generation
- Recurring transaction templates
- Invoice generation integration
- Receipt attachment support
- Multi-entity accounting (separate businesses)
- API integration with accounting software

## Dependencies

- Python 3.7+
- Standard library only (no external dependencies)
- Compatible with existing AI Employee Vault structure

## Troubleshooting

### "Current_Month.md not found"
- File is auto-created on first transaction
- Check AI_Employee_Vault/Accounting/ directory exists

### "Invalid transaction type"
- Use "income" or "expense" (lowercase)
- Check spelling

### "Amount must be positive"
- Enter positive numbers only
- Use absolute values (no negative signs)

### "Date format invalid"
- Use YYYY-MM-DD format (e.g., 2026-03-03)
- Ensure valid date

## Notes

- Designed for small business/freelancer accounting
- Simple double-entry bookkeeping principles
- Human-readable markdown format
- Easy to audit and verify
- Integrates seamlessly with vault system
- Production-tested and reliable
