# Accounting Manager - Quick Examples

## Add Income Transaction

```bash
python scripts/accounting_manager.py add \
  --date 2026-03-03 \
  --title "Client Payment - ABC Corp" \
  --type income \
  --amount 5000.00 \
  --description "Monthly retainer payment for consulting services"
```

## Add Expense Transaction

```bash
python scripts/accounting_manager.py add \
  --date 2026-03-03 \
  --title "Office Supplies" \
  --type expense \
  --amount 127.50 \
  --description "Printer paper, pens, and notebooks from Office Depot"
```

## Generate Monthly Summary

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

## Generate Weekly Summary

```bash
python scripts/accounting_manager.py weekly
```

Output:
```
==================================================
WEEKLY SUMMARY
==================================================
Week: Feb 26 - Mar 3, 2026

Income:           $     5,000.00
Expenses:         $       226.50
Net:              $     4,773.50

Transactions:                  2
==================================================
```

## List All Transactions

```bash
python scripts/accounting_manager.py list
```

## List Income Only

```bash
python scripts/accounting_manager.py list --type income
```

## List Transactions by Date Range

```bash
python scripts/accounting_manager.py list --start 2026-03-01 --end 2026-03-31
```

## Archive Current Month

```bash
python scripts/accounting_manager.py archive
```

## Programmatic Usage

```python
from scripts.accounting_manager import add_transaction, generate_summary

# Add transaction
result = add_transaction(
    date="2026-03-03",
    title="Client Payment",
    type="income",
    amount=5000.00,
    description="Monthly retainer"
)

print(result['message'])

# Get summary
summary = generate_summary()
print(f"Net Profit: ${summary['net_profit']:,.2f}")
```

## Test the Skill

```bash
python .claude/skills/accounting-manager/test.py
```

## View Current Ledger

```bash
cat AI_Employee_Vault/Accounting/Current_Month.md
```

## View Logs

```bash
tail -f logs/actions.log | grep ACCOUNTING
```
