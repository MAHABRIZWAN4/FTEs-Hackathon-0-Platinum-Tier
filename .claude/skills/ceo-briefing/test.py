#!/usr/bin/env python3
"""
CEO Briefing - Test and Validation

Tests the CEO briefing generation functionality.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.ceo_briefing import (
        generate_ceo_briefing,
        get_week_range,
        get_completed_tasks,
        get_pending_tasks,
        get_pending_approvals,
        get_financial_summary,
        get_system_health,
        REPORTS_DIR
    )
except ImportError as e:
    print(f"[ERROR] Failed to import ceo_briefing: {e}")
    sys.exit(1)

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_status(message, status="info"):
    """Print colored status."""
    if status == "success":
        print(f"{GREEN}[+]{RESET} {message}")
    elif status == "error":
        print(f"{RED}[!]{RESET} {message}")
    elif status == "warning":
        print(f"{YELLOW}[*]{RESET} {message}")
    else:
        print(f"{BLUE}[i]{RESET} {message}")


def test_week_range():
    """Test week range calculation."""
    print_status("Testing week range calculation...", "info")

    try:
        week_start, week_end = get_week_range()

        print_status(f"Week start: {week_start.strftime('%Y-%m-%d')}", "info")
        print_status(f"Week end: {week_end.strftime('%Y-%m-%d')}", "info")

        # Verify it's a 7-day range
        delta = (week_end - week_start).days
        if delta == 6:
            print_status("Week range calculation correct (7 days)", "success")
            return True
        else:
            print_status(f"Week range incorrect: {delta + 1} days", "error")
            return False
    except Exception as e:
        print_status(f"Week range error: {str(e)}", "error")
        return False


def test_data_gathering():
    """Test data gathering functions."""
    print_status("Testing data gathering...", "info")

    try:
        week_start, week_end = get_week_range()

        # Test each data source
        completed = get_completed_tasks(week_start, week_end)
        print_status(f"Completed tasks: {len(completed)}", "info")

        pending = get_pending_tasks()
        print_status(f"Pending tasks: {len(pending)}", "info")

        approvals = get_pending_approvals()
        print_status(f"Pending approvals: {len(approvals)}", "info")

        financial = get_financial_summary()
        print_status(f"Net profit: ${financial['net_profit']:,.2f}", "info")

        health = get_system_health()
        print_status(f"System health: {health['success_rate']:.1f}%", "info")

        print_status("Data gathering successful", "success")
        return True
    except Exception as e:
        print_status(f"Data gathering error: {str(e)}", "error")
        return False


def test_report_generation():
    """Test report generation."""
    print_status("Testing report generation...", "info")

    try:
        report_path = generate_ceo_briefing()

        if Path(report_path).exists():
            print_status(f"Report generated: {report_path}", "success")

            # Check file size
            size = Path(report_path).stat().st_size
            print_status(f"Report size: {size} bytes", "info")

            if size > 100:
                print_status("Report has content", "success")
                return True
            else:
                print_status("Report is too small", "warning")
                return False
        else:
            print_status("Report file not found", "error")
            return False
    except Exception as e:
        print_status(f"Report generation error: {str(e)}", "error")
        return False


def test_report_content():
    """Test report content structure."""
    print_status("Testing report content...", "info")

    try:
        latest_report = REPORTS_DIR / "CEO_Weekly.md"

        if not latest_report.exists():
            print_status("Latest report not found", "error")
            return False

        with open(latest_report, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required sections
        required_sections = [
            "# CEO Weekly Briefing",
            "## Executive Summary",
            "## 📋 Tasks & Productivity",
            "## 🔔 Pending Approvals",
            "## 📱 Social Media Activity",
            "## 💰 Financial Summary",
            "## 🔧 System Health",
            "## 📊 Key Metrics",
            "## 🎯 Recommendations"
        ]

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            print_status(f"Missing sections: {', '.join(missing_sections)}", "error")
            return False
        else:
            print_status("All required sections present", "success")
            return True
    except Exception as e:
        print_status(f"Content validation error: {str(e)}", "error")
        return False


def test_report_readability():
    """Test report is readable and well-formatted."""
    print_status("Testing report readability...", "info")

    try:
        latest_report = REPORTS_DIR / "CEO_Weekly.md"

        with open(latest_report, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for markdown formatting
        has_headers = content.count("##") >= 8
        has_lists = content.count("-") >= 5
        has_tables = "|" in content
        has_separators = "---" in content

        if all([has_headers, has_lists, has_tables, has_separators]):
            print_status("Report is well-formatted", "success")
            return True
        else:
            print_status("Report formatting issues detected", "warning")
            return False
    except Exception as e:
        print_status(f"Readability test error: {str(e)}", "error")
        return False


def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}CEO Briefing - Validation Tests{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    tests = [
        ("Week Range Calculation", test_week_range),
        ("Data Gathering", test_data_gathering),
        ("Report Generation", test_report_generation),
        ("Report Content", test_report_content),
        ("Report Readability", test_report_readability)
    ]

    results = {}
    for name, test_func in tests:
        print(f"\n{BLUE}[{name}]{RESET}")
        results[name] = test_func()

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "success" if result else "error"
        print_status(f"{name}: {'PASS' if result else 'FAIL'}", status)

    print(f"\n{BLUE}Result: {passed}/{total} tests passed{RESET}\n")

    if passed == total:
        print_status("All tests passed! CEO Briefing is ready to use.", "success")
        print(f"\n{BLUE}View the report:{RESET}")
        print(f"  cat AI_Employee_Vault/Reports/CEO_Weekly.md\n")
        return 0
    else:
        print_status("Some tests failed. Check errors above.", "warning")
        return 1


if __name__ == "__main__":
    sys.exit(main())
