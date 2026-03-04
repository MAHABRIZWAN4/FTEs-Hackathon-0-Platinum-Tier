"""
CEO Briefing Agent - Gold Tier AI Employee

Automated weekly executive summary report generator.
Aggregates data from all AI Employee systems into a comprehensive CEO briefing.

Features:
- Tasks completed this week
- Tasks sent/created
- LinkedIn posts published
- Pending approvals
- Income/Expense financial summary
- System health metrics
- Auto-scheduled weekly generation

Output: AI_Employee_Vault/Reports/CEO_Weekly.md

Usage:
    python scripts/ceo_briefing.py
    python scripts/ceo_briefing.py --date 2026-03-03
"""

import os
import sys
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
REPORTS_DIR = VAULT_DIR / "Reports"
DONE_DIR = VAULT_DIR / "Done"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
NEEDS_APPROVAL_DIR = VAULT_DIR / "Needs_Approval"
ACCOUNTING_FILE = VAULT_DIR / "Accounting" / "Current_Month.md"
LOGS_DIR = Path("logs")
ACTIONS_LOG = LOGS_DIR / "actions.log"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def log_action(message: str, level: str = "INFO"):
    """Log an action to logs/actions.log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [CEO_BRIEFING] {message}\n"

    try:
        with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[{level}] {message}")
    except Exception as e:
        print(f"[ERROR] Failed to write to log: {e}")


def get_week_range(date: datetime = None) -> Tuple[datetime, datetime]:
    """
    Get the start and end dates for the week.

    Args:
        date (datetime): Reference date (default: today)

    Returns:
        Tuple[datetime, datetime]: (week_start, week_end)
    """
    if date is None:
        date = datetime.now()

    # Week starts on Monday
    week_start = date - timedelta(days=date.weekday())
    week_end = week_start + timedelta(days=6)

    return week_start, week_end


def get_completed_tasks(week_start: datetime, week_end: datetime) -> List[Dict]:
    """
    Get tasks completed this week from Done directory.

    Args:
        week_start (datetime): Start of week
        week_end (datetime): End of week

    Returns:
        List[Dict]: List of completed tasks
    """
    if not DONE_DIR.exists():
        return []

    completed_tasks = []

    for file_path in DONE_DIR.glob("*.md"):
        try:
            # Check file modification time
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

            if week_start <= mtime <= week_end:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract title (first # heading)
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1) if title_match else file_path.stem

                completed_tasks.append({
                    "title": title,
                    "file": file_path.name,
                    "date": mtime.strftime("%Y-%m-%d")
                })
        except Exception as e:
            log_action(f"Error reading task {file_path.name}: {e}", "WARNING")

    return sorted(completed_tasks, key=lambda x: x["date"], reverse=True)


def get_pending_tasks() -> List[Dict]:
    """
    Get pending tasks from Needs_Action directory.

    Returns:
        List[Dict]: List of pending tasks
    """
    if not NEEDS_ACTION_DIR.exists():
        return []

    pending_tasks = []

    for file_path in NEEDS_ACTION_DIR.glob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract title
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem

            # Extract priority if exists
            priority_match = re.search(r"\*\*Priority:\*\*\s+(.+)", content)
            priority = priority_match.group(1) if priority_match else "Normal"

            pending_tasks.append({
                "title": title,
                "file": file_path.name,
                "priority": priority
            })
        except Exception as e:
            log_action(f"Error reading task {file_path.name}: {e}", "WARNING")

    return pending_tasks


def get_pending_approvals() -> List[Dict]:
    """
    Get items pending approval from Needs_Approval directory.

    Returns:
        List[Dict]: List of items needing approval
    """
    if not NEEDS_APPROVAL_DIR.exists():
        return []

    approvals = []

    for file_path in NEEDS_APPROVAL_DIR.glob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract title
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem

            # Extract date
            ctime = datetime.fromtimestamp(file_path.stat().st_ctime)

            approvals.append({
                "title": title,
                "file": file_path.name,
                "date": ctime.strftime("%Y-%m-%d")
            })
        except Exception as e:
            log_action(f"Error reading approval {file_path.name}: {e}", "WARNING")

    return sorted(approvals, key=lambda x: x["date"])


def get_linkedin_posts(week_start: datetime, week_end: datetime) -> List[Dict]:
    """
    Get LinkedIn posts from logs this week.

    Args:
        week_start (datetime): Start of week
        week_end (datetime): End of week

    Returns:
        List[Dict]: List of LinkedIn posts
    """
    if not ACTIONS_LOG.exists():
        return []

    posts = []

    try:
        with open(ACTIONS_LOG, "r", encoding="utf-8") as f:
            for line in f:
                # Look for LinkedIn post entries
                if "[LINKEDIN]" in line and "Post published successfully" in line:
                    # Extract timestamp
                    timestamp_match = re.search(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
                    if timestamp_match:
                        post_time = datetime.strptime(timestamp_match.group(1), "%Y-%m-%d %H:%M:%S")

                        if week_start <= post_time <= week_end:
                            posts.append({
                                "date": post_time.strftime("%Y-%m-%d"),
                                "time": post_time.strftime("%H:%M:%S")
                            })
    except Exception as e:
        log_action(f"Error reading LinkedIn posts: {e}", "WARNING")

    return posts


def get_financial_summary() -> Dict:
    """
    Get financial summary from accounting ledger.

    Returns:
        Dict: Financial summary with income, expenses, net
    """
    if not ACCOUNTING_FILE.exists():
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_profit": 0.0,
            "transaction_count": 0
        }

    try:
        with open(ACCOUNTING_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract totals from summary section
        income_match = re.search(r"\*\*Total Income:\*\*\s+\$([0-9,]+\.\d{2})", content)
        expenses_match = re.search(r"\*\*Total Expenses:\*\*\s+\$([0-9,]+\.\d{2})", content)
        net_match = re.search(r"\*\*Net Profit:\*\*\s+-?\$([0-9,]+\.\d{2})", content)

        total_income = float(income_match.group(1).replace(",", "")) if income_match else 0.0
        total_expenses = float(expenses_match.group(1).replace(",", "")) if expenses_match else 0.0
        net_profit = float(net_match.group(1).replace(",", "")) if net_match else 0.0

        # Count transactions
        transaction_count = len(re.findall(r"^###\s+\d{4}-\d{2}-\d{2}\s+\|", content, re.MULTILINE))

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "transaction_count": transaction_count
        }
    except Exception as e:
        log_action(f"Error reading financial summary: {e}", "WARNING")
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_profit": 0.0,
            "transaction_count": 0
        }


def get_system_health() -> Dict:
    """
    Get system health metrics from logs.

    Returns:
        Dict: System health metrics
    """
    if not ACTIONS_LOG.exists():
        return {
            "total_operations": 0,
            "errors": 0,
            "warnings": 0,
            "success_rate": 100.0
        }

    try:
        total_operations = 0
        errors = 0
        warnings = 0

        with open(ACTIONS_LOG, "r", encoding="utf-8") as f:
            for line in f:
                if "[INFO]" in line or "[SUCCESS]" in line or "[ERROR]" in line or "[WARNING]" in line:
                    total_operations += 1

                if "[ERROR]" in line:
                    errors += 1
                elif "[WARNING]" in line:
                    warnings += 1

        success_rate = ((total_operations - errors) / total_operations * 100) if total_operations > 0 else 100.0

        return {
            "total_operations": total_operations,
            "errors": errors,
            "warnings": warnings,
            "success_rate": success_rate
        }
    except Exception as e:
        log_action(f"Error calculating system health: {e}", "WARNING")
        return {
            "total_operations": 0,
            "errors": 0,
            "warnings": 0,
            "success_rate": 100.0
        }


def generate_ceo_briefing(date: datetime = None) -> str:
    """
    Generate CEO weekly briefing report.

    Args:
        date (datetime): Reference date for the week (default: today)

    Returns:
        str: Path to generated report
    """
    if date is None:
        date = datetime.now()

    week_start, week_end = get_week_range(date)

    log_action(f"Generating CEO briefing for week {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}", "INFO")

    # Gather data from all sources
    completed_tasks = get_completed_tasks(week_start, week_end)
    pending_tasks = get_pending_tasks()
    pending_approvals = get_pending_approvals()
    linkedin_posts = get_linkedin_posts(week_start, week_end)
    financial_summary = get_financial_summary()
    system_health = get_system_health()

    # Generate report
    report = f"""# CEO Weekly Briefing

**Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}**
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

This week's AI Employee performance summary covering task completion, social media activity, financial metrics, and system health.

---

## 📋 Tasks & Productivity

### Completed This Week
**Total:** {len(completed_tasks)} tasks completed

"""

    if completed_tasks:
        for task in completed_tasks[:10]:  # Show top 10
            report += f"- **{task['title']}** ({task['date']})\n"
        if len(completed_tasks) > 10:
            report += f"\n*...and {len(completed_tasks) - 10} more*\n"
    else:
        report += "*No tasks completed this week*\n"

    report += f"""

### Pending Tasks
**Total:** {len(pending_tasks)} tasks awaiting action

"""

    if pending_tasks:
        # Group by priority
        high_priority = [t for t in pending_tasks if "high" in t.get("priority", "").lower()]
        normal_priority = [t for t in pending_tasks if "high" not in t.get("priority", "").lower()]

        if high_priority:
            report += "**High Priority:**\n"
            for task in high_priority[:5]:
                report += f"- {task['title']}\n"

        if normal_priority:
            report += "\n**Normal Priority:**\n"
            for task in normal_priority[:5]:
                report += f"- {task['title']}\n"

        if len(pending_tasks) > 10:
            report += f"\n*...and {len(pending_tasks) - 10} more*\n"
    else:
        report += "*No pending tasks*\n"

    report += """

