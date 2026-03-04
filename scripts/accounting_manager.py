"""
Accounting Manager Agent - Gold Tier AI Employee

Automated accounting and financial tracking system.
Maintains income/expense ledger in AI_Employee_Vault/Accounting/Current_Month.md

Features:
- Add income and expense transactions
- Generate monthly and weekly summaries
- Calculate totals and net profit
- Archive completed months
- Transaction filtering and search
- Comprehensive logging

Usage:
    python scripts/accounting_manager.py add --date 2026-03-03 --title "Payment" --type income --amount 5000 --description "Client payment"
    python scripts/accounting_manager.py summary
    python scripts/accounting_manager.py weekly
    python scripts/accounting_manager.py archive
"""

import os
import sys
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
VAULT_DIR = Path("AI_Employee_Vault/Accounting")
CURRENT_MONTH_FILE = VAULT_DIR / "Current_Month.md"
ARCHIVE_DIR = VAULT_DIR / "Archive"
LOGS_DIR = Path("logs")
ACTIONS_LOG = LOGS_DIR / "actions.log"

# Ensure directories exist
VAULT_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log_action(message: str, level: str = "INFO"):
    """
    Log an action to logs/actions.log.

    Args:
        message (str): Message to log
        level (str): Log level (INFO, SUCCESS, WARNING, ERROR)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [ACCOUNTING] {message}\n"

    try:
        with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[{level}] {message}")
    except Exception as e:
        print(f"[ERROR] Failed to write to log: {e}")


def validate_transaction(date: str, title: str, type: str, amount: float, description: str) -> Tuple[bool, str]:
    """
    Validate transaction data.

    Args:
        date (str): Transaction date (YYYY-MM-DD)
        title (str): Transaction title
        type (str): "income" or "expense"
        amount (float): Transaction amount
        description (str): Transaction description

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"

    # Validate title
    if not title or not title.strip():
        return False, "Title cannot be empty"

    # Validate type
    if type.lower() not in ["income", "expense"]:
        return False, "Type must be 'income' or 'expense'"

    # Validate amount
    try:
        amount = float(amount)
        if amount <= 0:
            return False, "Amount must be positive"
    except (ValueError, TypeError):
        return False, "Invalid amount"

    # Validate description
    if not description or not description.strip():
        return False, "Description cannot be empty"

    return True, ""


def initialize_current_month():
    """
    Initialize Current_Month.md if it doesn't exist.
    """
    if CURRENT_MONTH_FILE.exists():
        return

    now = datetime.now()
    month_name = now.strftime("%B %Y")
    start_date = now.replace(day=1).strftime("%B %d")

    # Calculate last day of month
    if now.month == 12:
        next_month = now.replace(year=now.year + 1, month=1, day=1)
    else:
        next_month = now.replace(month=now.month + 1, day=1)
    last_day = (next_month - timedelta(days=1)).strftime("%B %d, %Y")

    content = f"""# Accounting Ledger - {month_name}

**Period:** {start_date} - {last_day}
**Status:** Active

---

## Summary

- **Total Income:** $0.00
- **Total Expenses:** $0.00
- **Net Profit:** $0.00

---

## Transactions

*No transactions yet*

---

*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

    with open(CURRENT_MONTH_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    log_action(f"Initialized Current_Month.md for {month_name}", "INFO")


def parse_transactions() -> List[Dict]:
    """
    Parse all transactions from Current_Month.md.

    Returns:
        List[Dict]: List of transaction dictionaries
    """
    if not CURRENT_MONTH_FILE.exists():
        return []

    with open(CURRENT_MONTH_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    transactions = []

    # Find all transaction blocks
    pattern = r"### (\d{4}-\d{2}-\d{2}) \| (.+?)\n\*\*Type:\*\* (Income|Expense)\n\*\*Amount:\*\* \$([0-9,]+\.\d{2})\n\*\*Description:\*\* (.+?)(?=\n---|\n\n##|\Z)"

    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        date, title, type, amount, description = match.groups()
        transactions.append({
            "date": date,
            "title": title.strip(),
            "type": type.lower(),
            "amount": float(amount.replace(",", "")),
            "description": description.strip()
        })

    return transactions


def calculate_totals() -> Dict[str, float]:
    """
    Calculate total income, expenses, and net profit.

    Returns:
        Dict[str, float]: Dictionary with totals
    """
    transactions = parse_transactions()

    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    net_profit = total_income - total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "transaction_count": len(transactions)
    }


def update_summary():
    """
    Update the summary section in Current_Month.md.
    """
    if not CURRENT_MONTH_FILE.exists():
        return

    totals = calculate_totals()

    with open(CURRENT_MONTH_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Update summary section
    summary_pattern = r"## Summary\n\n- \*\*Total Income:\*\* \$[0-9,]+\.\d{2}\n- \*\*Total Expenses:\*\* \$[0-9,]+\.\d{2}\n- \*\*Net Profit:\*\* -?\$[0-9,]+\.\d{2}"

    new_summary = f"""## Summary

