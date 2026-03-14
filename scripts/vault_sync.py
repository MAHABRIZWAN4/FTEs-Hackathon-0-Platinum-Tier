#!/usr/bin/env python3
"""
Vault Sync Script - Local Machine
Synchronizes AI_Employee_Vault with GitHub repository
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
VAULT_DIR = "AI_Employee_Vault"
LOG_FILE = "logs/sync.log"
BRANCH = "main"


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def log_message(message, level="INFO"):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Write to log file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

    # Print to console with colors
    color = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED
    }.get(level, Colors.RESET)

    print(f"{color}{log_entry}{Colors.RESET}")


def run_command(command, capture_output=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            encoding="utf-8"
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_git_repo():
    """Verify we're in a git repository"""
    success, _, _ = run_command("git rev-parse --git-dir")
    if not success:
        log_message("Not a git repository! Run 'git init' first.", "ERROR")
        return False
    return True


def check_vault_exists():
    """Verify vault directory exists"""
    if not os.path.exists(VAULT_DIR):
        log_message(f"Vault directory '{VAULT_DIR}' not found!", "ERROR")
        return False
    return True


def get_git_status():
    """Get current git status"""
    success, output, _ = run_command("git status --porcelain")
    if success:
        return output.strip()
    return ""


def pull_latest_changes():
    """Pull latest changes from remote"""
    log_message("Pulling latest changes from remote...", "INFO")

    # Stash any uncommitted changes first
    success, output, _ = run_command("git status --porcelain")
    has_local_changes = success and output.strip()

    if has_local_changes:
        log_message("Stashing local changes before pull...", "INFO")
        success, _, error = run_command("git stash push -u -m 'Auto-stash before vault sync'")
        if not success:
            log_message(f"Failed to stash changes: {error}", "ERROR")
            return False

    # Fetch first
    success, _, error = run_command("git fetch origin")
    if not success:
        log_message(f"Failed to fetch: {error}", "ERROR")
        # Pop stash if we stashed
        if has_local_changes:
            run_command("git stash pop")
        return False

    # Check if we're behind
    success, output, _ = run_command("git rev-list HEAD..origin/main --count")
    if success and output.strip() != "0":
        log_message(f"Remote has {output.strip()} new commits", "INFO")

    # Pull with rebase to avoid merge commits
    success, output, error = run_command("git pull --rebase origin main")

    if not success:
        if "conflict" in error.lower() or "conflict" in output.lower():
            log_message("Merge conflict detected! Attempting auto-resolution...", "WARNING")
            result = handle_merge_conflict()
            # Pop stash after conflict resolution
            if has_local_changes and result:
                log_message("Restoring stashed changes...", "INFO")
                run_command("git stash pop")
            return result
        else:
            log_message(f"Pull failed: {error}", "ERROR")
            # Pop stash on failure
            if has_local_changes:
                run_command("git stash pop")
            return False

    # Pop stash after successful pull
    if has_local_changes:
        log_message("Restoring stashed changes...", "INFO")
        success, _, error = run_command("git stash pop")
        if not success:
            log_message(f"Warning: Failed to restore stashed changes: {error}", "WARNING")
            log_message("Your changes are still in the stash. Run 'git stash pop' manually.", "WARNING")

    log_message("Successfully pulled latest changes", "SUCCESS")
    return True


def handle_merge_conflict():
    """Handle merge conflicts automatically"""
    log_message("Resolving merge conflicts...", "INFO")

    # Strategy: Accept remote changes for vault files (cloud is source of truth)
    success, output, _ = run_command("git diff --name-only --diff-filter=U")

    if success and output.strip():
        conflicted_files = output.strip().split("\n")
        log_message(f"Conflicted files: {', '.join(conflicted_files)}", "WARNING")

        for file in conflicted_files:
            if file.startswith(VAULT_DIR):
                # Accept remote version for vault files
                log_message(f"Accepting remote version for: {file}", "INFO")
                run_command(f'git checkout --theirs "{file}"')
                run_command(f'git add "{file}"')
            else:
                # Accept local version for non-vault files
                log_message(f"Accepting local version for: {file}", "INFO")
                run_command(f'git checkout --ours "{file}"')
                run_command(f'git add "{file}"')

        # Continue rebase
        success, _, error = run_command("git rebase --continue")
        if success:
            log_message("Merge conflicts resolved successfully", "SUCCESS")
            return True
        else:
            log_message(f"Failed to continue rebase: {error}", "ERROR")
            # Abort rebase if it fails
            run_command("git rebase --abort")
            return False

    return True


