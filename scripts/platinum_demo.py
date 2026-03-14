#!/usr/bin/env python3
"""
Platinum Tier AI Employee - Demo Script
Demonstrates: Email arrives → Cloud drafts → Local approves → Send via MCP
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich import box

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
NEEDS_ACTION_EMAIL = VAULT_DIR / "Needs_Action" / "email"
PENDING_APPROVAL_EMAIL = VAULT_DIR / "Pending_Approval" / "email"
IN_PROGRESS_CLOUD = VAULT_DIR / "In_Progress" / "cloud"
IN_PROGRESS_LOCAL = VAULT_DIR / "In_Progress" / "local"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = VAULT_DIR / "Logs"

console = Console()


class PlatinumDemo:
    """Platinum Tier demo orchestrator"""

    def __init__(self):
        # Ensure directories exist
        for dir_path in [NEEDS_ACTION_EMAIL, PENDING_APPROVAL_EMAIL,
                         IN_PROGRESS_CLOUD, IN_PROGRESS_LOCAL, DONE_DIR, LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def print_header(self, title: str):
        """Print section header"""
        console.print(f"\n[bold blue]{'='*60}[/bold blue]")
        console.print(f"[bold blue]{title}[/bold blue]")
        console.print(f"[bold blue]{'='*60}[/bold blue]\n")

    def print_step(self, step_num: int, description: str):
        """Print step header"""
        console.print(f"\n[bold cyan]STEP {step_num}: {description}[/bold cyan]")
        console.print(f"[dim]{'─'*60}[/dim]\n")

    def wait_for_user(self, message: str = "Press Enter to continue..."):
        """Wait for user input"""
        console.print(f"\n[yellow]{message}[/yellow]")
        input()

    def step1_simulate_email_arrival(self):
        """Step 1: Simulate email arriving"""
        self.print_step(1, "Email Arrives (Simulated)")

        email_data = {
            "id": "email_001",
            "from": "client@example.com",
            "to": "you@company.com",
            "subject": "Urgent: Project Deadline Extension Request",
            "body": """Hi,

I hope this email finds you well. I'm writing to request a 2-week extension
on the current project deadline due to some unexpected technical challenges
we've encountered.

Could we schedule a call to discuss this?

Best regards,
John Smith
Client Success Manager""",
            "received_at": datetime.now().isoformat(),
            "priority": "high"
        }

        # Save email to Needs_Action
        email_file = NEEDS_ACTION_EMAIL / "email_001.json"
        with open(email_file, "w", encoding="utf-8") as f:
            json.dump(email_data, f, indent=2)

        # Display email
        table = Table(title="[bold]Incoming Email[/bold]", box=box.ROUNDED)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("From", email_data["from"])
        table.add_row("To", email_data["to"])
        table.add_row("Subject", email_data["subject"])
        table.add_row("Priority", f"[red]{email_data['priority'].upper()}[/red]")

        console.print(table)
        console.print(f"\n[dim]Email body:[/dim]")
        console.print(Panel(email_data["body"], border_style="dim"))

        console.print(f"\n[green]✓ Email saved to: {email_file}[/green]")
        console.print(f"[yellow]⚠ Local Agent is OFFLINE[/yellow]")

        self.wait_for_user()
        return email_file

    def step2_cloud_agent_processing(self, email_file: Path):
        """Step 2: Cloud Agent processes email"""
        self.print_step(2, "Cloud Agent Processing (Automated)")

        console.print("[cyan]CLOUD AGENT:[/cyan] Email detected in Needs_Action/")
        time.sleep(1)

        # Read email
        with open(email_file, "r", encoding="utf-8") as f:
            email_data = json.load(f)

        console.print("[cyan]CLOUD AGENT:[/cyan] Reading email content...")
        time.sleep(1)

        # Claim task (move to In_Progress/cloud)
        claimed_file = IN_PROGRESS_CLOUD / email_file.name
        email_file.rename(claimed_file)
        console.print(f"[cyan]CLOUD AGENT:[/cyan] Claimed task (moved to In_Progress/cloud/)")
        time.sleep(1)

        # Draft reply using Claude API (or fallback)
        console.print("[cyan]CLOUD AGENT:[/cyan] Drafting reply with Claude AI...")
        time.sleep(2)

        draft_reply = self.generate_draft_reply(email_data)

        # Create approval file
        approval_data = {
            "type": "email_approval",
            "created_at": datetime.now().isoformat(),
            "created_by": "cloud-agent",
            "original_email": email_data,
            "draft_reply": draft_reply,
            "status": "pending_approval"
        }

        approval_file = PENDING_APPROVAL_EMAIL / "email_001_approval.json"
        with open(approval_file, "w", encoding="utf-8") as f:
            json.dump(approval_data, f, indent=2)

        console.print(f"[green]✓ Draft reply generated[/green]")
        console.print(f"[green]✓ Approval file created: {approval_file}[/green]")

        # Show draft
        console.print(f"\n[bold]Draft Reply:[/bold]")
        console.print(Panel(draft_reply, border_style="green"))

        console.print(f"\n[cyan]CLOUD AGENT:[/cyan] [bold]Waiting for Local Agent approval...[/bold]")

        self.wait_for_user()
        return approval_file, claimed_file

    def generate_draft_reply(self, email_data: dict) -> str:
        """Generate draft reply (with fallback)"""
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")

            if api_key:
                client = anthropic.Anthropic(api_key=api_key)

                prompt = f"""Draft a professional reply to this email:

