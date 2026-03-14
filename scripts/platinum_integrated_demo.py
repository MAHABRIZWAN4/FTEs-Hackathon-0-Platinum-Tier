#!/usr/bin/env python3
"""
Platinum Tier AI Employee - Integrated Demo
Complete automated demonstration of all features
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich import box

console = Console()

VAULT_DIR = Path("AI_Employee_Vault")


class IntegratedDemo:
    """Complete integrated demo"""

    def __init__(self):
        self.console = console
        self.start_time = datetime.now()

    def print_banner(self):
        """Print demo banner"""
        banner = """
================================================================

         PLATINUM TIER AI EMPLOYEE - INTEGRATED DEMO

  Demonstrating: Dual-Agent Architecture + Cloud Automation

================================================================
"""
        console.print(banner, style="bold blue")

    def show_architecture(self):
        """Show system architecture"""
        console.print("\n[bold cyan]SYSTEM ARCHITECTURE[/bold cyan]\n")

        arch = """
+---------------------+         +---------------------+
|   CLOUD AGENT       |         |   LOCAL AGENT       |
|   (GitHub Actions)  |<------->|   (Your Machine)    |
+---------------------+  Vault  +---------------------+
| - Email triage      |  Sync   | - Approvals         |
| - Draft replies     |  Every  | - Final send/post   |
| - Draft social      |  2 min  | - WhatsApp          |
| - NEVER sends       |         | - Payments          |
+---------------------+         +---------------------+
"""
        console.print(Panel(arch, title="Dual-Agent Architecture", border_style="cyan"))

    def show_workflow(self):
        """Show workflow steps"""
        console.print("\n[bold cyan]WORKFLOW DEMONSTRATION[/bold cyan]\n")

        table = Table(title="Demo Steps", box=box.ROUNDED)
        table.add_column("Step", style="cyan", width=8)
        table.add_column("Agent", style="yellow", width=12)
        table.add_column("Action", style="white")

        table.add_row("1", "System", "Email arrives in Needs_Action/")
        table.add_row("2", "Cloud", "Reads email, drafts reply with Claude AI")
        table.add_row("3", "Cloud", "Writes approval file to Pending_Approval/")
        table.add_row("4", "Cloud", "Moves original to In_Progress/cloud/")
        table.add_row("5", "Local", "Returns online, finds pending approval")
        table.add_row("6", "Local", "Shows draft to user for approval")
        table.add_row("7", "User", "Reviews and approves draft")
        table.add_row("8", "Local", "Executes send via Gmail MCP")
        table.add_row("9", "Local", "Logs activity to system_health.md")
        table.add_row("10", "Local", "Moves completed task to Done/")

        console.print(table)

    def show_security_model(self):
        """Show security model"""
        console.print("\n[bold cyan]SECURITY MODEL[/bold cyan]\n")

        table = Table(box=box.ROUNDED)
        table.add_column("Component", style="cyan")
        table.add_column("Cloud Agent", style="yellow")
        table.add_column("Local Agent", style="green")

        table.add_row("Email Access", "Read-only", "Full access")
        table.add_row("Send Emails", "❌ NO", "✓ YES (with approval)")
        table.add_row("Post Social", "❌ NO", "✓ YES (with approval)")
        table.add_row("Credentials", "API keys only", "All credentials")
        table.add_row("Approval", "N/A", "Required for all sends")

        console.print(table)

    def show_key_features(self):
        """Show key features"""
        console.print("\n[bold cyan]KEY FEATURES[/bold cyan]\n")

        features = [
            ("Claim-by-Move", "Tasks claimed by moving files (atomic, no race conditions)"),
            ("Single-Writer", "One agent per file prevents merge conflicts"),
            ("Draft-Only Cloud", "Cloud never sends - security by design"),
            ("Auto-Restart", "Watchdog monitors and restarts failed processes"),
            ("Health Monitoring", "Continuous system health checks every 5 minutes"),
            ("CEO Briefings", "Automated weekly executive summaries"),
            ("Vault Sync", "Git-based sync every 2 minutes (cloud + local)")
        ]

        for feature, description in features:
            console.print(f"  [green]✓[/green] [bold]{feature}:[/bold] {description}")

    def show_folder_structure(self):
        """Show folder structure"""
        console.print("\n[bold cyan]VAULT FOLDER STRUCTURE[/bold cyan]\n")

        structure = """
