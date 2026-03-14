#!/usr/bin/env python3
"""
Dashboard Updater - Single-Writer Rule Enforcer
Only Local Agent updates Dashboard.md
Merges Cloud updates from /Updates/ folder
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
DASHBOARD_FILE = VAULT_DIR / "Dashboard.md"
UPDATES_DIR = VAULT_DIR / "Updates"
LOGS_DIR = VAULT_DIR / "Logs"


class DashboardUpdater:
    """Manages Dashboard.md with single-writer rule"""

    def __init__(self):
        self.updates_dir = UPDATES_DIR
        self.dashboard_file = DASHBOARD_FILE
        self.logs_dir = LOGS_DIR

        # Ensure directories exist
        self.updates_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """Log to dashboard updater log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        log_file = self.logs_dir / "dashboard_updater.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"[DASHBOARD] {message}")

    def collect_updates(self) -> List[Dict]:
        """Collect all updates from Updates folder"""
        update_files = sorted(self.updates_dir.glob("*.json"))
        updates = []

        for update_file in update_files:
            try:
                with open(update_file, "r", encoding="utf-8") as f:
                    update_data = json.load(f)
                    updates.append(update_data)

                # Archive processed update
                archive_dir = self.updates_dir / "processed"
                archive_dir.mkdir(exist_ok=True)
                update_file.rename(archive_dir / update_file.name)

            except Exception as e:
                self.log(f"Error reading update {update_file.name}: {e}")

        return updates

    def generate_dashboard_content(self, updates: List[Dict]) -> str:
        """Generate dashboard markdown content"""
        now = datetime.now()

        # Header
        content = f"""# AI Employee Dashboard

**Last Updated:** {now.strftime("%Y-%m-%d %H:%M:%S")}

---

## 📊 System Status

| Component | Status | Last Activity |
|-----------|--------|---------------|
| Cloud Agent | 🟢 Active | {now.strftime("%H:%M")} |
| Local Agent | 🟢 Active | {now.strftime("%H:%M")} |
| Email Triage | 🟢 Running | Every 15 min |
| Social Posts | 🟢 Running | On demand |
| Vault Sync | 🟢 Running | Every 2 min |

---

## 📥 Pending Actions

"""

        # Count pending items
        pending_email = len(list((VAULT_DIR / "Pending_Approval" / "email").glob("*.json")))
        pending_social = len(list((VAULT_DIR / "Pending_Approval" / "social").glob("*.json")))
        needs_action_email = len(list((VAULT_DIR / "Needs_Action" / "email").glob("*.json")))
        needs_action_social = len(list((VAULT_DIR / "Needs_Action" / "social").glob("*.json")))

        content += f"""
- **Pending Approval (Email):** {pending_email}
- **Pending Approval (Social):** {pending_social}
- **Needs Action (Email):** {needs_action_email}
- **Needs Action (Social):** {needs_action_social}

---

## 🔄 Recent Activity

"""

        # Add recent updates
        if updates:
            for update in updates[-10:]:  # Last 10 updates
                timestamp = update.get("timestamp", "Unknown")
                agent = update.get("agent", "unknown")
                data = update.get("data", {})
                action = data.get("action", "unknown")

                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = timestamp

                content += f"- **{time_str}** [{agent}] {action}\n"
        else:
            content += "- No recent activity\n"

        content += """
---

## 📁 Folder Status

| Folder | Count | Description |
|--------|-------|-------------|
| Inbox | {inbox} | New items to process |
| Needs_Action | {needs_action} | Ready for action |
| Pending_Approval | {pending} | Awaiting approval |
| In_Progress | {in_progress} | Currently being processed |
| Done | {done} | Completed tasks |

---

## 🎯 Quick Actions

- Run local agent: `python scripts/local_agent.py`
- Check logs: `tail -f AI_Employee_Vault/Logs/*.log`
- Manual vault sync: `scripts/vault_push.bat`

---

*Dashboard managed by Local Agent - Single-writer rule enforced*
""".format(
            inbox=len(list((VAULT_DIR / "Inbox").glob("*.json"))) if (VAULT_DIR / "Inbox").exists() else 0,
            needs_action=needs_action_email + needs_action_social,
            pending=pending_email + pending_social,
            in_progress=len(list((VAULT_DIR / "In_Progress" / "cloud").glob("*.json"))) + len(list((VAULT_DIR / "In_Progress" / "local").glob("*.json"))),
            done=len(list((VAULT_DIR / "Done").glob("*.json"))) if (VAULT_DIR / "Done").exists() else 0
        )

        return content

    def update_dashboard(self):
        """Update dashboard with collected updates"""
        self.log("Starting dashboard update")

        # Collect updates from cloud agent
        updates = self.collect_updates()
        self.log(f"Collected {len(updates)} updates")

        # Generate new dashboard content
        content = self.generate_dashboard_content(updates)

        # Write to dashboard (single-writer rule)
        with open(self.dashboard_file, "w", encoding="utf-8") as f:
            f.write(content)

        self.log("Dashboard updated successfully")

    def run(self):
        """Run dashboard updater"""
        try:
            self.update_dashboard()
        except Exception as e:
            self.log(f"Error updating dashboard: {e}")
            raise


def main():
    """Main entry point"""
    updater = DashboardUpdater()
    updater.run()


if __name__ == "__main__":
    main()