- **Total Income:** ${totals['total_income']:,.2f}
- **Total Expenses:** ${totals['total_expenses']:,.2f}
- **Net Profit:** ${totals['net_profit']:,.2f}"""

    content = re.sub(summary_pattern, new_summary, content)

    # Update last updated timestamp
    timestamp_pattern = r"\*Last updated: .+?\*"
    new_timestamp = f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    content = re.sub(timestamp_pattern, new_timestamp, content)

    with open(CURRENT_MONTH_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def add_transaction(date: str, title: str, type: str, amount: float, description: str) -> Dict:
    """
    Add a new transaction to Current_Month.md.

    Args:
        date (str): Transaction date (YYYY-MM-DD)
        title (str): Transaction title
        type (str): "income" or "expense"
        amount (float): Transaction amount
        description (str): Transaction description

    Returns:
        Dict: Result with status and message
    """
    # Validate transaction
    is_valid, error_msg = validate_transaction(date, title, type, amount, description)
    if not is_valid:
        log_action(f"Transaction validation failed: {error_msg}", "ERROR")
        return {"status": "error", "message": error_msg}

    # Initialize file if needed
    initialize_current_month()

    # Format transaction
    type_capitalized = type.capitalize()
    transaction_block = f"""
### {date} | {title}
**Type:** {type_capitalized}
**Amount:** ${amount:,.2f}
**Description:** {description}