From: {email_data['from']}
Subject: {email_data['subject']}
Body:
{email_data['body']}

Write a professional, empathetic reply that:
1. Acknowledges their request
2. Proposes a meeting to discuss
3. Is concise and professional
"""

                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )

                return response.content[0].text

        except:
            pass

        # Fallback draft
        return f"""Hi John,

Thank you for reaching out regarding the project deadline extension.

I understand that unexpected technical challenges can arise, and I appreciate
you communicating this proactively. A 2-week extension is certainly something
we can discuss.

I'd be happy to schedule a call to review the situation in detail and work
out a revised timeline that works for both teams.

Could you share your availability for this week? I'm generally free on
Tuesday and Thursday afternoons.

Best regards,
[Your Name]"""

    def step3_local_agent_approval(self, approval_file: Path, claimed_file: Path):
        """Step 3: Local Agent returns and processes approval"""
        self.print_step(3, "Local Agent Returns Online")

        console.print("[green]LOCAL AGENT:[/green] Coming online...")
        time.sleep(1)

        console.print("[green]LOCAL AGENT:[/green] Checking for pending approvals...")
        time.sleep(1)

        console.print(f"[green]LOCAL AGENT:[/green] Found 1 pending approval: {approval_file.name}")
        time.sleep(1)

        # Read approval data
        with open(approval_file, "r", encoding="utf-8") as f:
            approval_data = json.load(f)

        # Show approval request
        console.print(f"\n[bold yellow]APPROVAL REQUEST[/bold yellow]")

        table = Table(box=box.ROUNDED)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("From", approval_data["original_email"]["from"])
        table.add_row("Subject", approval_data["original_email"]["subject"])
        table.add_row("Priority", approval_data["original_email"]["priority"].upper())

        console.print(table)

        console.print(f"\n[bold]Draft Reply:[/bold]")
        console.print(Panel(approval_data["draft_reply"], border_style="green"))

        # Request approval
        console.print()
        approved = Confirm.ask("[bold yellow]Approve and send this email?[/bold yellow]", default=True)

        if approved:
            # Move to In_Progress/local
            local_file = IN_PROGRESS_LOCAL / approval_file.name
            approval_file.rename(local_file)

            console.print(f"\n[green]LOCAL AGENT:[/green] Approval granted!")
            console.print(f"[green]LOCAL AGENT:[/green] Executing send via MCP...")
            time.sleep(2)

            # Simulate send (in real system, would use MCP)
            success = self.simulate_email_send(approval_data)

            if success:
                # Move to Done
                done_file = DONE_DIR / f"email_001_completed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

                completion_data = {
                    **approval_data,
                    "status": "completed",
                    "completed_at": datetime.now().isoformat(),
                    "completed_by": "local-agent"
                }

                with open(done_file, "w", encoding="utf-8") as f:
                    json.dump(completion_data, f, indent=2)

                # Clean up
                local_file.unlink()
                if claimed_file.exists():
                    claimed_file.unlink()

                console.print(f"[bold green]✓ Email sent successfully![/bold green]")
                console.print(f"[green]✓ Task moved to Done: {done_file}[/green]")

                # Log to system health
                self.log_to_system_health("Email sent successfully", "email_001")

                self.wait_for_user()
                return done_file
            else:
                console.print(f"[red]✗ Email send failed[/red]")
                return None
        else:
            console.print(f"\n[yellow]LOCAL AGENT:[/yellow] Approval rejected")
            console.print(f"[yellow]LOCAL AGENT:[/yellow] Moving back to Pending_Approval")
            return None

    def simulate_email_send(self, approval_data: dict) -> bool:
        """Simulate email send via MCP"""
        console.print("[green]LOCAL AGENT:[/green] Connecting to Gmail MCP...")
        time.sleep(1)

        console.print("[green]LOCAL AGENT:[/green] Sending email...")
        time.sleep(2)

        console.print("[green]LOCAL AGENT:[/green] Email delivered!")
        return True

    def log_to_system_health(self, message: str, task_id: str):
        """Log to system health"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n## Activity Log - {timestamp}\n\n"
        log_entry += f"- **Task:** {task_id}\n"
        log_entry += f"- **Action:** {message}\n"
        log_entry += f"- **Agent:** local-agent\n"

        health_file = LOGS_DIR / "system_health.md"
        with open(health_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def step4_show_final_state(self, done_file: Path):
        """Step 4: Show final state"""
        self.print_step(4, "Final State - Task Completed")

        # Show Done folder
        console.print("[bold]Done Folder Contents:[/bold]")
        done_files = list(DONE_DIR.glob("*.json"))
        for file in done_files:
            console.print(f"  [green]✓[/green] {file.name}")

        # Show task details
        if done_file and done_file.exists():
            console.print(f"\n[bold]Completed Task Details:[/bold]")
            with open(done_file, "r", encoding="utf-8") as f:
                task_data = json.load(f)

            table = Table(box=box.ROUNDED)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Task ID", task_data["original_email"]["id"])
            table.add_row("Status", f"[green]{task_data['status'].upper()}[/green]")
            table.add_row("Created By", task_data["created_by"])
            table.add_row("Completed By", task_data["completed_by"])
            table.add_row("Completed At", task_data["completed_at"])

            console.print(table)

        # Show system health log
        health_file = LOGS_DIR / "system_health.md"
        if health_file.exists():
            console.print(f"\n[bold]System Health Log (last 10 lines):[/bold]")
            with open(health_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    console.print(f"  [dim]{line.rstrip()}[/dim]")

        console.print(f"\n[bold green]DEMO COMPLETE![/bold green]")
        console.print(f"\n[bold]What was demonstrated:[/bold]")
        console.print("  [green]✓[/green] Email arrived while Local was offline")
        console.print("  [green]✓[/green] Cloud Agent drafted reply automatically")
        console.print("  [green]✓[/green] Cloud wrote approval file (no direct send)")
        console.print("  [green]✓[/green] Local Agent returned and showed approval")
        console.print("  [green]✓[/green] User approved the draft")
        console.print("  [green]✓[/green] Local executed send via MCP")
        console.print("  [green]✓[/green] Task logged and moved to Done")
        console.print("  [green]✓[/green] System health updated")

    def run(self):
        """Run complete demo"""
        self.print_header("PLATINUM TIER AI EMPLOYEE - DEMO")

        console.print("[bold]Scenario:[/bold]")
        console.print("Email arrives → Cloud drafts reply → Local approves → Send via MCP")
        console.print()

        self.wait_for_user("Press Enter to start demo...")

        # Step 1: Email arrives
        email_file = self.step1_simulate_email_arrival()

        # Step 2: Cloud processes
        approval_file, claimed_file = self.step2_cloud_agent_processing(email_file)

        # Step 3: Local approves
        done_file = self.step3_local_agent_approval(approval_file, claimed_file)

        # Step 4: Show final state
        if done_file:
            self.step4_show_final_state(done_file)


def main():
    """Main entry point"""
    demo = PlatinumDemo()
    demo.run()


if __name__ == "__main__":
    main()
