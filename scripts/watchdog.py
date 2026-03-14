#!/usr/bin/env python3
"""
Watchdog - System Health Monitor
Monitors agents, watchers, and system health
Auto-restarts stopped processes
"""

import os
import sys
import time
import psutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
LOGS_DIR = VAULT_DIR / "Logs"
HEALTH_FILE = LOGS_DIR / "system_health.md"
WATCHDOG_LOG = LOGS_DIR / "watchdog.log"
CHECK_INTERVAL = 300  # 5 minutes

# Processes to monitor (local processes only)
MONITORED_PROCESSES = {
    "watch_gmail": {
        "script": "scripts/watch_gmail.py",
        "auto_restart": True,
        "critical": False
    },
    "watch_inbox": {
        "script": "scripts/watch_inbox.py",
        "auto_restart": True,
        "critical": False
    }
}


class Watchdog:
    """System health monitor and process watchdog"""

    def __init__(self):
        self.logs_dir = LOGS_DIR
        self.health_file = HEALTH_FILE
        self.watchdog_log = WATCHDOG_LOG

        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Track process PIDs
        self.process_pids: Dict[str, Optional[int]] = {}

    def log(self, message: str, level: str = "INFO"):
        """Log to watchdog log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        with open(self.watchdog_log, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"[WATCHDOG] {message}")

    def is_process_running(self, script_name: str) -> Optional[int]:
        """Check if a Python script is running, return PID if found"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if cmdline and any(script_name in arg for arg in cmdline):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def start_process(self, process_name: str, script_path: str) -> bool:
        """Start a process"""
        try:
            self.log(f"Starting {process_name}...")

            # Start process in background
            if sys.platform == "win32":
                # Windows: use CREATE_NEW_CONSOLE to run in background
                subprocess.Popen(
                    ["python", script_path],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Unix: use nohup
                subprocess.Popen(
                    ["nohup", "python", script_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setpgrp
                )

            time.sleep(2)  # Wait for process to start

            # Verify it started
            pid = self.is_process_running(script_path)
            if pid:
                self.log(f"Started {process_name} (PID: {pid})", "SUCCESS")
                self.process_pids[process_name] = pid
                return True
            else:
                self.log(f"Failed to start {process_name}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Error starting {process_name}: {e}", "ERROR")
            return False

    def check_processes(self) -> Dict[str, str]:
        """Check status of all monitored processes"""
        status = {}

        for process_name, config in MONITORED_PROCESSES.items():
            script_path = config["script"]
            pid = self.is_process_running(script_path)

            if pid:
                status[process_name] = "RUNNING"
                self.process_pids[process_name] = pid
            else:
                status[process_name] = "STOPPED"
                self.process_pids[process_name] = None

                # Auto-restart if configured
                if config.get("auto_restart", False):
                    self.log(f"{process_name} is stopped, attempting restart...", "WARNING")
                    self.start_process(process_name, script_path)

        return status

    def check_github_actions(self) -> Dict[str, str]:
        """Check GitHub Actions workflow status"""
        workflows = {
            "cloud_agent": "unknown",
            "health_monitor": "unknown",
            "vault_sync": "unknown",
            "ceo_briefing": "unknown"
        }

        try:
            # Try to get workflow status via gh CLI
            result = subprocess.run(
                ["gh", "run", "list", "--limit", "4", "--json", "name,status,conclusion"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                runs = json.loads(result.stdout)
                for run in runs:
                    name = run.get("name", "").lower()
                    status = run.get("status", "unknown")
                    conclusion = run.get("conclusion", "")

                    if "cloud agent" in name:
                        workflows["cloud_agent"] = conclusion if conclusion else status
                    elif "health monitor" in name:
                        workflows["health_monitor"] = conclusion if conclusion else status
                    elif "vault sync" in name:
                        workflows["vault_sync"] = conclusion if conclusion else status
                    elif "ceo briefing" in name:
                        workflows["ceo_briefing"] = conclusion if conclusion else status

        except Exception as e:
            self.log(f"Could not check GitHub Actions: {e}", "WARNING")

        return workflows

    def get_vault_metrics(self) -> Dict[str, int]:
        """Get vault folder metrics"""
        metrics = {
            "pending_approval_email": 0,
            "pending_approval_social": 0,
            "needs_action_email": 0,
            "needs_action_social": 0,
            "in_progress_cloud": 0,
            "in_progress_local": 0,
            "done_today": 0
        }

        try:
            # Count pending approvals
            pending_email = VAULT_DIR / "Pending_Approval" / "email"
            if pending_email.exists():
                metrics["pending_approval_email"] = len(list(pending_email.glob("*.json")))

            pending_social = VAULT_DIR / "Pending_Approval" / "social"
            if pending_social.exists():
                metrics["pending_approval_social"] = len(list(pending_social.glob("*.json")))

            # Count needs action
            needs_email = VAULT_DIR / "Needs_Action" / "email"
            if needs_email.exists():
                metrics["needs_action_email"] = len(list(needs_email.glob("*.json")))

            needs_social = VAULT_DIR / "Needs_Action" / "social"
            if needs_social.exists():
                metrics["needs_action_social"] = len(list(needs_social.glob("*.json")))

            # Count in progress
            in_progress_cloud = VAULT_DIR / "In_Progress" / "cloud"
            if in_progress_cloud.exists():
                metrics["in_progress_cloud"] = len(list(in_progress_cloud.glob("*.json")))

            in_progress_local = VAULT_DIR / "In_Progress" / "local"
            if in_progress_local.exists():
                metrics["in_progress_local"] = len(list(in_progress_local.glob("*.json")))

            # Count done today
            done_dir = VAULT_DIR / "Done"
            if done_dir.exists():
                today = datetime.now().date()
                for file in done_dir.glob("*.json"):
                    if file.stat().st_mtime >= datetime.combine(today, datetime.min.time()).timestamp():
                        metrics["done_today"] += 1

        except Exception as e:
            self.log(f"Error getting vault metrics: {e}", "ERROR")

        return metrics

    def count_recent_errors(self) -> int:
        """Count errors in logs from last hour"""
        error_count = 0
        one_hour_ago = datetime.now() - timedelta(hours=1)

        try:
            log_files = [
                LOGS_DIR / "cloud_agent.log",
                LOGS_DIR / "local_agent.log",
                LOGS_DIR / "watchdog.log"
            ]

            for log_file in log_files:
                if not log_file.exists():
                    continue

                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "[ERROR]" in line:
                            try:
                                # Extract timestamp
                                timestamp_str = line.split("]")[0].strip("[")
                                log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                                if log_time >= one_hour_ago:
                                    error_count += 1
                            except:
                                continue

        except Exception as e:
            self.log(f"Error counting errors: {e}", "WARNING")

        return error_count

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

    def write_health_report(self, process_status: Dict[str, str],
                           workflow_status: Dict[str, str],
                           metrics: Dict[str, int],
                           error_count: int,
                           last_sync: str):
        """Write comprehensive health report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# System Health Report

**Last Updated:** {timestamp}

---

## 🖥️ Local Processes

| Process | Status | Auto-Restart |
|---------|--------|--------------|
"""

        for process_name, status in process_status.items():
            config = MONITORED_PROCESSES.get(process_name, {})
            auto_restart = "✓" if config.get("auto_restart") else "✗"
            status_icon = "🟢" if status == "RUNNING" else "🔴"

            report += f"| {process_name} | {status_icon} {status} | {auto_restart} |\n"

        report += f"""
---

## ☁️ GitHub Actions Workflows

| Workflow | Status |
|----------|--------|
"""

        for workflow_name, status in workflow_status.items():
            if status == "success":
                status_icon = "🟢"
            elif status == "failure":
                status_icon = "🔴"
            elif status in ["in_progress", "queued"]:
                status_icon = "🟡"
            else:
                status_icon = "⚪"

            report += f"| {workflow_name} | {status_icon} {status} |\n"

        report += f"""
---

## 📊 Vault Metrics

| Metric | Count |
|--------|-------|
| Pending Approval (Email) | {metrics['pending_approval_email']} |
| Pending Approval (Social) | {metrics['pending_approval_social']} |
| Needs Action (Email) | {metrics['needs_action_email']} |
| Needs Action (Social) | {metrics['needs_action_social']} |
| In Progress (Cloud) | {metrics['in_progress_cloud']} |
| In Progress (Local) | {metrics['in_progress_local']} |
| Completed Today | {metrics['done_today']} |

---

## 🔄 System Status

- **Last Vault Sync:** {last_sync}
- **Errors (Last Hour):** {error_count}
- **Total Pending Actions:** {metrics['pending_approval_email'] + metrics['pending_approval_social']}
- **Total In Progress:** {metrics['in_progress_cloud'] + metrics['in_progress_local']}

---

## 🚨 Alerts

"""

        # Generate alerts
        alerts = []

        if error_count > 10:
            alerts.append("⚠️ **HIGH ERROR RATE**: More than 10 errors in the last hour")

        if metrics['pending_approval_email'] + metrics['pending_approval_social'] > 20:
            alerts.append("⚠️ **HIGH PENDING APPROVALS**: More than 20 items awaiting approval")

        if metrics['in_progress_cloud'] + metrics['in_progress_local'] > 10:
            alerts.append("⚠️ **STUCK TASKS**: More than 10 tasks in progress (possible stuck tasks)")

        if any(status == "STOPPED" for status in process_status.values()):
            stopped = [name for name, status in process_status.items() if status == "STOPPED"]
            alerts.append(f"🔴 **PROCESSES STOPPED**: {', '.join(stopped)}")

        if any(status == "failure" for status in workflow_status.values()):
            failed = [name for name, status in workflow_status.items() if status == "failure"]
            alerts.append(f"🔴 **WORKFLOWS FAILED**: {', '.join(failed)}")

        if alerts:
            for alert in alerts:
                report += f"- {alert}\n"
        else:
            report += "✅ No alerts - System healthy\n"

        report += f"""
---

*Generated by Watchdog - System Health Monitor*
*Next check in 5 minutes*
"""

        # Write report
        with open(self.health_file, "w", encoding="utf-8") as f:
            f.write(report)

        self.log("Health report updated")

    def run_check(self):
        """Run one health check cycle"""
        self.log("Starting health check cycle")

        # Check local processes
        process_status = self.check_processes()

        # Check GitHub Actions
        workflow_status = self.check_github_actions()

        # Get vault metrics
        metrics = self.get_vault_metrics()

        # Count recent errors
        error_count = self.count_recent_errors()

        # Get last sync time
        last_sync = self.get_last_sync_time()

        # Write health report
        self.write_health_report(
            process_status,
            workflow_status,
            metrics,
            error_count,
            last_sync
        )

        self.log("Health check cycle completed")

    def run_forever(self):
        """Run watchdog continuously"""
        self.log("Watchdog started - monitoring system health")

        try:
            while True:
                self.run_check()
                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            self.log("Watchdog stopped by user", "WARNING")

        except Exception as e:
            self.log(f"Watchdog error: {e}", "ERROR")
            raise


def main():
    """Main entry point"""
    watchdog = Watchdog()

    if "--once" in sys.argv:
        # Run once and exit
        watchdog.run_check()
    else:
        # Run continuously
        watchdog.run_forever()


if __name__ == "__main__":
    main()
