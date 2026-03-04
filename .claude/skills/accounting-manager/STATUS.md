# Accounting Manager Skill - Installation Complete ✓

## Overview

Production-ready accounting and financial tracking system for the Gold Tier AI Employee.

## What Was Created

### Files (5 total)

```
.claude/skills/accounting-manager/
├── SKILL.md           (400 lines) - Complete documentation
├── EXAMPLES.md        (100 lines) - Usage examples
├── test.py            (200 lines) - Validation script
└── requirements.txt   (1 line)    - No dependencies needed

scripts/
└── accounting_manager.py (600 lines) - Main implementation

AI_Employee_Vault/Accounting/
└── Current_Month.md   (auto-created) - Active ledger
```

## Features

✅ Add income and expense transactions
✅ Maintain Current_Month.md ledger
✅ Generate monthly summaries
✅ Generate weekly summaries
✅ Calculate totals and net profit
✅ Archive completed months
✅ Transaction filtering and search
✅ Comprehensive logging
✅ Input validation
✅ Zero external dependencies

## Quick Start

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

### Generate Monthly Summary

```bash
python scripts/accounting_manager.py summary
```

Output:
```
==================================================
MONTHLY SUMMARY
==================================================
Total Income:     $    15,750.00
Total Expenses:   $     8,420.50
Net Profit:       $     7,329.50

Transactions:                 42
  Income:                     15
  Expenses:                   27

Average Income:   $     1,050.00
Average Expense:  $       311.87
==================================================
```

### Generate Weekly Summary

```bash
python scripts/accounting_manager.py weekly
```

### List Transactions

```bash
# All transactions
python scripts/accounting_manager.py list

# Income only
python scripts/accounting_manager.py list --type income

# Date range
python scripts/accounting_manager.py list --start 2026-03-01 --end 2026-03-31
```

### Archive Month

```bash
python scripts/accounting_manager.py archive
```

## Ledger Format

Current_Month.md maintains a structured ledger:

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
**Description:** Monthly retainer payment

---

### 2026-03-03 | Office Supplies
**Type:** Expense
**Amount:** $127.50
**Description:** Printer paper and pens

---

## Weekly Summary

### Week of Mar 02 - Mar 08, 2026
- Income: $5,000.00
- Expenses: $226.50
- Net: $4,773.50
- Transactions: 2

---

*Last updated: 2026-03-03 14:30:45*
```

## Programmatic Usage

```python
from scripts.accounting_manager import (
    add_transaction,
    generate_summary,
    generate_weekly_summary,
    get_transactions,
    archive_month
)

# Add transaction
result = add_transaction(
    date="2026-03-03",
    title="Client Payment",
    type="income",
    amount=5000.00,
    description="Monthly retainer"
)

# Get summary
summary = generate_summary()
print(f"Net Profit: ${summary['net_profit']:,.2f}")

# Get weekly summary
weekly = generate_weekly_summary()
print(f"This week: ${weekly['net']:,.2f}")

# Filter transactions
income = get_transactions(type="income")
march = get_transactions(start_date="2026-03-01", end_date="2026-03-31")

# Archive month
archive_month(2026, 2)
```

## Logging

All operations logged to `logs/actions.log`:

```
[2026-03-03 14:30:45] [ACCOUNTING] Added income transaction: Client Payment ($5,000.00)
[2026-03-03 14:30:45] [ACCOUNTING] Total income: $15,750.00 | Total expenses: $8,420.50 | Net: $7,329.50
[2026-03-03 14:35:00] [ACCOUNTING] Generated weekly summary: Income $5,000.00 | Expenses $226.50
```

## File Locations

- **Active Ledger:** `AI_Employee_Vault/Accounting/Current_Month.md`
- **Archives:** `AI_Employee_Vault/Accounting/Archive/YYYY-MM_Month.md`
- **Logs:** `logs/actions.log`
- **Script:** `scripts/accounting_manager.py`

## Validation

Tested and working:
- ✓ File initialization
- ✓ Income transactions
- ✓ Expense transactions
- ✓ Monthly summaries
- ✓ Weekly summaries
- ✓ Transaction filtering
- ✓ Input validation
- ✓ Negative amount rejection
- ✓ Invalid type rejection
- ✓ Date format validation

## Integration Points

### Upstream
- Manual entry via CLI
- Odoo MCP (sync invoices/payments)
- Email watcher (detect payment notifications)

### Downstream
- Dashboard (financial metrics)
- Reports (monthly/weekly summaries)
- Task planner (threshold-based tasks)

## No Dependencies

Uses Python standard library only:
- No pip install required
- No external APIs
- All data stored locally
- Works offline

## Security

- Financial data in plain text markdown
- Restrict access to AI_Employee_Vault/Accounting/
- Automatic backups before archiving
- Audit trail with timestamps
- No external API calls

## Archive Structure

```
AI_Employee_Vault/Accounting/Archive/
├── 2026-01_January.md
├── 2026-02_February.md
└── 2026-03_March.md
```

## Commands Summary

```bash
# Add transactions
python scripts/accounting_manager.py add --date YYYY-MM-DD --title "Title" --type income|expense --amount 100.00 --description "Description"

# View summaries
python scripts/accounting_manager.py summary
python scripts/accounting_manager.py weekly

# List transactions
python scripts/accounting_manager.py list [--type income|expense] [--start YYYY-MM-DD] [--end YYYY-MM-DD]

# Archive month
python scripts/accounting_manager.py archive [--year YYYY] [--month MM]
```

## Status

✅ Fully implemented and tested
✅ Production-ready
✅ Zero dependencies
✅ Comprehensive documentation
✅ Example usage provided
✅ Validation script included

Ready to track your finances! 💰
