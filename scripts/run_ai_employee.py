"""
Silver Scheduler Agent - AI Employee Orchestrator

This script is the master orchestrator for the AI Employee system.
It coordinates vault monitoring and task planning in a unified scheduling loop.

Features:
- Daemon mode (continuous) or once mode (single execution)
- Configurable interval (default: 5 minutes)
- Comprehensive logging with automatic rotation
- Lock file management (prevents duplicate instances)
- Statistics tracking and reporting
- Graceful shutdown handling

Usage:
    python scripts/run_ai_employee.py              # Daemon mode (default)
    python scripts/run_ai_employee.py --once       # Run once and exit
    python scripts/run_ai_employee.py --interval 600  # Custom interval
"""

import os
import sys
import time
import json
import argparse
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Rich library for beautiful terminal output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


# Configuration
INBOX_FOLDER = os.path.join("AI_Employee_Vault", "Inbox")
NEEDS_ACTION_FOLDER = os.path.join("AI_Employee_Vault", "Needs_Action")
LOGS_FOLDER = "logs"
LOG_FILE = os.path.join(LOGS_FOLDER, "ai_employee.log")
LOCK_FILE = os.path.join(LOGS_FOLDER, "ai_employee.lock")
PROCESSED_REGISTRY = os.path.join(LOGS_FOLDER, "processed.json")
TASK_PLANNER_SCRIPT = os.path.join("scripts", "task_planner.py")

# Defaults
DEFAULT_INTERVAL = 300  # 5 minutes
MAX_LOG_SIZE = 1 * 1024 * 1024  # 1 MB

# Global flag for graceful shutdown
shutdown_requested = False