---
"""

    # Read current content
    with open(CURRENT_MONTH_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Find insertion point (after "## Transactions" header)
    if "*No transactions yet*" in content:
        # Replace placeholder
        content = content.replace("*No transactions yet*\n\n---", transaction_block.strip())
    else:
        # Insert after "## Transactions" header
        pattern = r"(## Transactions\n\n)"
        content = re.sub(pattern, r"\1" + transaction_block, content, count=1)

    # Write updated content
    with open(CURRENT_MONTH_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    # Update summary
    update_summary()

    log_action(f"Added {type} transaction: {title} (${amount:,.2f})", "SUCCESS")

    totals = calculate_totals()
    log_action(f"Total income: ${totals['total_income']:,.2f} | Total expenses: ${totals['total_expenses']:,.2f} | Net: ${totals['net_profit']:,.2f}", "INFO")

    return {
        "status": "success",
        "message": f"Transaction added successfully: {title} (${amount:,.2f})"
    }


def generate_summary() -> Dict:
    """
    Generate financial summary for the current month.

    Returns:
        Dict: Summary with totals and statistics
    """
    initialize_current_month()

    totals = calculate_totals()
    transactions = parse_transactions()

    # Calculate additional statistics
    income_txns = [t for t in transactions if t["type"] == "income"]
    expense_txns = [t for t in transactions if t["type"] == "expense"]

    avg_income = totals["total_income"] / len(income_txns) if income_txns else 0
    avg_expense = totals["total_expenses"] / len(expense_txns) if expense_txns else 0

    summary = {
        "total_income": totals["total_income"],
        "total_expenses": totals["total_expenses"],
        "net_profit": totals["net_profit"],
        "transaction_count": totals["transaction_count"],
        "income_count": len(income_txns),
        "expense_count": len(expense_txns),
        "avg_income": avg_income,
        "avg_expense": avg_expense
    }

    log_action(f"Generated monthly summary: Income ${summary['total_income']:,.2f} | Expenses ${summary['total_expenses']:,.2f} | Net ${summary['net_profit']:,.2f}", "INFO")

    return summary


def generate_weekly_summary() -> Dict:
    """
    Generate summary for the current week.

    Returns:
        Dict: Weekly summary with income, expenses, and net
    """
    initialize_current_month()

    transactions = parse_transactions()

    # Get current week date range
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday

    week_start_str = week_start.strftime("%Y-%m-%d")
    week_end_str = week_end.strftime("%Y-%m-%d")

    # Filter transactions for current week
    week_transactions = [
        t for t in transactions
        if week_start_str <= t["date"] <= week_end_str
    ]

    weekly_income = sum(t["amount"] for t in week_transactions if t["type"] == "income")
    weekly_expenses = sum(t["amount"] for t in week_transactions if t["type"] == "expense")
    weekly_net = weekly_income - weekly_expenses

    summary = {
        "week_start": week_start.strftime("%b %d"),
        "week_end": week_end.strftime("%b %d, %Y"),
        "income": weekly_income,
        "expenses": weekly_expenses,
        "net": weekly_net,
        "transaction_count": len(week_transactions)
    }

    # Add weekly summary to Current_Month.md
    add_weekly_summary_to_file(summary)

    log_action(f"Generated weekly summary: Income ${summary['income']:,.2f} | Expenses ${summary['expenses']:,.2f} | Net ${summary['net']:,.2f}", "INFO")

    return summary


def add_weekly_summary_to_file(summary: Dict):
    """
    Add weekly summary section to Current_Month.md.

    Args:
        summary (Dict): Weekly summary data
    """
    if not CURRENT_MONTH_FILE.exists():
        return

    with open(CURRENT_MONTH_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    weekly_block = f"""
## Weekly Summary

### Week of {summary['week_start']} - {summary['week_end']}
- Income: ${summary['income']:,.2f}
- Expenses: ${summary['expenses']:,.2f}
- Net: ${summary['net']:,.2f}
- Transactions: {summary['transaction_count']}

