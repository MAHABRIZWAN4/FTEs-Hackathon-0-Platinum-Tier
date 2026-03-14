#!/usr/bin/env python3
"""
Health Check - Quick System Status
Shows all process status, pending tasks, and system health
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
LOGS_DIR = VAULT_DIR / "Logs"

console = Console()


class HealthCheck:
    """Quick system health checker"""

    def __init__(self):
        self.vault_dir = VAULT_DIR
        self.logs_dir = LOGS_DIR

    def check_github_workflows(self) -> dict:
        """Check GitHub Actions workflow status"""
        workflows = {}

        try:
            result = subprocess.run(
                ["gh", "run", "list", "--limit", "4", "--json", "name,status,conclusion,createdAt"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                runs = json.loads(result.stdout)
                for run in runs:
                    name = run.get("name", "")
                    status = run.get("status", "unknown")
                    conclusion = run.get("conclusion", "")
                    created_at = run.get("createdAt", "")

                    workflows[name] = {
                        "status": conclusion if conclusion else status,
                        "time": created_at
                    }

        except Exception as e:
            console.print(f"[yellow]Could not check GitHub Actions: {e}[/yellow]")

        return workflows

    def get_pending_counts(self) -> dict:
        """Get counts of pending items"""
        counts = {
            "pending_approval_email": 0,
            "pending_approval_social": 0,
            "needs_action_email": 0,
            "needs_action_social": 0,
            "in_progress_cloud": 0,
            "in_progress_local": 0
        }

        try:
            pending_email = self.vault_dir / "Pending_Approval" / "email"
            if pending_email.exists():
                counts["pending_approval_email"] = len(list(pending_email.glob("*.json")))

            pending_social = self.vault_dir / "Pending_Approval" / "social"
            if pending_social.exists():
                counts["pending_approval_social"] = len(list(pending_social.glob("*.json")))

            needs_email = self.vault_dir / "Needs_Action" / "email"
            if needs_email.exists():
                counts["needs_action_email"] = len(list(needs_email.glob("*.json")))

            needs_social = self.vault_dir / "Needs_Action" / "social"
            if needs_social.exists():
                counts["needs_action_social"] = len(list(needs_social.glob("*.json")))

            in_progress_cloud = self.vault_dir / "In_Progress" / "cloud"
            if in_progress_cloud.exists():
                counts["in_progress_cloud"] = len(list(in_progress_cloud.glob("*.json")))

            in_progress_local = self.vault_dir / "In_Progress" / "local"
            if in_progress_local.exists():
                counts["in_progress_local"] = len(list(in_progress_local.glob("*.json")))

        except Exception as e:
            console.print(f"[red]Error getting counts: {e}[/red]")

        return counts

    def get_last_sync_time(self) -> str:
        """Get last vault sync time"""
        try:
            sync_log = Path("logs/sync.log")
            if sync_log.exists():
                with open(sync_log, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in reversed(lines):
                        if "Vault sync completed successfully" in line:
                            timestamp_str = line.split("]")[0].strip("[")
                            return timestamp_str
        except:
            pass

        return "Never"

    def display_workflows(self, workflows: dict):
        """Display GitHub Actions workflow status"""
        table = Table(title="☁️ GitHub Actions Workflows", box=box.ROUNDED)
        table.add_column("Workflow", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Last Run", style="dim")

        for name, info in workflows.items():
            status = info["status"]
            time_str = info["time"][:19] if info["time"] else "Unknown"

            if status == "success":
                status_display = "[green]✓ Success[/green]"
            elif status == "failure":
                status_display = "[red]✗ Failed[/red]"
            elif status in ["in_progress", "queued"]:
                status_display = "[yellow]⟳ Running[/yellow]"
            else:
                status_display = f"[dim]{status}[/dim]"

            table.add_row(name, status_display, time_str)

        console.print(table)

    def display_pending_tasks(self, counts: dict):
        """Display pending tasks"""
        table = Table(title="📋 Pending Tasks", box=box.ROUNDED)
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="white", justify="right")

        total_pending = counts["pending_approval_email"] + counts["pending_approval_social"]
        total_needs_action = counts["needs_action_email"] + counts["needs_action_social"]
        total_in_progress = counts["in_progress_cloud"] + counts["in_progress_local"]

        table.add_row("Pending Approval (Email)", str(counts["pending_approval_email"]))
        table.add_row("Pending Approval (Social)", str(counts["pending_approval_social"]))
        table.add_row("Needs Action (Email)", str(counts["needs_action_email"]))
        table.add_row("Needs Action (Social)", str(counts["needs_action_social"]))
        table.add_row("In Progress (Cloud)", str(counts["in_progress_cloud"]))
        table.add_row("In Progress (Local)", str(counts["in_progress_local"]))
        table.add_row("", "")
        table.add_row("[bold]Total Pending Approval[/bold]", f"[bold]{total_pending}[/bold]")
        table.add_row("[bold]Total Needs Action[/bold]", f"[bold]{total_needs_action}[/bold]")
        table.add_row("[bold]Total In Progress[/bold]", f"[bold]{total_in_progress}[/bold]")

        console.print(table)

    def display_system_info(self, last_sync: str):
        """Display system information"""
        table = Table(title="🖥️ System Information", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Last Vault Sync", last_sync)
        table.add_row("Current Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Check if health report exists
        health_file = self.logs_dir / "system_health.md"
        if health_file.exists():
            mod_time = datetime.fromtimestamp(health_file.stat().st_mtime)
            table.add_row("Last Health Check", mod_time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            table.add_row("Last Health Check", "Never")

        console.print(table)

    def display_alerts(self, counts: dict):
        """Display system alerts"""
        alerts = []

        total_pending = counts["pending_approval_email"] + counts["pending_approval_social"]
        total_in_progress = counts["in_progress_cloud"] + counts["in_progress_local"]

        if total_pending > 20:
            alerts.append("⚠️  HIGH PENDING APPROVALS: More than 20 items awaiting approval")

        if total_in_progress > 10:
            alerts.append("⚠️  STUCK TASKS: More than 10 tasks in progress")

        if total_pending == 0 and total_in_progress == 0:
            alerts.append("✅ All clear - No pending tasks")

        if alerts:
            console.print("\n[bold yellow]🚨 Alerts:[/bold yellow]")
            for alert in alerts:
                console.print(f"  {alert}")

    def run(self):
        """Run health check"""
        console.print("\n[bold blue]====================================================[/bold blue]")
        console.print("[bold blue]  System Health Check - Platinum Tier AI Employee[/bold blue]")
        console.print("[bold blue]====================================================[/bold blue]\n")

        # Check GitHub workflows
        console.print("[cyan]Checking GitHub Actions...[/cyan]")
        workflows = self.check_github_workflows()
        self.display_workflows(workflows)

        console.print()

        # Get pending counts
        console.print("[cyan]Checking pending tasks...[/cyan]")
        counts = self.get_pending_counts()
        self.display_pending_tasks(counts)

        console.print()

        # Get system info
        console.print("[cyan]Checking system status...[/cyan]")
        last_sync = self.get_last_sync_time()
        self.display_system_info(last_sync)

        console.print()

        # Display alerts
        self.display_alerts(counts)

        console.print("\n[bold green]Health check completed[/bold green]\n")


def main():
    """Main entry point"""
    checker = HealthCheck()
    checker.run()


if __name__ == "__main__":
    main()
