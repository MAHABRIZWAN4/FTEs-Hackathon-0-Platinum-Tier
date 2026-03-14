#!/usr/bin/env python3
"""
Cloud Agent - GitHub Actions Worker
Responsibilities: Email triage, draft social posts, write approval files
NEVER sends/posts directly - draft only
"""

import os
import json
import anthropic
from datetime import datetime
from pathlib import Path
import shutil

# Configuration
VAULT_DIR = Path("AI_Employee_Vault")
NEEDS_ACTION_EMAIL = VAULT_DIR / "Needs_Action" / "email"
NEEDS_ACTION_SOCIAL = VAULT_DIR / "Needs_Action" / "social"
PENDING_APPROVAL_EMAIL = VAULT_DIR / "Pending_Approval" / "email"
PENDING_APPROVAL_SOCIAL = VAULT_DIR / "Pending_Approval" / "social"
IN_PROGRESS_CLOUD = VAULT_DIR / "In_Progress" / "cloud"
UPDATES_DIR = VAULT_DIR / "Updates"
LOGS_DIR = VAULT_DIR / "Logs"


class CloudAgent:
    """Cloud agent that drafts emails and social posts"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.agent_id = "cloud-agent"

        # Ensure directories exist
        for dir_path in [NEEDS_ACTION_EMAIL, NEEDS_ACTION_SOCIAL,
                         PENDING_APPROVAL_EMAIL, PENDING_APPROVAL_SOCIAL,
                         IN_PROGRESS_CLOUD, UPDATES_DIR, LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def log(self, message, level="INFO"):
        """Log message to cloud agent log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        log_file = LOGS_DIR / "cloud_agent.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"[CLOUD] {log_entry.strip()}")

    def claim_task(self, task_file: Path) -> Path:
        """
        Claim task by moving to In_Progress/cloud/
        Returns new path or None if already claimed
        """
        if not task_file.exists():
            return None

        claimed_path = IN_PROGRESS_CLOUD / task_file.name

        try:
            shutil.move(str(task_file), str(claimed_path))
            self.log(f"Claimed task: {task_file.name}")
            return claimed_path
        except FileNotFoundError:
            # Another agent claimed it first
            self.log(f"Task already claimed: {task_file.name}", "WARNING")
            return None

    def release_task(self, task_file: Path, destination: Path):
        """Move task from In_Progress to destination"""
        if task_file.exists():
            dest_path = destination / task_file.name
            shutil.move(str(task_file), str(dest_path))
            self.log(f"Released task to {destination.name}: {task_file.name}")

    def triage_email(self, email_data: dict) -> dict:
        """
        Triage email and generate draft reply
        Returns draft reply data
        """
        self.log(f"Triaging email: {email_data.get('subject', 'No subject')}")

        prompt = f"""You are an AI executive assistant triaging emails.

Email Details:
From: {email_data.get('from', 'Unknown')}
Subject: {email_data.get('subject', 'No subject')}
Body:
{email_data.get('body', '')}

Tasks:
1. Determine priority (high/medium/low)
2. Categorize (action_required/informational/spam)
3. Draft a professional reply if action is required
4. Suggest next steps

Respond in JSON format:
{{
    "priority": "high|medium|low",
    "category": "action_required|informational|spam",
    "draft_reply": "Your draft reply here (or null if not needed)",
    "next_steps": ["Step 1", "Step 2"],
    "requires_approval": true|false,
    "reasoning": "Why you made these decisions"
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse JSON response
            content = response.content[0].text
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            self.log(f"Email triaged: {result['category']} - {result['priority']}")
            return result

        except Exception as e:
            self.log(f"Error triaging email: {e}", "ERROR")
            return {
                "priority": "medium",
                "category": "action_required",
                "draft_reply": None,
                "next_steps": ["Manual review required"],
                "requires_approval": True,
                "reasoning": f"Error during triage: {str(e)}"
            }

    def create_email_draft(self, email_data: dict, triage_result: dict):
        """Create email draft file in appropriate folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        email_id = email_data.get('id', timestamp)
        filename = f"email_{email_id}_{timestamp}.json"

        draft_data = {
            "type": "email_draft",
            "created_at": datetime.now().isoformat(),
            "created_by": self.agent_id,
            "original_email": email_data,
            "triage": triage_result,
            "status": "pending_approval" if triage_result["requires_approval"] else "needs_action"
        }

        # Determine destination based on approval requirement
        if triage_result["requires_approval"]:
            dest_dir = PENDING_APPROVAL_EMAIL
        else:
            dest_dir = NEEDS_ACTION_EMAIL

        filepath = dest_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(draft_data, f, indent=2, ensure_ascii=False)

        self.log(f"Created email draft: {filepath}")
        return filepath

    def generate_social_post(self, topic: str, platform: str) -> dict:
        """
        Generate social media post draft
        Returns post data
        """
        self.log(f"Generating {platform} post about: {topic}")

        prompt = f"""You are a social media manager creating engaging content.

Platform: {platform}
Topic: {topic}

Create a post that is:
- Engaging and authentic
- Appropriate for {platform}
- Professional yet personable
- Includes relevant hashtags (if appropriate)

Respond in JSON format:
{{
    "post_text": "Your post content here",
    "hashtags": ["hashtag1", "hashtag2"],
    "media_suggestion": "Description of image/video if needed",
    "best_time_to_post": "Morning|Afternoon|Evening",
    "requires_approval": true|false,
    "reasoning": "Why this approach"
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            self.log(f"Social post generated for {platform}")
            return result

        except Exception as e:
            self.log(f"Error generating social post: {e}", "ERROR")
            return {
                "post_text": f"[Draft] {topic}",
                "hashtags": [],
                "media_suggestion": None,
                "best_time_to_post": "Afternoon",
                "requires_approval": True,
                "reasoning": f"Error during generation: {str(e)}"
            }

    def create_social_draft(self, topic: str, platform: str, post_data: dict):
        """Create social post draft file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"social_{platform}_{timestamp}.json"

        draft_data = {
            "type": "social_post_draft",
            "created_at": datetime.now().isoformat(),
            "created_by": self.agent_id,
            "platform": platform,
            "topic": topic,
            "post_data": post_data,
            "status": "pending_approval" if post_data["requires_approval"] else "needs_action"
        }

        # Determine destination
        if post_data["requires_approval"]:
            dest_dir = PENDING_APPROVAL_SOCIAL
        else:
            dest_dir = NEEDS_ACTION_SOCIAL

        filepath = dest_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(draft_data, f, indent=2, ensure_ascii=False)

        self.log(f"Created social draft: {filepath}")
        return filepath

    def write_status_update(self, update_data: dict):
        """Write status update to Updates folder (for Dashboard merger)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cloud_update_{timestamp}.json"
        filepath = UPDATES_DIR / filename

        update = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
            "data": update_data
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(update, f, indent=2, ensure_ascii=False)

        self.log(f"Wrote status update: {filename}")

    def run_email_triage_cycle(self):
        """Run one cycle of email triage"""
        self.log("Starting email triage cycle")

        # In production, this would fetch from Gmail API
        # For now, we'll check for email files in Inbox
        inbox_dir = VAULT_DIR / "Inbox"
        if not inbox_dir.exists():
            self.log("No inbox directory found")
            return

        email_files = list(inbox_dir.glob("email_*.json"))
        self.log(f"Found {len(email_files)} emails to triage")

        for email_file in email_files:
            # Claim task
            claimed_path = self.claim_task(email_file)
            if not claimed_path:
                continue

            try:
                # Load email data
                with open(claimed_path, "r", encoding="utf-8") as f:
                    email_data = json.load(f)

                # Triage email
                triage_result = self.triage_email(email_data)

                # Create draft
                draft_path = self.create_email_draft(email_data, triage_result)

                # Move to Done (original email processed)
                done_dir = VAULT_DIR / "Done"
                done_dir.mkdir(exist_ok=True)
                self.release_task(claimed_path, done_dir)

                # Write status update
                self.write_status_update({
                    "action": "email_triaged",
                    "email_id": email_data.get("id"),
                    "priority": triage_result["priority"],
                    "draft_created": str(draft_path)
                })

            except Exception as e:
                self.log(f"Error processing email {email_file.name}: {e}", "ERROR")
                # Release back to inbox on error
                if claimed_path.exists():
                    self.release_task(claimed_path, inbox_dir)

    def run_social_generation_cycle(self):
        """Run one cycle of social post generation"""
        self.log("Starting social post generation cycle")

        # Check for social post requests in Plans folder
        plans_dir = VAULT_DIR / "Plans"
        if not plans_dir.exists():
            self.log("No plans directory found")
            return

        social_requests = list(plans_dir.glob("social_request_*.json"))
        self.log(f"Found {len(social_requests)} social post requests")

        for request_file in social_requests:
            # Claim task
            claimed_path = self.claim_task(request_file)
            if not claimed_path:
                continue

            try:
                # Load request
                with open(claimed_path, "r", encoding="utf-8") as f:
                    request_data = json.load(f)

                topic = request_data.get("topic", "Company update")
                platform = request_data.get("platform", "linkedin")

                # Generate post
                post_data = self.generate_social_post(topic, platform)

                # Create draft
                draft_path = self.create_social_draft(topic, platform, post_data)

                # Move to Done
                done_dir = VAULT_DIR / "Done"
                done_dir.mkdir(exist_ok=True)
                self.release_task(claimed_path, done_dir)

                # Write status update
                self.write_status_update({
                    "action": "social_post_drafted",
                    "platform": platform,
                    "topic": topic,
                    "draft_created": str(draft_path)
                })

            except Exception as e:
                self.log(f"Error processing social request {request_file.name}: {e}", "ERROR")
                if claimed_path.exists():
                    self.release_task(claimed_path, plans_dir)

    def run(self):
        """Run cloud agent main loop"""
        self.log("Cloud Agent starting")

        try:
            # Run email triage
            self.run_email_triage_cycle()

            # Run social post generation
            self.run_social_generation_cycle()

            self.log("Cloud Agent cycle completed")

        except Exception as e:
            self.log(f"Cloud Agent error: {e}", "ERROR")
            raise


def main():
    """Main entry point"""
    agent = CloudAgent()
    agent.run()


if __name__ == "__main__":
    main()