---

## 🔔 Pending Approvals

"""

    if pending_approvals:
        report += f"**Total:** {len(pending_approvals)} items awaiting approval\n\n"
        for approval in pending_approvals[:5]:
            report += f"- **{approval['title']}** (since {approval['date']})\n"
        if len(pending_approvals) > 5:
            report += f"\n*...and {len(pending_approvals) - 5} more*\n"
    else:
        report += "✓ No items pending approval\n"

    report += """

---

## 📱 Social Media Activity

### LinkedIn Posts
"""

    if linkedin_posts:
        report += f"**Total:** {len(linkedin_posts)} posts published this week\n\n"
        for post in linkedin_posts:
            report += f"- {post['date']} at {post['time']}\n"
    else:
        report += "*No LinkedIn posts this week*\n"

    report += """

---

## 💰 Financial Summary

"""

    report += f"""**Month-to-Date:**
- Total Income: ${financial_summary['total_income']:,.2f}
- Total Expenses: ${financial_summary['total_expenses']:,.2f}
- Net Profit: ${financial_summary['net_profit']:,.2f}
- Transactions: {financial_summary['transaction_count']}

"""

    # Calculate profit margin
    if financial_summary['total_income'] > 0:
        profit_margin = (financial_summary['net_profit'] / financial_summary['total_income']) * 100
        report += f"**Profit Margin:** {profit_margin:.1f}%\n"

    report += """

---

## 🔧 System Health

"""

    report += f"""**Overall Status:** {"✓ Healthy" if system_health['success_rate'] >= 95 else "⚠ Needs Attention" if system_health['success_rate'] >= 85 else "✗ Critical"}

- Total Operations: {system_health['total_operations']:,}
- Success Rate: {system_health['success_rate']:.1f}%
- Errors: {system_health['errors']}
- Warnings: {system_health['warnings']}