---
"""

    # Check if weekly summary section exists
    if "## Weekly Summary" in content:
        # Replace existing weekly summary
        pattern = r"## Weekly Summary\n\n### Week of .+?\n- Income: .+?\n- Expenses: .+?\n- Net: .+?\n- Transactions: .+?\n\n---"
        content = re.sub(pattern, weekly_block.strip(), content)
    else:
        # Add before last updated timestamp
        pattern = r"(\n---\n\n\*Last updated:)"
        content = re.sub(pattern, weekly_block + r"\1", content)

    with open(CURRENT_MONTH_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def archive_month(year: int = None, month: int = None) -> Dict:
    """
    Archive the current month's ledger.

    Args:
        year (int): Year to archive (default: current year)
        month (int): Month to archive (default: current month)

    Returns:
        Dict: Result with archive file path
    """
    if not CURRENT_MONTH_FILE.exists():
        return {"status": "error", "message": "No current month file to archive"}

    now = datetime.now()
    year = year or now.year
    month = month or now.month

    month_name = datetime(year, month, 1).strftime("%B")
    archive_filename = f"{year}-{month:02d}_{month_name}.md"
    archive_path = ARCHIVE_DIR / archive_filename

    # Copy current month to archive
    with open(CURRENT_MONTH_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Update status to Archived
    content = content.replace("**Status:** Active", "**Status:** Archived")

    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(content)

    log_action(f"Archived {month_name} {year} to {archive_filename}", "SUCCESS")

    # Initialize new current month
    CURRENT_MONTH_FILE.unlink()
    initialize_current_month()

    return {
        "status": "success",
        "message": f"Month archived successfully",
        "archive_path": str(archive_path)
    }


def get_transactions(type: str = None, start_date: str = None, end_date: str = None) -> List[Dict]:
    """
    Get filtered list of transactions.

    Args:
        type (str): Filter by "income" or "expense"
        start_date (str): Start date (YYYY-MM-DD)
        end_date (str): End date (YYYY-MM-DD)

    Returns:
        List[Dict]: Filtered transactions
    """
    transactions = parse_transactions()

    # Filter by type
    if type:
        transactions = [t for t in transactions if t["type"] == type.lower()]

    # Filter by date range
    if start_date:
        transactions = [t for t in transactions if t["date"] >= start_date]
    if end_date:
        transactions = [t for t in transactions if t["date"] <= end_date]

    return transactions


def main():
    """
    Main entry point for command-line usage.
    """
    parser = argparse.ArgumentParser(description="Accounting Manager - Track income and expenses")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add transaction command
    add_parser = subparsers.add_parser("add", help="Add a new transaction")
    add_parser.add_argument("--date", required=True, help="Transaction date (YYYY-MM-DD)")
    add_parser.add_argument("--title", required=True, help="Transaction title")
    add_parser.add_argument("--type", required=True, choices=["income", "expense"], help="Transaction type")
    add_parser.add_argument("--amount", required=True, type=float, help="Transaction amount")
    add_parser.add_argument("--description", required=True, help="Transaction description")

    # Summary command
    subparsers.add_parser("summary", help="Generate monthly summary")

    # Weekly summary command
    subparsers.add_parser("weekly", help="Generate weekly summary")

    # Archive command
    archive_parser = subparsers.add_parser("archive", help="Archive current month")
    archive_parser.add_argument("--year", type=int, help="Year to archive")
    archive_parser.add_argument("--month", type=int, help="Month to archive (1-12)")

    # List transactions command
    list_parser = subparsers.add_parser("list", help="List transactions")
    list_parser.add_argument("--type", choices=["income", "expense"], help="Filter by type")
    list_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    list_parser.add_argument("--end", help="End date (YYYY-MM-DD)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == "add":
        result = add_transaction(args.date, args.title, args.type, args.amount, args.description)
        print(f"\n{result['message']}\n")

    elif args.command == "summary":
        summary = generate_summary()
        print(f"\n{'='*50}")
        print(f"MONTHLY SUMMARY")
        print(f"{'='*50}")
        print(f"Total Income:     ${summary['total_income']:>12,.2f}")
        print(f"Total Expenses:   ${summary['total_expenses']:>12,.2f}")
        print(f"Net Profit:       ${summary['net_profit']:>12,.2f}")
        print(f"\nTransactions:     {summary['transaction_count']:>12}")
        print(f"  Income:         {summary['income_count']:>12}")
        print(f"  Expenses:       {summary['expense_count']:>12}")
        print(f"\nAverage Income:   ${summary['avg_income']:>12,.2f}")
        print(f"Average Expense:  ${summary['avg_expense']:>12,.2f}")
        print(f"{'='*50}\n")

    elif args.command == "weekly":
        summary = generate_weekly_summary()
        print(f"\n{'='*50}")
        print(f"WEEKLY SUMMARY")
        print(f"{'='*50}")
        print(f"Week: {summary['week_start']} - {summary['week_end']}")
        print(f"\nIncome:           ${summary['income']:>12,.2f}")
        print(f"Expenses:         ${summary['expenses']:>12,.2f}")
        print(f"Net:              ${summary['net']:>12,.2f}")
        print(f"\nTransactions:     {summary['transaction_count']:>12}")
        print(f"{'='*50}\n")

    elif args.command == "archive":
        result = archive_month(args.year, args.month)
        print(f"\n{result['message']}")
        if result['status'] == 'success':
            print(f"Archive location: {result['archive_path']}\n")

    elif args.command == "list":
        transactions = get_transactions(args.type, args.start, args.end)
        print(f"\n{'='*70}")
        print(f"TRANSACTIONS ({len(transactions)} found)")
        print(f"{'='*70}")
        for txn in transactions:
            print(f"\n{txn['date']} | {txn['title']}")
            print(f"  Type: {txn['type'].capitalize()}")
            print(f"  Amount: ${txn['amount']:,.2f}")
            print(f"  Description: {txn['description']}")
        print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()