AI_Employee_Vault/
├── Needs_Action/
│   ├── email/          ← Email drafts ready for action
│   └── social/         ← Social post drafts ready
├── Pending_Approval/
│   ├── email/          ← Awaiting user approval
│   └── social/         ← Awaiting user approval
├── In_Progress/
│   ├── cloud/          ← Cloud agent working
│   └── local/          ← Local agent working
├── Done/               ← Completed tasks
├── Logs/               ← System logs
│   ├── cloud_agent.log
│   ├── local_agent.log
│   ├── watchdog.log
│   └── system_health.md
└── Briefings/          ← Weekly CEO briefings
"""
        console.print(Panel(structure, border_style="dim"))

    def show_metrics(self):
        """Show system metrics"""
        console.print("\n[bold cyan]SYSTEM METRICS[/bold cyan]\n")

        table = Table(box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Total Scripts", "15+")
        table.add_row("GitHub Workflows", "4")
        table.add_row("Documentation Files", "15")
        table.add_row("Lines of Code", "5,000+")
        table.add_row("Cloud Automation", "24/7")
        table.add_row("Sync Interval", "Every 2 minutes")
        table.add_row("Health Checks", "Every 5 minutes")

        console.print(table)

    def show_demo_summary(self):
        """Show demo summary"""
        console.print("\n[bold green]DEMO SUMMARY[/bold green]\n")

        console.print("[bold]What This Demo Shows:[/bold]")
        console.print("  [green]✓[/green] Dual-agent architecture (Cloud + Local)")
        console.print("  [green]✓[/green] Cloud drafts, Local approves and sends")
        console.print("  [green]✓[/green] Claim-by-move pattern (no race conditions)")
        console.print("  [green]✓[/green] Single-writer rule (no merge conflicts)")
        console.print("  [green]✓[/green] Security by design (draft-only cloud)")
        console.print("  [green]✓[/green] Complete task lifecycle (Needs_Action → Done)")
        console.print("  [green]✓[/green] Logging and health monitoring")
        console.print("  [green]✓[/green] Professional approval workflow")

        console.print("\n[bold]Production Features:[/bold]")
        console.print("  [green]✓[/green] 24/7 cloud automation via GitHub Actions")
        console.print("  [green]✓[/green] Health monitoring with auto-restart")
        console.print("  [green]✓[/green] Automated weekly CEO briefings")
        console.print("  [green]✓[/green] Git-based vault synchronization")
        console.print("  [green]✓[/green] Comprehensive documentation")

    def run(self):
        """Run integrated demo"""
        self.print_banner()

        console.print("\n[yellow]This demo will show you the complete Platinum Tier system.[/yellow]")
        console.print("[yellow]Press Enter to continue through each section...[/yellow]\n")
        input()

        # Show architecture
        self.show_architecture()
        input("\nPress Enter to continue...")

        # Show workflow
        self.show_workflow()
        input("\nPress Enter to continue...")

        # Show security model
        self.show_security_model()
        input("\nPress Enter to continue...")

        # Show key features
        self.show_key_features()
        input("\nPress Enter to continue...")

        # Show folder structure
        self.show_folder_structure()
        input("\nPress Enter to continue...")

        # Show metrics
        self.show_metrics()
        input("\nPress Enter to continue...")

        # Show summary
        self.show_demo_summary()

        console.print("\n[bold blue]Ready to run the interactive demo?[/bold blue]")
        console.print("[yellow]Run: python scripts/platinum_demo.py[/yellow]\n")

        elapsed = (datetime.now() - self.start_time).total_seconds()
        console.print(f"[dim]Demo presentation completed in {elapsed:.1f} seconds[/dim]\n")


def main():
    """Main entry point"""
    demo = IntegratedDemo()
    demo.run()


if __name__ == "__main__":
    main()