"""

    if system_health['errors'] > 0:
        report += f"⚠ **Action Required:** {system_health['errors']} errors detected. Review logs/actions.log\n"

    report += """

---

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| Tasks Completed | """
    report += f"{len(completed_tasks)} |\n"
    report += f"| Tasks Pending | {len(pending_tasks)} |\n"
    report += f"| Approvals Needed | {len(pending_approvals)} |\n"
    report += f"| LinkedIn Posts | {len(linkedin_posts)} |\n"
    report += f"| Net Profit | ${financial_summary['net_profit']:,.2f} |\n"
    report += f"| System Health | {system_health['success_rate']:.1f}% |\n"

    report += """

---

## 🎯 Recommendations

"""

    # Generate recommendations based on data
    recommendations = []

    if len(pending_tasks) > 10:
        recommendations.append(f"- **Task Backlog:** {len(pending_tasks)} pending tasks. Consider prioritizing or delegating.")

    if len(pending_approvals) > 0:
        recommendations.append(f"- **Approvals:** {len(pending_approvals)} items awaiting approval. Review to unblock workflows.")

    if len(linkedin_posts) == 0:
        recommendations.append("- **Social Media:** No LinkedIn posts this week. Consider increasing social presence.")

    if financial_summary['net_profit'] < 0:
        recommendations.append(f"- **Finances:** Negative net profit (${financial_summary['net_profit']:,.2f}). Review expenses.")

    if system_health['success_rate'] < 95:
        recommendations.append(f"- **System Health:** Success rate at {system_health['success_rate']:.1f}%. Investigate errors.")

    if len(completed_tasks) == 0:
        recommendations.append("- **Productivity:** No tasks completed this week. Review task pipeline.")

    if recommendations:
        for rec in recommendations:
            report += f"{rec}\n"
    else:
        report += "✓ All systems operating optimally. No immediate action required.\n"

    report += """

---

## 📁 Detailed Reports

For more information, see:
- Tasks: `AI_Employee_Vault/Done/` and `AI_Employee_Vault/Needs_Action/`
- Approvals: `AI_Employee_Vault/Needs_Approval/`
- Finances: `AI_Employee_Vault/Accounting/Current_Month.md`
- System Logs: `logs/actions.log`

---

*Generated by CEO Briefing Agent - Gold Tier AI Employee*
"""

    # Write report to file
    report_filename = f"CEO_Weekly_{week_start.strftime('%Y-%m-%d')}.md"
    report_path = REPORTS_DIR / report_filename

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    # Also update CEO_Weekly.md (latest)
    latest_path = REPORTS_DIR / "CEO_Weekly.md"
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(report)

    log_action(f"CEO briefing generated: {report_filename}", "SUCCESS")
    log_action(f"Summary: {len(completed_tasks)} tasks completed, {len(pending_tasks)} pending, ${financial_summary['net_profit']:,.2f} net profit", "INFO")

    return str(report_path)


def main():
    """
    Main entry point for command-line usage.
    """
    parser = argparse.ArgumentParser(description="CEO Briefing - Generate weekly executive summary")
    parser.add_argument("--date", help="Reference date for the week (YYYY-MM-DD)")

    args = parser.parse_args()

    # Parse date if provided
    date = None
    if args.date:
        try:
            date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"[ERROR] Invalid date format. Use YYYY-MM-DD")
            return 1

    # Generate briefing
    try:
        report_path = generate_ceo_briefing(date)
        print(f"\n{'='*60}")
        print(f"CEO BRIEFING GENERATED")
        print(f"{'='*60}")
        print(f"Report: {report_path}")
        print(f"Latest: AI_Employee_Vault/Reports/CEO_Weekly.md")
        print(f"{'='*60}\n")
        return 0
    except Exception as e:
        log_action(f"Failed to generate CEO briefing: {str(e)}", "ERROR")
        print(f"\n[ERROR] Failed to generate briefing: {str(e)}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