def stage_vault_changes():
    """Stage changes in vault directory"""
    log_message(f"Staging changes in {VAULT_DIR}/...", "INFO")

    # Check if there are changes
    success, output, _ = run_command(f"git status --porcelain {VAULT_DIR}/")

    if not success or not output.strip():
        log_message("No changes to stage in vault", "INFO")
        return False

    # Stage vault directory
    success, _, error = run_command(f'git add "{VAULT_DIR}/"')

    if not success:
        log_message(f"Failed to stage changes: {error}", "ERROR")
        return False

    log_message("Changes staged successfully", "SUCCESS")
    return True


def create_commit():
    """Create commit with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Vault sync: {timestamp}\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

    log_message("Creating commit...", "INFO")

    # Create commit
    success, _, error = run_command(f'git commit -m "{commit_message}"')

    if not success:
        if "nothing to commit" in error.lower():
            log_message("No changes to commit", "INFO")
            return False
        else:
            log_message(f"Failed to create commit: {error}", "ERROR")
            return False

    log_message("Commit created successfully", "SUCCESS")
    return True


def push_changes():
    """Push changes to remote"""
    log_message("Pushing changes to remote...", "INFO")

    success, _, error = run_command(f"git push origin {BRANCH}")

    if not success:
        log_message(f"Failed to push: {error}", "ERROR")
        return False

    log_message("Changes pushed successfully", "SUCCESS")
    return True


def verify_no_sensitive_files():
    """Verify no sensitive files are staged"""
    log_message("Verifying no sensitive files are staged...", "INFO")

    success, output, _ = run_command("git diff --cached --name-only")

    if success and output.strip():
        staged_files = output.strip().split("\n")
        sensitive_patterns = [".env", ".token", "token.json", "credentials.json", "_session"]

        for file in staged_files:
            for pattern in sensitive_patterns:
                if pattern in file.lower():
                    log_message(f"WARNING: Sensitive file staged: {file}", "ERROR")
                    log_message("Unstaging sensitive file...", "WARNING")
                    run_command(f'git reset HEAD "{file}"')
                    return False

    log_message("No sensitive files detected", "SUCCESS")
    return True


def main():
    """Main sync function"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}  Vault Sync - Local Machine{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

    log_message("Starting vault sync...", "INFO")

    # Pre-flight checks
    if not check_git_repo():
        return 1

    if not check_vault_exists():
        return 1

    # Step 1: Pull latest changes (with conflict resolution)
    if not pull_latest_changes():
        log_message("Sync failed: Could not pull latest changes", "ERROR")
        return 1

    # Step 2: Stage vault changes
    has_changes = stage_vault_changes()

    if not has_changes:
        log_message("Sync complete: No changes to push", "SUCCESS")
        print(f"\n{Colors.GREEN}[OK] Vault is up to date{Colors.RESET}\n")
        return 0

    # Step 3: Verify no sensitive files
    if not verify_no_sensitive_files():
        log_message("Sync failed: Sensitive files detected", "ERROR")
        return 1

    # Step 4: Create commit
    if not create_commit():
        log_message("Sync complete: No changes to commit", "INFO")
        print(f"\n{Colors.GREEN}[OK] Vault is up to date{Colors.RESET}\n")
        return 0

    # Step 5: Push changes
    if not push_changes():
        log_message("Sync failed: Could not push changes", "ERROR")
        return 1

    log_message("Vault sync completed successfully!", "SUCCESS")
    print(f"\n{Colors.GREEN}{Colors.BOLD}[SUCCESS] Vault synced successfully!{Colors.RESET}\n")

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Sync cancelled by user{Colors.RESET}")
        log_message("Sync cancelled by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        log_message(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)
