#!/usr/bin/env python3
"""
Local Agent - Local Machine Worker
Responsibilities: Approvals, final send/post actions, WhatsApp, payments
Monitors Pending_Approval folders and executes approved actions
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich import box

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
PENDING_APPROVAL_EMAIL = VAULT_DIR / "Pending_Approval" / "email"
PENDING_APPROVAL_SOCIAL = VAULT_DIR / "Pending_Approval" / "social"
APPROVED_DIR = VAULT_DIR / "Approved"
IN_PROGRESS_LOCAL = VAULT_DIR / "In_Progress" / "local"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = VAULT_DIR / "Logs"

console = Console()


class LocalAgent:
    """Local agent that handles approvals and executes actions"""

    def __init__(self):
        self.agent_id = "local-agent"

        # Ensure directories exist
        for dir_path in [PENDING_APPROVAL_EMAIL, PENDING_APPROVAL_SOCIAL,
                         APPROVED_DIR, IN_PROGRESS_LOCAL, DONE_DIR, LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def log(self, message, level="INFO"):
        """Log message to local agent log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        log_file = LOGS_DIR / "local_agent.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        console.print(f"[cyan][LOCAL][/cyan] {message}")

    def claim_task(self, task_file: Path) -> Path:
        """
        Claim task by moving to In_Progress/local/
        Returns new path or None if already claimed
        """
        if not task_file.exists():
            return None

        claimed_path = IN_PROGRESS_LOCAL / task_file.name

        try:
            shutil.move(str(task_file), str(claimed_path))
            self.log(f"Claimed task: {task_file.name}")
            return claimed_path
        except FileNotFoundError:
            self.log(f"Task already claimed: {task_file.name}", "WARNING")
            return None

    def release_task(self, task_file: Path, destination: Path):
        """Move task from In_Progress to destination"""
        if task_file.exists():
            dest_path = destination / task_file.name
            shutil.move(str(task_file), str(dest_path))
            self.log(f"Released task to {destination.name}: {task_file.name}")

    def display_email_approval(self, draft_data: dict) -> bool:
        """Display email draft and request approval"""
        original = draft_data.get("original_email", {})
        triage = draft_data.get("triage", {})

        # Create approval panel
        table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
        table.add_column("Field", style="cyan bold")
        table.add_column("Value", style="white")

        table.add_row("From", original.get("from", "Unknown"))
        table.add_row("Subject", original.get("subject", "No subject"))
        table.add_row("Priority", f"[{'red' if triage.get('priority') == 'high' else 'yellow' if triage.get('priority') == 'medium' else 'green'}]{triage.get('priority', 'unknown').upper()}[/]")
        table.add_row("Category", triage.get("category", "unknown"))

        console.print("\n")
        console.print(Panel(table, title="[bold blue]📧 Email Approval Request[/bold blue]", border_style="blue"))

        # Show original email
        console.print("\n[bold]Original Email:[/bold]")
        console.print(Panel(original.get("body", "No content")[:500], border_style="dim"))

        # Show draft reply
        draft_reply = triage.get("draft_reply")
        if draft_reply:
            console.print("\n[bold]Draft Reply:[/bold]")
            console.print(Panel(draft_reply, border_style="green"))

        # Show reasoning
        console.print("\n[bold]AI Reasoning:[/bold]")
        console.print(f"[dim]{triage.get('reasoning', 'No reasoning provided')}[/dim]")

        # Show next steps
        next_steps = triage.get("next_steps", [])
        if next_steps:
            console.print("\n[bold]Suggested Next Steps:[/bold]")
            for i, step in enumerate(next_steps, 1):
                console.print(f"  {i}. {step}")

        # Request approval
        console.print("\n")
        return Confirm.ask("[bold yellow]Approve and send this email?[/bold yellow]", default=False)

    def display_social_approval(self, draft_data: dict) -> bool:
        """Display social post draft and request approval"""
        platform = draft_data.get("platform", "unknown")
        topic = draft_data.get("topic", "No topic")
        post_data = draft_data.get("post_data", {})

        # Create approval panel
        table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
        table.add_column("Field", style="cyan bold")
        table.add_column("Value", style="white")

        table.add_row("Platform", platform.upper())
        table.add_row("Topic", topic)
        table.add_row("Best Time", post_data.get("best_time_to_post", "Anytime"))

        console.print("\n")
        console.print(Panel(table, title="[bold blue]📱 Social Post Approval Request[/bold blue]", border_style="blue"))

        # Show post content
        console.print("\n[bold]Post Content:[/bold]")
        console.print(Panel(post_data.get("post_text", "No content"), border_style="green"))

        # Show hashtags
        hashtags = post_data.get("hashtags", [])
        if hashtags:
            console.print("\n[bold]Hashtags:[/bold]")
            console.print(" ".join([f"#{tag}" for tag in hashtags]))

        # Show media suggestion
        media = post_data.get("media_suggestion")
        if media:
            console.print("\n[bold]Media Suggestion:[/bold]")
            console.print(f"[dim]{media}[/dim]")

        # Show reasoning
        console.print("\n[bold]AI Reasoning:[/bold]")
        console.print(f"[dim]{post_data.get('reasoning', 'No reasoning provided')}[/dim]")

        # Request approval
        console.print("\n")
        return Confirm.ask(f"[bold yellow]Approve and post to {platform}?[/bold yellow]", default=False)

    def execute_email_send(self, draft_data: dict) -> bool:
        """Execute email send via send_email.py"""
        try:
            original = draft_data.get("original_email", {})
            triage = draft_data.get("triage", {})

            # Prepare email data for send_email.py
            email_data = {
                "to": original.get("from"),
                "subject": f"Re: {original.get('subject', '')}",
                "body": triage.get("draft_reply", ""),
                "reply_to": original.get("id")
            }

            # Save to temp file
            temp_file = Path("temp_email_send.json")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(email_data, f, indent=2)

            # Execute send_email.py
            result = subprocess.run(
                ["python", "scripts/send_email.py", "--file", str(temp_file)],
                capture_output=True,
                text=True
            )

            # Clean up temp file
            temp_file.unlink(missing_ok=True)

            if result.returncode == 0:
                self.log(f"Email sent successfully to {email_data['to']}")
                return True
            else:
                self.log(f"Email send failed: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Error executing email send: {e}", "ERROR")
            return False

    def execute_social_post(self, draft_data: dict) -> bool:
        """Execute social post via platform-specific script"""
        try:
            platform = draft_data.get("platform", "").lower()
            post_data = draft_data.get("post_data", {})

            # Map platform to script
            script_map = {
                "linkedin": "scripts/post_linkedin.py",
                "twitter": "scripts/post_twitter.py",
                "facebook": "scripts/post_facebook.py",
                "instagram": "scripts/post_instagram.py"
            }

            script = script_map.get(platform)
            if not script:
                self.log(f"Unknown platform: {platform}", "ERROR")
                return False

            # Prepare post data
            post_text = post_data.get("post_text", "")
            hashtags = post_data.get("hashtags", [])
            full_text = f"{post_text}\n\n{' '.join(['#' + tag for tag in hashtags])}"

            # Save to temp file
            temp_file = Path("temp_social_post.json")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump({"text": full_text}, f, indent=2)

            # Execute platform script
            result = subprocess.run(
                ["python", script, "--file", str(temp_file)],
                capture_output=True,
                text=True
            )

            # Clean up temp file
            temp_file.unlink(missing_ok=True)

            if result.returncode == 0:
                self.log(f"Posted successfully to {platform}")
                return True
            else:
                self.log(f"Post failed: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Error executing social post: {e}", "ERROR")
            return False

    def process_email_approvals(self):
        """Process pending email approvals"""
        email_files = list(PENDING_APPROVAL_EMAIL.glob("*.json"))

        if not email_files:
            return

        console.print(f"\n[bold cyan]Found {len(email_files)} email(s) pending approval[/bold cyan]")

        for email_file in email_files:
            # Claim task
            claimed_path = self.claim_task(email_file)
            if not claimed_path:
                continue

            try:
                # Load draft data
                with open(claimed_path, "r", encoding="utf-8") as f:
                    draft_data = json.load(f)

                # Display and request approval
                approved = self.display_email_approval(draft_data)

                if approved:
                    # Move to Approved
                    self.release_task(claimed_path, APPROVED_DIR)

                    # Execute send
                    success = self.execute_email_send(draft_data)

                    if success:
                        # Move to Done
                        approved_path = APPROVED_DIR / claimed_path.name
                        if approved_path.exists():
                            self.release_task(approved_path, DONE_DIR)
                        console.print("[bold green]✓ Email sent successfully![/bold green]")
                    else:
                        console.print("[bold red]✗ Email send failed - check logs[/bold red]")
                else:
                    # Rejected - move back to Pending
                    self.release_task(claimed_path, PENDING_APPROVAL_EMAIL)
                    console.print("[yellow]Email approval rejected[/yellow]")

            except Exception as e:
                self.log(f"Error processing email approval {email_file.name}: {e}", "ERROR")
                if claimed_path.exists():
                    self.release_task(claimed_path, PENDING_APPROVAL_EMAIL)

    def process_social_approvals(self):
        """Process pending social post approvals"""
        social_files = list(PENDING_APPROVAL_SOCIAL.glob("*.json"))

        if not social_files:
            return

        console.print(f"\n[bold cyan]Found {len(social_files)} social post(s) pending approval[/bold cyan]")

        for social_file in social_files:
            # Claim task
            claimed_path = self.claim_task(social_file)
            if not claimed_path:
                continue

            try:
                # Load draft data
                with open(claimed_path, "r", encoding="utf-8") as f:
                    draft_data = json.load(f)

                # Display and request approval
                approved = self.display_social_approval(draft_data)

                if approved:
                    # Move to Approved
                    self.release_task(claimed_path, APPROVED_DIR)

                    # Execute post
                    success = self.execute_social_post(draft_data)

                    if success:
                        # Move to Done
                        approved_path = APPROVED_DIR / claimed_path.name
                        if approved_path.exists():
                            self.release_task(approved_path, DONE_DIR)
                        console.print("[bold green]✓ Posted successfully![/bold green]")
                    else:
                        console.print("[bold red]✗ Post failed - check logs[/bold red]")
                else:
                    # Rejected - move back to Pending
                    self.release_task(claimed_path, PENDING_APPROVAL_SOCIAL)
                    console.print("[yellow]Social post approval rejected[/yellow]")

            except Exception as e:
                self.log(f"Error processing social approval {social_file.name}: {e}", "ERROR")
                if claimed_path.exists():
                    self.release_task(claimed_path, PENDING_APPROVAL_SOCIAL)

    def update_dashboard(self):
        """Update dashboard via dashboard_updater.py"""
        try:
            result = subprocess.run(
                ["python", "scripts/dashboard_updater.py"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.log("Dashboard updated successfully")
            else:
                self.log(f"Dashboard update failed: {result.stderr}", "ERROR")

        except Exception as e:
            self.log(f"Error updating dashboard: {e}", "ERROR")

    def run(self):
        """Run local agent main loop"""
        console.print("\n[bold blue]====================================================[/bold blue]")
        console.print("[bold blue]  Local Agent - Approval & Execution System[/bold blue]")
        console.print("[bold blue]====================================================[/bold blue]\n")

        self.log("Local Agent starting")

        try:
            # Process email approvals
            self.process_email_approvals()

            # Process social approvals
            self.process_social_approvals()

            # Update dashboard
            self.update_dashboard()

            self.log("Local Agent cycle completed")
            console.print("\n[bold green]Local Agent cycle completed[/bold green]\n")

        except KeyboardInterrupt:
            console.print("\n[yellow]Local Agent interrupted by user[/yellow]")
            self.log("Local Agent interrupted by user", "WARNING")

        except Exception as e:
            console.print(f"\n[bold red]Error: {e}[/bold red]")
            self.log(f"Local Agent error: {e}", "ERROR")
            raise


def main():
    """Main entry point"""
    agent = LocalAgent()
    agent.run()


if __name__ == "__main__":
    main()
