#!/usr/bin/env python3
"""
Platinum CEO Briefing Generator
Generates weekly executive summary from all system data sources
"""

import os
import json
import anthropic
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
DONE_DIR = VAULT_DIR / "Done"
ACCOUNTING_FILE = VAULT_DIR / "Accounting" / "Current_Month.md"
HEALTH_FILE = VAULT_DIR / "Logs" / "system_health.md"
BRIEFINGS_DIR = VAULT_DIR / "Briefings"
LOGS_DIR = VAULT_DIR / "Logs"


class PlatinumCEOBriefing:
    """Generates comprehensive CEO briefings"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Ensure directories exist
        BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """Log to briefing log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        log_file = LOGS_DIR / "ceo_briefing.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"[CEO BRIEFING] {message}")

    def read_completed_tasks(self, days: int = 7) -> List[Dict]:
        """Read completed tasks from Done folder"""
        tasks = []
        cutoff_date = datetime.now() - timedelta(days=days)

        if not DONE_DIR.exists():
            self.log("Done directory not found")
            return tasks

        for file in DONE_DIR.glob("*.json"):
            try:
                # Check file modification time
                mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                if mod_time < cutoff_date:
                    continue

                with open(file, "r", encoding="utf-8") as f:
                    task_data = json.load(f)
                    tasks.append(task_data)

            except Exception as e:
                self.log(f"Error reading task {file.name}: {e}")

        self.log(f"Found {len(tasks)} completed tasks in last {days} days")
        return tasks

    def read_accounting_data(self) -> Dict[str, Any]:
        """Read accounting data from Current_Month.md"""
        accounting = {
            "revenue": "N/A",
            "expenses": "N/A",
            "profit": "N/A",
            "transactions": []
        }

        if not ACCOUNTING_FILE.exists():
            self.log("Accounting file not found")
            return accounting

        try:
            with open(ACCOUNTING_FILE, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse markdown for key metrics
            # This is a simple parser - adjust based on actual format
            lines = content.split("\n")
            for line in lines:
                if "Revenue" in line or "revenue" in line:
                    # Extract number from line
                    parts = line.split(":")
                    if len(parts) > 1:
                        accounting["revenue"] = parts[1].strip()

                if "Expenses" in line or "expenses" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        accounting["expenses"] = parts[1].strip()

                if "Profit" in line or "profit" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        accounting["profit"] = parts[1].strip()

            self.log("Accounting data loaded")

        except Exception as e:
            self.log(f"Error reading accounting data: {e}")

        return accounting

    def read_system_health(self) -> Dict[str, Any]:
        """Read system health from system_health.md"""
        health = {
            "status": "Unknown",
            "errors": 0,
            "pending_approvals": 0,
            "workflows": {},
            "alerts": []
        }

        if not HEALTH_FILE.exists():
            self.log("Health file not found")
            return health

        try:
            with open(HEALTH_FILE, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse health report
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "Errors (Last Hour)" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        try:
                            health["errors"] = int(parts[1].strip().split()[0])
                        except:
                            pass

                if "Total Pending Actions" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        try:
                            health["pending_approvals"] = int(parts[1].strip().split()[0])
                        except:
                            pass

                if "Alerts" in line and i + 1 < len(lines):
                    # Collect alerts
                    j = i + 1
                    while j < len(lines) and lines[j].strip().startswith("-"):
                        health["alerts"].append(lines[j].strip("- ").strip())
                        j += 1

            # Determine overall status
            if health["errors"] == 0 and not health["alerts"]:
                health["status"] = "Healthy"
            elif health["errors"] < 5:
                health["status"] = "Good"
            else:
                health["status"] = "Needs Attention"

            self.log("System health data loaded")

        except Exception as e:
            self.log(f"Error reading system health: {e}")

        return health

    def analyze_tasks(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Analyze completed tasks for metrics"""
        analysis = {
            "total_tasks": len(tasks),
            "emails_handled": 0,
            "social_posts": 0,
            "approvals_processed": 0,
            "task_types": {}
        }

        for task in tasks:
            task_type = task.get("type", "unknown")

            # Count by type
            if task_type not in analysis["task_types"]:
                analysis["task_types"][task_type] = 0
            analysis["task_types"][task_type] += 1

            # Specific metrics
            if "email" in task_type.lower():
                analysis["emails_handled"] += 1

            if "social" in task_type.lower():
                analysis["social_posts"] += 1

            if "approval" in task.get("status", "").lower():
                analysis["approvals_processed"] += 1

        return analysis

    def generate_briefing_with_claude(self, data: Dict[str, Any]) -> str:
        """Use Claude to generate executive summary"""
        self.log("Generating briefing with Claude...")

        prompt = f"""You are an executive assistant preparing a weekly CEO briefing.

Generate a professional, concise executive summary based on the following data:

## Completed Tasks (Last 7 Days)
- Total tasks completed: {data['task_analysis']['total_tasks']}
- Emails handled: {data['task_analysis']['emails_handled']}
- Social media posts: {data['task_analysis']['social_posts']}
- Approvals processed: {data['task_analysis']['approvals_processed']}
- Task breakdown: {json.dumps(data['task_analysis']['task_types'], indent=2)}

## Financial Summary
- Revenue: {data['accounting']['revenue']}
- Expenses: {data['accounting']['expenses']}
- Profit: {data['accounting']['profit']}

## System Health
- Overall status: {data['health']['status']}
- Errors (last hour): {data['health']['errors']}
- Pending approvals: {data['health']['pending_approvals']}
- Alerts: {', '.join(data['health']['alerts']) if data['health']['alerts'] else 'None'}

## Week Period
{data['week_start']} to {data['week_end']}

Please generate a professional CEO briefing with these sections:
1. Executive Summary (2-3 sentences)
2. Key Metrics
3. Operational Highlights
4. Financial Summary
5. System Health
6. Action Items (if any)
7. Outlook

Use professional business language. Be concise but informative. Highlight both achievements and areas needing attention.
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            briefing_content = response.content[0].text
            self.log("Briefing generated successfully")
            return briefing_content

        except Exception as e:
            self.log(f"Error generating briefing: {e}")
            return self.generate_fallback_briefing(data)

    def generate_fallback_briefing(self, data: Dict[str, Any]) -> str:
        """Generate basic briefing without Claude"""
        self.log("Generating fallback briefing")

        briefing = f"""# Weekly CEO Briefing

**Period:** {data['week_start']} to {data['week_end']}

## Executive Summary

This week, the Platinum Tier AI Employee completed {data['task_analysis']['total_tasks']} tasks, handled {data['task_analysis']['emails_handled']} emails, and published {data['task_analysis']['social_posts']} social media posts. System health is {data['health']['status']}.

## Key Metrics

| Metric | Value |
|--------|-------|
| Tasks Completed | {data['task_analysis']['total_tasks']} |
| Emails Handled | {data['task_analysis']['emails_handled']} |
| Social Posts | {data['task_analysis']['social_posts']} |
| Approvals Processed | {data['task_analysis']['approvals_processed']} |
| Pending Approvals | {data['health']['pending_approvals']} |

## Financial Summary

- **Revenue:** {data['accounting']['revenue']}
- **Expenses:** {data['accounting']['expenses']}
- **Profit:** {data['accounting']['profit']}

## System Health

- **Status:** {data['health']['status']}
- **Errors (Last Hour):** {data['health']['errors']}
- **Pending Approvals:** {data['health']['pending_approvals']}

### Alerts
{chr(10).join(['- ' + alert for alert in data['health']['alerts']]) if data['health']['alerts'] else '- No alerts'}

## Task Breakdown

{chr(10).join([f'- {task_type}: {count}' for task_type, count in data['task_analysis']['task_types'].items()])}

## Action Items

{'- Review pending approvals (' + str(data['health']['pending_approvals']) + ' items)' if data['health']['pending_approvals'] > 0 else '- No immediate action items'}
{chr(10).join(['- Address: ' + alert for alert in data['health']['alerts'][:3]])}

---

*Generated by Platinum Tier AI Employee - CEO Briefing System*
"""

        return briefing

    def save_briefing(self, content: str, date: datetime) -> Path:
        """Save briefing to file"""
        filename = date.strftime("%Y-%m-%d") + "_CEO_Briefing.md"
        filepath = BRIEFINGS_DIR / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        self.log(f"Briefing saved to {filepath}")
        return filepath

    def generate(self) -> Path:
        """Generate complete CEO briefing"""
        self.log("Starting CEO briefing generation")

        # Collect data
        week_end = datetime.now()
        week_start = week_end - timedelta(days=7)

        tasks = self.read_completed_tasks(days=7)
        accounting = self.read_accounting_data()
        health = self.read_system_health()
        task_analysis = self.analyze_tasks(tasks)

        # Prepare data for Claude
        data = {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "task_analysis": task_analysis,
            "accounting": accounting,
            "health": health
        }

        # Generate briefing
        briefing_content = self.generate_briefing_with_claude(data)

        # Save briefing
        filepath = self.save_briefing(briefing_content, week_end)

        self.log("CEO briefing generation completed")
        return filepath


def main():
    """Main entry point"""
    try:
        generator = PlatinumCEOBriefing()
        filepath = generator.generate()
        print(f"\n[SUCCESS] CEO briefing generated: {filepath}\n")
        return 0

    except Exception as e:
        print(f"\n[ERROR] Failed to generate CEO briefing: {e}\n")
        return 1


if __name__ == "__main__":
    exit(main())