class AIEmployeeScheduler:
    """
    Master orchestrator for the AI Employee system.
    """

    def __init__(self, mode: str = "daemon", interval: int = DEFAULT_INTERVAL):
        """
        Initialize the scheduler.

        Args:
            mode (str): "daemon" or "once"
            interval (int): Check interval in seconds
        """
        self.mode = mode
        self.interval = interval
        self.session_processed = 0
        self.session_errors = 0

        # Ensure directories exist
        os.makedirs(LOGS_FOLDER, exist_ok=True)
        os.makedirs(INBOX_FOLDER, exist_ok=True)
        os.makedirs(NEEDS_ACTION_FOLDER, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """
        Log a message to the log file with timestamp.

        Args:
            message (str): Message to log
            level (str): Log level (INFO, SUCCESS, WARNING, ERROR, CRITICAL)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [SCHEDULER] {message}\n"

        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)

            # Cyber-Silver Professional console output
            if RICH_AVAILABLE:
                if level == "ERROR" or level == "CRITICAL":
                    console.print(f"[bold red]🚫 FAIL:[/] [red]{message}[/red]")
                elif level == "SUCCESS":
                    console.print(f"[bold green]✅ DONE:[/] [green]{message}[/green]")
                elif level == "WARNING":
                    console.print(f"[bold yellow]🔍 SCAN:[/] [yellow]{message}[/yellow]")
                elif level == "STATS":
                    console.print(f"[bold cyan]⚡ EXEC:[/] [bright_white]{message}[/bright_white]")
                else:
                    console.print(f"[bold cyan]⚡ EXEC:[/] [cyan]{message}[/cyan]")
            else:
                print(f"[{level}] {message}")
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[bold red]🚫 FAIL:[/] Failed to write to log: {e}")
            else:
                print(f"[ERROR] Failed to write to log: {e}")

    def check_log_size_and_rotate(self):
        """
        Check log file size and rotate if it exceeds MAX_LOG_SIZE.
        """
        try:
            if not os.path.exists(LOG_FILE):
                return

            size = os.path.getsize(LOG_FILE)
            if size > MAX_LOG_SIZE:
                # Create rotated filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                rotated_name = f"ai_employee_{timestamp}.log"
                rotated_path = os.path.join(LOGS_FOLDER, rotated_name)

                # Rename current log
                os.rename(LOG_FILE, rotated_path)

                # Log rotation in new file
                self.log(f"Log rotated to {rotated_name} (size: {size / 1024 / 1024:.2f} MB)", "INFO")

        except Exception as e:
            self.log(f"Failed to rotate log: {str(e)}", "WARNING")

    def create_lock_file(self) -> bool:
        """
        Create a lock file with current PID to prevent duplicate instances.

        Returns:
            bool: True if lock created successfully, False if another instance is running
        """
        try:
            # Check if lock file exists
            if os.path.exists(LOCK_FILE):
                # Read existing lock
                with open(LOCK_FILE, "r", encoding="utf-8") as f:
                    lock_data = json.load(f)

                pid = lock_data.get("pid")
                started_at = lock_data.get("started_at")

                # Check if process is still running
                if self.is_process_running(pid):
                    self.log(f"Another instance is already running (PID: {pid}, started: {started_at})", "ERROR")
                    return False
                else:
                    self.log(f"Removing stale lock file (PID: {pid} not running)", "WARNING")
                    os.remove(LOCK_FILE)

            # Create new lock file
            lock_data = {
                "pid": os.getpid(),
                "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "mode": self.mode
            }

            with open(LOCK_FILE, "w", encoding="utf-8") as f:
                json.dump(lock_data, f, indent=2)

            return True

        except Exception as e:
            self.log(f"Failed to create lock file: {str(e)}", "ERROR")
            return False

    def remove_lock_file(self):
        """
        Remove the lock file on shutdown.
        """
        try:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
                self.log("Lock file removed", "INFO")
        except Exception as e:
            self.log(f"Failed to remove lock file: {str(e)}", "WARNING")

    def is_process_running(self, pid: int) -> bool:
        """
        Check if a process with given PID is running.

        Args:
            pid (int): Process ID to check

        Returns:
            bool: True if process is running
        """
        if not pid:
            return False

        try:
            if sys.platform == "win32":
                # Windows: Use tasklist
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True,
                    text=True
                )
                return str(pid) in result.stdout
            else:
                # Linux/Mac: Use ps
                result = subprocess.run(
                    ["ps", "-p", str(pid)],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
        except Exception:
            return False

    def get_inbox_files(self) -> List[str]:
        """
        Get list of .md files in Inbox.

        Returns:
            List[str]: List of .md filenames
        """
        try:
            if not os.path.exists(INBOX_FOLDER):
                return []

            files = []
            for filename in os.listdir(INBOX_FOLDER):
                filepath = os.path.join(INBOX_FOLDER, filename)
                if os.path.isfile(filepath) and filename.endswith('.md'):
                    files.append(filename)

            return files
        except Exception as e:
            self.log(f"Error scanning inbox: {str(e)}", "ERROR")
            return []

    def get_active_tasks(self) -> int:
        """
        Count files in Needs_Action folder.

        Returns:
            int: Number of active tasks
        """
        try:
            if not os.path.exists(NEEDS_ACTION_FOLDER):
                return 0

            count = 0
            for filename in os.listdir(NEEDS_ACTION_FOLDER):
                filepath = os.path.join(NEEDS_ACTION_FOLDER, filename)
                if os.path.isfile(filepath) and filename.endswith('.md'):
                    count += 1

            return count
        except Exception as e:
            self.log(f"Error counting active tasks: {str(e)}", "ERROR")
            return 0

    def get_processed_count(self) -> int:
        """
        Get total number of processed files from registry.

        Returns:
            int: Total processed files
        """
        try:
            if not os.path.exists(PROCESSED_REGISTRY):
                return 0

            with open(PROCESSED_REGISTRY, "r", encoding="utf-8") as f:
                data = json.load(f)

            return len(data.get("processed_files", []))
        except Exception:
            return 0

    def get_new_files(self, inbox_files: List[str]) -> List[str]:
        """
        Get list of files that haven't been processed yet.

        Args:
            inbox_files (List[str]): All files in inbox

        Returns:
            List[str]: New files not yet processed
        """
        try:
            if not os.path.exists(PROCESSED_REGISTRY):
                return inbox_files

            with open(PROCESSED_REGISTRY, "r", encoding="utf-8") as f:
                data = json.load(f)

            processed_files = set()
            for entry in data.get("processed_files", []):
                processed_files.add(entry.get("filename"))

            new_files = [f for f in inbox_files if f not in processed_files]
            return new_files

        except Exception as e:
            self.log(f"Error checking processed files: {str(e)}", "WARNING")
            return inbox_files

    def run_task_planner(self) -> bool:
        """
        Execute the task planner script.

        Returns:
            bool: True if successful
        """
        try:
            self.log("Triggering task planner", "INFO")

            result = subprocess.run(
                [sys.executable, TASK_PLANNER_SCRIPT],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode == 0:
                # Parse output for success count
                output = result.stdout
                if "Processed:" in output:
                    # Extract processed count from output
                    for line in output.split('\n'):
                        if "Processed:" in line:
                            self.log(f"Task planner: {line.strip()}", "SUCCESS")
                            break
                return True
            else:
                self.log(f"Task planner failed: {result.stderr[:200]}", "ERROR")
                self.session_errors += 1
                return False

        except subprocess.TimeoutExpired:
            self.log("Task planner timed out", "ERROR")
            self.session_errors += 1
            return False
        except Exception as e:
            self.log(f"Error running task planner: {str(e)}", "ERROR")
            self.session_errors += 1
            return False

    def log_statistics(self, inbox_files: List[str], new_files: List[str]):
        """
        Log system statistics.

        Args:
            inbox_files (List[str]): All inbox files
            new_files (List[str]): New files to process
        """
        active_tasks = self.get_active_tasks()
        total_processed = self.get_processed_count()

        stats = (
            f"Inbox: {len(new_files)} new, {len(inbox_files)} total | "
            f"Active Tasks: {active_tasks} | "
            f"Processed: {self.session_processed} this session, {total_processed} total"
        )

        # Beautiful table for statistics
        if RICH_AVAILABLE:
            table = Table(title="📊 System Statistics", border_style="cyan", show_header=True, header_style="bold bright_white")
            table.add_column("Metric", style="cyan", justify="left")
            table.add_column("Value", style="bright_white", justify="center")

            table.add_row("📥 New Files", f"[bold green]{len(new_files)}[/bold green]")
            table.add_row("📁 Total Inbox", f"[cyan]{len(inbox_files)}[/cyan]")
            table.add_row("⚡ Active Tasks", f"[yellow]{active_tasks}[/yellow]")
            table.add_row("✅ Session Processed", f"[green]{self.session_processed}[/green]")
            table.add_row("📊 Total Processed", f"[bold cyan]{total_processed}[/bold cyan]")

            console.print(table)
            console.print()

        self.log(stats, "STATS")

    def process_cycle(self):
        """
        Execute one processing cycle.
        """
        try:
            # Scan inbox
            inbox_files = self.get_inbox_files()
            new_files = self.get_new_files(inbox_files)

            # Log statistics
            self.log_statistics(inbox_files, new_files)

            # Process new files if any
            if new_files:
                self.log(f"Found {len(new_files)} new file(s) to process", "INFO")

                # Get count before processing
                before_count = self.get_processed_count()

                # Run task planner
                if self.run_task_planner():
                    # Get count after processing
                    after_count = self.get_processed_count()
                    processed_this_cycle = after_count - before_count
                    self.session_processed += processed_this_cycle
                    self.log(f"Processed {processed_this_cycle} file(s) successfully", "SUCCESS")
            else:
                self.log("No new files to process", "INFO")

            # Check and rotate log if needed
            self.check_log_size_and_rotate()

        except Exception as e:
            self.log(f"Error in processing cycle: {str(e)}", "ERROR")
            self.session_errors += 1

    def run_once(self):
        """
        Run a single processing cycle and exit.
        """
        # Cyber-Silver Professional Header
        if RICH_AVAILABLE:
            console.print()
            console.print(Panel.fit(
                "[bold cyan]★ ════════════════════════════════════════ ★[/bold cyan]\n"
                "[bold bright_white]🤖 SILVER SCHEDULER AGENT[/bold bright_white]\n"
                "[dim cyan]AI Employee Orchestrator[/dim cyan]\n"
                "[yellow]Mode:[/yellow] [bright_white]Single Execution[/bright_white]\n"
                "[bold cyan]★ ════════════════════════════════════════ ★[/bold cyan]",
                border_style="bold cyan",
                padding=(1, 2)
            ))
            console.print()

        self.log(f"AI Employee started (mode=once)", "INFO")

        # Create lock file
        if not self.create_lock_file():
            return False

        try:
            # Run one cycle
            self.process_cycle()

            # Log summary
            self.log(
                f"Session complete - Processed: {self.session_processed}, Errors: {self.session_errors}",
                "INFO"
            )

            return True

        finally:
            self.remove_lock_file()

    def run_daemon(self):
        """
        Run continuously in daemon mode.
        """
        # Cyber-Silver Professional Header
        if RICH_AVAILABLE:
            console.print()
            console.print(Panel.fit(
                "[bold cyan]★ ════════════════════════════════════════ ★[/bold cyan]\n"
                "[bold bright_white]🤖 SILVER SCHEDULER AGENT[/bold bright_white]\n"
                "[dim cyan]AI Employee Orchestrator[/dim cyan]\n"
                f"[yellow]Mode:[/yellow] [bright_white]Daemon (Interval: {self.interval}s)[/bright_white]\n"
                "[bold cyan]★ ════════════════════════════════════════ ★[/bold cyan]",
                border_style="bold cyan",
                padding=(1, 2)
            ))
            console.print()

        self.log(f"AI Employee started (mode=daemon, interval={self.interval}s)", "INFO")

        # Create lock file
        if not self.create_lock_file():
            return False

        try:
            cycle_count = 0

            while not shutdown_requested:
                cycle_count += 1
                self.log(f"Starting cycle #{cycle_count}", "INFO")

                # Run processing cycle
                self.process_cycle()

                # Log heartbeat
                if cycle_count % 5 == 0:  # Every 5 cycles
                    self.log(
                        f"Heartbeat - Cycles: {cycle_count}, Processed: {self.session_processed}, Errors: {self.session_errors}",
                        "INFO"
                    )

                # Sleep until next cycle
                if not shutdown_requested:
                    self.log(f"Sleeping for {self.interval}s until next cycle", "INFO")
                    time.sleep(self.interval)

            self.log("Shutdown requested, exiting gracefully", "INFO")
            return True

        except Exception as e:
            self.log(f"Fatal error in daemon loop: {str(e)}", "CRITICAL")
            return False

        finally:
            self.remove_lock_file()

            # Beautiful session summary
            if RICH_AVAILABLE:
                console.print()
                console.print(Panel(
                    "[bold cyan]★ ═══════════════════════════════════ ★[/bold cyan]\n"
                    "[bold bright_white]📊 Session Summary[/bold bright_white]\n"
                    f"[yellow]Cycles:[/yellow] [bright_white]{cycle_count}[/bright_white]\n"
                    f"[green]Processed:[/green] [bright_white]{self.session_processed}[/bright_white]\n"
                    f"[red]Errors:[/red] [bright_white]{self.session_errors}[/bright_white]\n"
                    "[bold cyan]★ ═══════════════════════════════════ ★[/bold cyan]",
                    border_style="bold cyan",
                    padding=(1, 2)
                ))
                console.print()

            self.log(
                f"Session ended - Cycles: {cycle_count}, Processed: {self.session_processed}, Errors: {self.session_errors}",
                "INFO"
            )

    def run(self):
        """
        Main entry point - runs in configured mode.
        """
        if self.mode == "once":
            return self.run_once()
        else:
            return self.run_daemon()


def signal_handler(signum, frame):
    """
    Handle shutdown signals gracefully.
    """
    global shutdown_requested
    shutdown_requested = True

    if RICH_AVAILABLE:
        console.print()
        console.print("[bold yellow]⚠️  Shutdown signal received, finishing current cycle...[/bold yellow]")
    else:
        print("\n[INFO] Shutdown signal received, finishing current cycle...")


def main():
    """
    Main entry point for command-line usage.
    """
    parser = argparse.ArgumentParser(
        description="Silver Scheduler - AI Employee Orchestrator"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (default: daemon mode)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run continuously (explicit daemon mode)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Check interval in seconds (default: {DEFAULT_INTERVAL})"
    )

    args = parser.parse_args()

    # Determine mode
    if args.once:
        mode = "once"
    else:
        mode = "daemon"

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

    # Create and run scheduler
    scheduler = AIEmployeeScheduler(mode=mode, interval=args.interval)

    try:
        success = scheduler.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print()
            console.print("[bold yellow]⚠️  Interrupted by user[/bold yellow]")
        else:
            print("\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        if RICH_AVAILABLE:
            console.print()
            console.print(Panel(
                f"[bold red]🚫 FAIL: Fatal error[/bold red]\n"
                f"[red]{e}[/red]",
                border_style="red",
                padding=(1, 2)
            ))
            console.print()
        else:
            print(f"\n[CRITICAL] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
