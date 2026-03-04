"""
CEO Briefing Scheduler - Gold Tier AI Employee

Automated scheduler that runs CEO briefing generation every Monday at 9:00 AM.
Runs as a background service.

Usage:
    python scripts/ceo_briefing_scheduler.py
    python scripts/ceo_briefing_scheduler.py --time "09:00"
    python scripts/ceo_briefing_scheduler.py --day monday
"""

import sys
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.ceo_briefing import generate_ceo_briefing, log_action
except ImportError as e:
    print(f"[ERROR] Failed to import ceo_briefing: {e}")
    sys.exit(1)


def parse_time(time_str: str) -> tuple:
    """
    Parse time string to (hour, minute).

    Args:
        time_str (str): Time in HH:MM format

    Returns:
        tuple: (hour, minute)
    """
    try:
        hour, minute = map(int, time_str.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time range")
        return hour, minute
    except Exception:
        print(f"[ERROR] Invalid time format. Use HH:MM (e.g., 09:00)")
        sys.exit(1)


def get_day_number(day_name: str) -> int:
    """
    Convert day name to weekday number (0=Monday, 6=Sunday).

    Args:
        day_name (str): Day name (e.g., "monday")

    Returns:
        int: Weekday number
    """
    days = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    day_lower = day_name.lower()
    if day_lower not in days:
        print(f"[ERROR] Invalid day name. Use: {', '.join(days.keys())}")
        sys.exit(1)

    return days[day_lower]


def should_run_now(target_day: int, target_hour: int, target_minute: int) -> bool:
    """
    Check if briefing should run now.

    Args:
        target_day (int): Target weekday (0=Monday)
        target_hour (int): Target hour (0-23)
        target_minute (int): Target minute (0-59)

    Returns:
        bool: True if should run now
    """
    now = datetime.now()

    # Check if it's the right day
    if now.weekday() != target_day:
        return False

    # Check if it's the right time (within 1 minute window)
    if now.hour == target_hour and now.minute == target_minute:
        return True

    return False


def get_next_run_time(target_day: int, target_hour: int, target_minute: int) -> datetime:
    """
    Calculate next run time.

    Args:
        target_day (int): Target weekday
        target_hour (int): Target hour
        target_minute (int): Target minute

    Returns:
        datetime: Next run time
    """
    now = datetime.now()
    days_ahead = target_day - now.weekday()

    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7

    next_run = now + timedelta(days=days_ahead)
    next_run = next_run.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

    # If we're on the target day but past the time, schedule for next week
    if days_ahead == 0 and now.time() > next_run.time():
        next_run += timedelta(days=7)

    return next_run


def run_scheduler(target_day: int = 0, target_hour: int = 9, target_minute: int = 0):
    """
    Run the scheduler loop.

    Args:
        target_day (int): Target weekday (0=Monday)
        target_hour (int): Target hour
        target_minute (int): Target minute
    """
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    print(f"\n{'='*60}")
    print(f"CEO BRIEFING SCHEDULER")
    print(f"{'='*60}")
    print(f"Schedule: Every {day_names[target_day]} at {target_hour:02d}:{target_minute:02d}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    next_run = get_next_run_time(target_day, target_hour, target_minute)
    print(f"Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    log_action(f"CEO Briefing Scheduler started - Schedule: {day_names[target_day]} at {target_hour:02d}:{target_minute:02d}", "INFO")

    last_run_date = None

    try:
        while True:
            now = datetime.now()

            # Check if we should run
            if should_run_now(target_day, target_hour, target_minute):
                # Prevent running multiple times in the same minute
                today = now.date()
                if last_run_date != today:
                    print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Generating CEO briefing...")
                    log_action("Scheduled CEO briefing generation triggered", "INFO")

                    try:
                        report_path = generate_ceo_briefing()
                        print(f"[SUCCESS] Briefing generated: {report_path}")
                        last_run_date = today

                        # Calculate next run
                        next_run = get_next_run_time(target_day, target_hour, target_minute)
                        print(f"[INFO] Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}\n")

                    except Exception as e:
                        log_action(f"Scheduled briefing generation failed: {str(e)}", "ERROR")
                        print(f"[ERROR] Failed to generate briefing: {str(e)}\n")

            # Sleep for 60 seconds before checking again
            time.sleep(60)

    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print(f"CEO Briefing Scheduler stopped by user")
        print(f"{'='*60}\n")
        log_action("CEO Briefing Scheduler stopped by user", "INFO")


def main():
    """
    Main entry point for scheduler.
    """
    parser = argparse.ArgumentParser(description="CEO Briefing Scheduler - Auto-generate weekly briefings")
    parser.add_argument("--day", default="monday", help="Day of week to run (default: monday)")
    parser.add_argument("--time", default="09:00", help="Time to run in HH:MM format (default: 09:00)")

    args = parser.parse_args()

    # Parse arguments
    target_day = get_day_number(args.day)
    target_hour, target_minute = parse_time(args.time)

    # Run scheduler
    run_scheduler(target_day, target_hour, target_minute)


if __name__ == "__main__":
    main()
