"""
Task Planner Agent - Silver Tier AI Employee

This script automatically processes markdown files from the Inbox,
analyzes their content, and generates actionable step-by-step plans.

Features:
- Processes only .md files from Inbox
- Generates structured plans with clear steps
- Idempotent operation (tracks processed files)
- Integrates with vault file management system
- Comprehensive logging
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

# Rich library for beautiful terminal output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Configuration
INBOX_FOLDER = os.path.join("AI_Employee_Vault", "Inbox")
NEEDS_ACTION_FOLDER = os.path.join("AI_Employee_Vault", "Needs_Action")
DONE_FOLDER = os.path.join("AI_Employee_Vault", "Done")
LOGS_FOLDER = "logs"
ACTIONS_LOG = os.path.join(LOGS_FOLDER, "actions.log")
PROCESSED_REGISTRY = os.path.join(LOGS_FOLDER, "processed.json")


def ensure_directories():
    """Create required directories if they don't exist."""
    for folder in [INBOX_FOLDER, NEEDS_ACTION_FOLDER, DONE_FOLDER, LOGS_FOLDER]:
        os.makedirs(folder, exist_ok=True)


def log_action(message):
    """
    Log an action to the actions.log file with timestamp.

    Args:
        message (str): The message to log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    try:
        with open(ACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)

        # Colorful console output with rich
        if RICH_AVAILABLE:
            if "ERROR" in message or "Failed" in message:
                console.print(f"[bold red][X][/bold red] [red]{message}[/red]")
            elif "SUCCESS" in message or "created" in message.lower() or "completed" in message.lower():
                console.print(f"[bold green][OK][/bold green] [green]{message}[/green]")
            elif "WARNING" in message or "Skipping" in message:
                console.print(f"[bold yellow][WARNING][/bold yellow] [yellow]{message}[/yellow]")
            else:
                console.print(f"[bold cyan][INFO][/bold cyan] [cyan]{message}[/cyan]")
        else:
            print(f"[LOG] {message}")
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red][X] Failed to write to log: {e}[/bold red]")
        else:
            print(f"[ERROR] Failed to write to log: {e}")


def load_processed_registry():
    """
    Load the registry of processed files.
    Handles legacy format and migrates to new format if needed.

    Returns:
        dict: Registry data with processed_files list
    """
    if os.path.exists(PROCESSED_REGISTRY):
        try:
            with open(PROCESSED_REGISTRY, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle legacy format: {"processed": ["file1.md", "file2.md"]}
            if "processed" in data and "processed_files" not in data:
                # Migrate to new format
                migrated = {"processed_files": []}
                for filename in data.get("processed", []):
                    migrated["processed_files"].append({
                        "filename": filename,
                        "processed_at": "unknown (migrated)",
                        "plan_created": f"Plan_{filename}"
                    })
                log_action(f"Migrated {len(migrated['processed_files'])} entries from legacy format")
                save_processed_registry(migrated)
                return migrated

            # Ensure processed_files key exists
            if "processed_files" not in data:
                data["processed_files"] = []

            return data
        except Exception as e:
            log_action(f"Error loading processed registry: {e}")
            return {"processed_files": []}
    return {"processed_files": []}


def save_processed_registry(registry):
    """
    Save the registry of processed files.

    Args:
        registry (dict): Registry data to save
    """
    try:
        with open(PROCESSED_REGISTRY, "w", encoding="utf-8") as f:
            json.dump(registry, indent=2, fp=f)
    except Exception as e:
        log_action(f"Error saving processed registry: {e}")


def is_file_processed(filename, registry):
    """
    Check if a file has already been processed.

    Args:
        filename (str): Name of the file to check
        registry (dict): Processed files registry

    Returns:
        bool: True if file was already processed
    """
    return any(entry["filename"] == filename for entry in registry["processed_files"])


def mark_file_processed(filename, plan_filename, registry):
    """
    Mark a file as processed in the registry.

    Args:
        filename (str): Original filename
        plan_filename (str): Generated plan filename
        registry (dict): Registry to update
    """
    registry["processed_files"].append({
        "filename": filename,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "plan_created": plan_filename
    })
    save_processed_registry(registry)


def extract_priority(content):
    """
    Extract priority from content using keywords.

    Args:
        content (str): File content

    Returns:
        str: Priority level (high, medium, low)
    """
    content_lower = content.lower()

    # Check for explicit priority markers
    if re.search(r'priority:\s*high', content_lower):
        return "high"
    if re.search(r'priority:\s*low', content_lower):
        return "low"

    # Check for urgency keywords
    urgent_keywords = ['urgent', 'asap', 'critical', 'emergency', 'immediately']
    if any(keyword in content_lower for keyword in urgent_keywords):
        return "high"

    # Check for low priority keywords
    low_keywords = ['whenever', 'eventually', 'nice to have', 'optional']
    if any(keyword in content_lower for keyword in low_keywords):
        return "low"

    return "medium"


def extract_task_type(content):
    """
    Determine task type from content.

    Args:
        content (str): File content

    Returns:
        str: Task type
    """
    content_lower = content.lower()

    if 'bug' in content_lower or 'fix' in content_lower or 'error' in content_lower:
        return "bug_fix"
    elif 'feature' in content_lower or 'implement' in content_lower or 'add' in content_lower:
        return "feature_development"
    elif 'review' in content_lower or 'analyze' in content_lower:
        return "review"
    elif 'research' in content_lower or 'investigate' in content_lower:
        return "research"
    elif 'refactor' in content_lower or 'improve' in content_lower:
        return "refactoring"
    elif 'test' in content_lower:
        return "testing"
    elif 'document' in content_lower or 'doc' in content_lower:
        return "documentation"
    else:
        return "general_task"


def estimate_effort(content):
    """
    Estimate effort level based on content complexity.

    Args:
        content (str): File content

    Returns:
        str: Effort level (Low, Medium, High)
    """
    # Simple heuristic based on content length and complexity indicators
    word_count = len(content.split())

    complexity_keywords = ['complex', 'multiple', 'integrate', 'system', 'architecture']
    complexity_score = sum(1 for keyword in complexity_keywords if keyword in content.lower())

    if word_count < 50 and complexity_score == 0:
        return "Low"
    elif word_count > 200 or complexity_score >= 2:
        return "High"
    else:
        return "Medium"


def generate_steps(content, task_type):
    """
    Generate step-by-step plan based on content and task type.

    Args:
        content (str): File content
        task_type (str): Type of task

    Returns:
        list: List of step dictionaries
    """
    steps = []

    # Generic steps based on task type
    if task_type == "bug_fix":
        steps = [
            {"title": "Reproduce the Issue", "subtasks": ["Identify steps to reproduce", "Verify the bug exists", "Document expected vs actual behavior"]},
            {"title": "Investigate Root Cause", "subtasks": ["Review relevant code sections", "Check logs and error messages", "Identify the source of the problem"]},
            {"title": "Implement Fix", "subtasks": ["Write code to resolve the issue", "Ensure fix doesn't break existing functionality", "Add error handling if needed"]},
            {"title": "Test the Fix", "subtasks": ["Verify bug is resolved", "Run regression tests", "Test edge cases"]},
            {"title": "Document Changes", "subtasks": ["Update code comments", "Add to changelog if applicable", "Document any new behavior"]}
        ]
    elif task_type == "feature_development":
        steps = [
            {"title": "Define Requirements", "subtasks": ["Clarify feature specifications", "Identify user stories", "List acceptance criteria"]},
            {"title": "Design Solution", "subtasks": ["Plan architecture/approach", "Identify affected components", "Consider edge cases and constraints"]},
            {"title": "Implement Feature", "subtasks": ["Write core functionality", "Add necessary UI/UX elements", "Integrate with existing systems"]},
            {"title": "Test Implementation", "subtasks": ["Write unit tests", "Perform integration testing", "Validate against requirements"]},
            {"title": "Review and Refine", "subtasks": ["Code review", "Performance optimization", "Documentation updates"]}
        ]
    elif task_type == "review":
        steps = [
            {"title": "Initial Assessment", "subtasks": ["Read through all materials", "Identify key areas to focus on", "Note initial observations"]},
            {"title": "Detailed Analysis", "subtasks": ["Examine code/content quality", "Check for issues or improvements", "Verify best practices are followed"]},
            {"title": "Document Findings", "subtasks": ["List strengths and weaknesses", "Provide specific recommendations", "Prioritize action items"]},
            {"title": "Create Action Plan", "subtasks": ["Outline next steps", "Assign priorities", "Set timeline if applicable"]}
        ]
    elif task_type == "research":
        steps = [
            {"title": "Define Research Scope", "subtasks": ["Clarify research questions", "Identify information sources", "Set boundaries and constraints"]},
            {"title": "Gather Information", "subtasks": ["Review documentation", "Analyze existing solutions", "Collect relevant data"]},
            {"title": "Analyze Findings", "subtasks": ["Compare options/approaches", "Identify pros and cons", "Evaluate feasibility"]},
            {"title": "Document Results", "subtasks": ["Summarize key findings", "Provide recommendations", "Include references and sources"]}
        ]
    else:
        # Generic task steps
        steps = [
            {"title": "Understand Requirements", "subtasks": ["Review task description", "Clarify any ambiguities", "Identify dependencies"]},
            {"title": "Plan Approach", "subtasks": ["Break down into subtasks", "Identify resources needed", "Estimate timeline"]},
            {"title": "Execute Task", "subtasks": ["Complete primary objectives", "Handle edge cases", "Ensure quality standards"]},
            {"title": "Verify Completion", "subtasks": ["Review work against requirements", "Test functionality", "Get feedback if needed"]}
        ]

    return steps


def identify_risks(content, task_type):
    """
    Identify potential risks or blockers.

    Args:
        content (str): File content
        task_type (str): Type of task

    Returns:
        list: List of risk dictionaries
    """
    risks = []
    content_lower = content.lower()

    # Check for dependency mentions
    if 'depend' in content_lower or 'require' in content_lower:
        risks.append({
            "risk": "Dependencies",
            "description": "Task may depend on other systems or tasks",
            "mitigation": "Identify and verify all dependencies before starting"
        })

    # Check for complexity indicators
    if 'complex' in content_lower or 'difficult' in content_lower:
        risks.append({
            "risk": "Complexity",
            "description": "Task appears to be complex and may take longer than expected",
            "mitigation": "Break down into smaller subtasks and tackle incrementally"
        })

    # Check for integration mentions
    if 'integrat' in content_lower or 'connect' in content_lower:
        risks.append({
            "risk": "Integration Challenges",
            "description": "May require integration with external systems",
            "mitigation": "Test integrations thoroughly and have rollback plan"
        })

    # Check for unclear requirements
    if len(content.split()) < 30:
        risks.append({
            "risk": "Unclear Requirements",
            "description": "Task description is brief and may lack detail",
            "mitigation": "Clarify requirements before proceeding with implementation"
        })

    # Add generic risk if none identified
    if not risks:
        risks.append({
            "risk": "Scope Creep",
            "description": "Task scope may expand during implementation",
            "mitigation": "Stay focused on core requirements and document any scope changes"
        })

    return risks


def generate_plan(filename, content):
    """
    Generate a comprehensive plan from file content.

    Args:
        filename (str): Original filename
        content (str): File content

    Returns:
        str: Generated plan in markdown format
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract metadata
    priority = extract_priority(content)
    task_type = extract_task_type(content)
    effort = estimate_effort(content)

    # Generate plan components
    steps = generate_steps(content, task_type)
    risks = identify_risks(content, task_type)

    # Extract title from content (first line or filename)
    lines = content.strip().split('\n')
    title = lines[0].strip('#').strip() if lines else filename.replace('.md', '').replace('_', ' ').title()

    # Build plan content
    plan = f"""---
type: action_plan
status: pending
priority: {priority}
task_type: {task_type}
created_at: {timestamp}
source_file: AI_Employee_Vault/Inbox/{filename}
related_files: []
---

# Plan: {title}

## Executive Summary
This plan outlines the approach for completing the task described in `{filename}`. The task has been classified as **{task_type}** with **{priority}** priority and an estimated effort level of **{effort}**.

## Original Request
```
{content[:500]}{'...' if len(content) > 500 else ''}
```

## Step-by-Step Plan

"""

    # Add steps
    for i, step in enumerate(steps, 1):
        plan += f"{i}. **{step['title']}**\n"
        for subtask in step['subtasks']:
            plan += f"   - {subtask}\n"
        plan += "\n"

    # Add success criteria
    plan += "## Success Criteria\n\n"
    plan += "- [ ] All steps completed successfully\n"
    plan += "- [ ] Requirements met and verified\n"
    plan += "- [ ] No critical issues or blockers remaining\n"
    plan += "- [ ] Documentation updated if applicable\n"
    plan += "- [ ] Task reviewed and approved\n\n"

    # Add risks
    plan += "## Potential Risks/Blockers\n\n"
    for risk in risks:
        plan += f"- **{risk['risk']}**: {risk['description']}\n"
        plan += f"  - *Mitigation*: {risk['mitigation']}\n"
    plan += "\n"

    # Add effort estimate
    plan += f"## Effort Estimate\n{effort}\n\n"

    # Add notes section
    plan += "## Notes\n"
    plan += "- This plan was automatically generated by the Task Planner Agent\n"
    plan += "- Review and adjust steps as needed based on actual requirements\n"
    plan += "- Update status and priority if circumstances change\n"
    plan += f"- Source file: `AI_Employee_Vault/Inbox/{filename}`\n"

    return plan


def process_file(filename):
    """
    Process a single markdown file from Inbox.

    Args:
        filename (str): Name of the file to process

    Returns:
        bool: True if processed successfully
    """
    try:
        # Read file content
        filepath = os.path.join(INBOX_FOLDER, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Generate plan
        plan_content = generate_plan(filename, content)

        # Create plan filename
        base_name = filename.replace('.md', '')
        plan_filename = f"Plan_{base_name}.md"
        plan_filepath = os.path.join(NEEDS_ACTION_FOLDER, plan_filename)

        # Save plan
        with open(plan_filepath, "w", encoding="utf-8") as f:
            f.write(plan_content)

        log_action(f"Created plan for '{filename}' -> '{plan_filename}'")
        return True

    except Exception as e:
        log_action(f"Error processing '{filename}': {str(e)}")
        return False


def main():
    """
    Main function to run the task planner.
    """
    # Beautiful startup banner
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            "[bold cyan][AI] TASK PLANNER AGENT[/bold cyan]\n"
            "[dim]Silver Tier AI Employee[/dim]\n"
            "[yellow]========================================[/yellow]",
            border_style="cyan",
            padding=(1, 2)
        ))
        console.print()
    else:
        print("=" * 60)
        print("  TASK PLANNER AGENT - Silver Tier AI Employee")
        print("=" * 60)
        print()

    # Ensure directories exist
    ensure_directories()
    log_action("Task Planner started")

    # Load processed files registry
    registry = load_processed_registry()

    # Get all .md files from Inbox
    if not os.path.exists(INBOX_FOLDER):
        log_action("Inbox folder does not exist")
        if RICH_AVAILABLE:
            console.print("[yellow][WARNING] Inbox folder not found. Nothing to process.[/yellow]")
        else:
            print("[INFO] Inbox folder not found. Nothing to process.")
        return

    md_files = [f for f in os.listdir(INBOX_FOLDER)
                if f.endswith('.md') and os.path.isfile(os.path.join(INBOX_FOLDER, f))]

    if not md_files:
        log_action("No .md files found in Inbox")
        if RICH_AVAILABLE:
            console.print("[yellow][INFO] No markdown files found in Inbox.[/yellow]")
        else:
            print("[INFO] No markdown files found in Inbox.")
        return

    if RICH_AVAILABLE:
        console.print(f"[bold green][FILES] Found {len(md_files)} markdown file(s) in Inbox[/bold green]")
        console.print()
    else:
        print(f"[INFO] Found {len(md_files)} markdown file(s) in Inbox")
        print()

    # Process each file
    processed_count = 0
    skipped_count = 0

    for filename in md_files:
        if is_file_processed(filename, registry):
            if RICH_AVAILABLE:
                console.print(f"[dim yellow][SKIP] Skipping {filename} (already processed)[/dim yellow]")
            else:
                print(f"[SKIP] {filename} (already processed)")
            skipped_count += 1
            continue

        if RICH_AVAILABLE:
            console.print(f"[bold blue][PROCESSING] Processing {filename}...[/bold blue]")
        else:
            print(f"[PROCESSING] {filename}...")

        if process_file(filename):
            base_name = filename.replace('.md', '')
            plan_filename = f"Plan_{base_name}.md"
            mark_file_processed(filename, plan_filename, registry)
            processed_count += 1
            if RICH_AVAILABLE:
                console.print(f"[bold green][OK] Plan created: {plan_filename}[/bold green]")
            else:
                print(f"[SUCCESS] Plan created: {plan_filename}")
        else:
            if RICH_AVAILABLE:
                console.print(f"[bold red][X] Could not process {filename}[/bold red]")
            else:
                print(f"[FAILED] Could not process {filename}")

        if RICH_AVAILABLE:
            console.print()
        else:
            print()

    # Summary with beautiful table
    if RICH_AVAILABLE:
        console.print()
        table = Table(title="[SUMMARY] Processing Summary", border_style="cyan", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", justify="left")
        table.add_column("Count", style="green", justify="center")

        table.add_row("[OK] Processed", f"[bold green]{processed_count}[/bold green]")
        table.add_row("[SKIP] Skipped", f"[yellow]{skipped_count}[/yellow]")
        table.add_row("[FILES] Total Files", f"[bold cyan]{len(md_files)}[/bold cyan]")

        console.print(table)
        console.print()

        if processed_count > 0:
            console.print(Panel(
                f"[bold green][OK] Successfully processed {processed_count} file(s)![/bold green]",
                border_style="green"
            ))
        else:
            console.print(Panel(
                "[yellow]No new files to process[/yellow]",
                border_style="yellow"
            ))
        console.print()
    else:
        print("-" * 60)
        print(f"[SUMMARY] Processed: {processed_count} | Skipped: {skipped_count} | Total: {len(md_files)}")
        print("-" * 60)

    log_action(f"Task Planner completed - Processed: {processed_count}, Skipped: {skipped_count}")
    if not RICH_AVAILABLE:
        print()


if __name__ == "__main__":
    main()
