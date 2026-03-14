# Platinum Tier Demo Guide

## Overview

This guide explains how to run and present the Platinum Tier AI Employee demo for the minimum passing gate.

## Demo Scenario

**"Email arrives while Local is offline → Cloud drafts reply + writes approval file → when Local returns, user approves → Local executes send via MCP → logs → moves task to /Done"**

This demonstrates the core dual-agent architecture and approval workflow.

---

## Quick Start

### Option 1: Interactive Demo (Recommended for Judges)

```bash
python scripts/platinum_demo.py
```

**Duration:** 3-5 minutes
**Interaction:** User approves/rejects draft
**Best for:** Live demonstrations, showing approval workflow

### Option 2: Integrated Presentation

```bash
python scripts/platinum_integrated_demo.py
```

**Duration:** 5-7 minutes
**Interaction:** Press Enter to advance through sections
**Best for:** Explaining architecture before live demo

---

## Demo Scripts

### 1. `platinum_demo.py` - Interactive Demo

**What it does:**
- Simulates complete email workflow
- Shows Cloud and Local agent separation
- Requires user approval
- Demonstrates claim-by-move pattern
- Shows task lifecycle (Needs_Action → Done)

**Steps:**

**Step 1: Email Arrives**
- Creates fake email in Needs_Action/email/
- Shows email content
- Indicates Local Agent is offline

**Step 2: Cloud Agent Processing**
- Reads email from Needs_Action/
- Claims task (moves to In_Progress/cloud/)
- Drafts reply using Claude API (or fallback)
- Writes approval file to Pending_Approval/
- Shows draft to user
- Waits for Local Agent

**Step 3: Local Agent Returns**
- Finds pending approval
- Shows draft to user
- Requests approval (APPROVED/REJECTED)
- If approved:
  - Moves to In_Progress/local/
  - Simulates send via MCP
  - Moves to Done/
  - Logs to system_health.md

**Step 4: Final State**
- Shows Done folder contents
- Shows completed task details
- Shows system health log
- Summarizes what was demonstrated

### 2. `platinum_integrated_demo.py` - Presentation

**What it shows:**
- System architecture diagram
- Workflow steps (10 steps)
- Security model comparison
- Key features list
- Folder structure
- System metrics
- Demo summary

**Use this to:**
- Explain architecture before demo
- Show judges the complete system
- Highlight key features
- Set context for interactive demo

---

## Running the Demo

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Set API key for real Claude drafts
export ANTHROPIC_API_KEY=your_key_here
```

### Step-by-Step Demo Flow

**1. Start with Integrated Presentation (Optional)**
```bash
python scripts/platinum_integrated_demo.py
```
- Shows architecture
- Explains workflow
- Sets context

**2. Run Interactive Demo**
```bash
python scripts/platinum_demo.py
```
- Follow on-screen prompts
- Press Enter to advance
- Approve draft when prompted

**3. Show Results**
- Check `AI_Employee_Vault/Done/` folder
- Check `AI_Employee_Vault/Logs/system_health.md`
- Show task completion

---

## Explaining to Judges

### Key Points to Emphasize

**1. Dual-Agent Architecture**
```
"We have two agents: Cloud and Local. Cloud runs 24/7 on GitHub Actions
and handles automation. Local runs on your machine and handles approvals
and final actions. This separation provides security and control."
```

**2. Security by Design**
```
"Cloud agent NEVER sends emails or posts to social media. It only creates
drafts. All final actions require local approval. This prevents unauthorized
actions even if the cloud is compromised."
```

**3. Claim-by-Move Pattern**
```
"Tasks are claimed by moving files between folders. This is atomic and
prevents race conditions. No lock files needed - Git handles it naturally."
```

**4. Single-Writer Rule**
```
"Only one agent writes to each file. Cloud writes to Updates/, Local writes
to Dashboard.md. This prevents merge conflicts in Git."
```

**5. Complete Task Lifecycle**
```
"Watch the task move through folders: Needs_Action → In_Progress/cloud →
Pending_Approval → In_Progress/local → Done. Each step is logged."
```

### Demo Script for Judges

**Opening (30 seconds):**
```
"I'm going to show you our Platinum Tier AI Employee - a dual-agent system
that automates email triage while maintaining human control. The key innovation
is the separation between Cloud automation and Local approval."
```

**Architecture (1 minute):**
```
"Here's how it works: [Show integrated demo architecture]
- Cloud Agent runs 24/7 on GitHub Actions
- Local Agent runs on your machine
- They communicate through a Git-based vault
- Cloud drafts, Local approves and sends"
```

**Live Demo (3 minutes):**
```
"Let me show you the workflow: [Run platinum_demo.py]
1. Email arrives while Local is offline
2. Cloud reads it and drafts a reply using Claude AI
3. Cloud writes an approval file - notice it doesn't send
4. Local comes online and finds the pending approval
5. I review and approve the draft
6. Local executes the send via MCP
7. Task is logged and moved to Done"
```

**Key Features (1 minute):**
```
"This demonstrates several key features:
- Security: Cloud can't send without approval
- Scalability: Claim-by-move prevents race conditions
- Reliability: Single-writer prevents merge conflicts
- Auditability: Complete logging of all actions
- Production-ready: 24/7 automation with health monitoring"
```

**Closing (30 seconds):**
```
"This is a production-ready system with 4 GitHub Actions workflows,
15+ scripts, comprehensive health monitoring, and automated CEO briefings.
It's running 24/7 in the cloud right now."
```

---

## Demo Variations

### Quick Demo (2 minutes)

Skip integrated presentation, run only:
```bash
python scripts/platinum_demo.py
```

Focus on:
- Cloud drafts (automated)
- Local approves (manual)
- Security separation

### Full Demo (10 minutes)

1. Run integrated presentation
2. Run interactive demo
3. Show GitHub Actions workflows
4. Show health monitoring
5. Show CEO briefing

### Technical Deep Dive (15 minutes)

1. Explain architecture in detail
2. Show code structure
3. Run interactive demo
4. Show vault folder structure
5. Explain claim-by-move pattern
6. Show health monitoring system
7. Show CEO briefing generation

---

## Troubleshooting

### Demo Script Fails

**Issue:** Script crashes or errors

**Solutions:**
```bash
# Check dependencies
pip install -r requirements.txt

# Check folder structure
ls -la AI_Employee_Vault/

# Run with verbose output
python -v scripts/platinum_demo.py
```

### No Draft Generated

**Issue:** Draft reply is generic fallback

**Cause:** ANTHROPIC_API_KEY not set

**Solution:**
```bash
export ANTHROPIC_API_KEY=your_key_here
python scripts/platinum_demo.py
```

**Note:** Fallback draft still works for demo purposes

### Folders Not Created

**Issue:** Missing vault folders

**Solution:**
```bash
# Create manually
mkdir -p AI_Employee_Vault/Needs_Action/email
mkdir -p AI_Employee_Vault/Pending_Approval/email
mkdir -p AI_Employee_Vault/In_Progress/cloud
mkdir -p AI_Employee_Vault/In_Progress/local
mkdir -p AI_Employee_Vault/Done
mkdir -p AI_Employee_Vault/Logs
```

---

## Customizing the Demo

### Change Email Content

Edit `platinum_demo.py`, line ~60:

```python
email_data = {
    "from": "your_client@example.com",
    "subject": "Your Custom Subject",
    "body": "Your custom email body...",
    # ...
}
```

### Change Draft Reply

Edit `generate_draft_reply()` method to customize fallback:

```python
return f"""Your custom draft reply here..."""
```

### Add More Steps

Add additional steps in `run()` method:

```python
def run(self):
    # ... existing steps ...

    # Add custom step
    self.step5_custom_action()
```

---

## Demo Checklist

### Before Demo

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test demo script: `python scripts/platinum_demo.py`
- [ ] Check vault folders exist
- [ ] Optional: Set ANTHROPIC_API_KEY
- [ ] Prepare talking points
- [ ] Time the demo (should be 3-5 minutes)

### During Demo

- [ ] Explain dual-agent architecture
- [ ] Show Cloud drafting (automated)
- [ ] Show Local approval (manual)
- [ ] Emphasize security separation
- [ ] Show task lifecycle
- [ ] Show final state (Done folder)

### After Demo

- [ ] Answer questions about architecture
- [ ] Show GitHub Actions workflows (if asked)
- [ ] Show health monitoring (if asked)
- [ ] Show CEO briefing (if asked)
- [ ] Provide repository link

---

## FAQ for Judges

**Q: Why separate Cloud and Local agents?**

A: Security and control. Cloud automates repetitive tasks but can't send without approval. Local maintains human oversight for sensitive actions.

**Q: What prevents race conditions?**

A: Claim-by-move pattern. Tasks are claimed by moving files atomically. Git handles conflicts naturally.

**Q: What prevents merge conflicts?**

A: Single-writer rule. Only one agent writes to each file. Cloud writes to Updates/, Local merges them into Dashboard.md.

**Q: How does this scale?**

A: Cloud runs on GitHub Actions (unlimited for public repos). Multiple Local agents can run simultaneously. Claim-by-move prevents conflicts.

**Q: Is this production-ready?**

A: Yes. We have 4 GitHub Actions workflows running 24/7, health monitoring with auto-restart, automated CEO briefings, and comprehensive logging.

**Q: What about security?**

A: Cloud has read-only access and can't send. All credentials stay on Local. Sensitive files never sync (.env, tokens). All actions logged.

**Q: Can I see it running live?**

A: Yes. Check our GitHub Actions tab to see workflows running. Health monitor updates every 5 minutes.

---

## Advanced Demo Features

### Show GitHub Actions

```bash
# View workflow runs
gh run list --limit 5

# View specific workflow
gh run list --workflow=cloud-agent.yml

# Show workflow logs
gh run view --log
```

### Show Health Monitoring

```bash
# Run health check
python scripts/health_check.py

# View health report
cat AI_Employee_Vault/Logs/system_health.md

# Start watchdog
python scripts/watchdog.py --once
```

### Show CEO Briefing

```bash
# Generate briefing
python scripts/platinum_ceo_briefing.py

# View latest briefing
cat AI_Employee_Vault/Briefings/$(ls -t AI_Employee_Vault/Briefings/ | head -1)
```

---

## Demo Success Criteria

### Minimum Passing Gate

✅ Email arrives
✅ Cloud drafts reply
✅ Cloud writes approval file
✅ Local shows approval
✅ User approves
✅ Local sends via MCP
✅ Task moves to Done
✅ Logging works

### Bonus Points

✅ Real Claude API draft (not fallback)
✅ Show GitHub Actions running
✅ Show health monitoring
✅ Show CEO briefing
✅ Explain architecture clearly
✅ Answer technical questions

---

## Summary

The Platinum Tier demo showcases:

1. **Dual-Agent Architecture** - Cloud + Local separation
2. **Security by Design** - Draft-only cloud, approval required
3. **Claim-by-Move Pattern** - No race conditions
4. **Single-Writer Rule** - No merge conflicts
5. **Complete Task Lifecycle** - Needs_Action → Done
6. **Production Features** - 24/7 automation, health monitoring, CEO briefings

**Demo Duration:** 3-5 minutes (interactive) or 10 minutes (full)

**Key Message:** "Production-ready AI employee with security, scalability, and human oversight."

---

## Quick Commands

```bash
# Run interactive demo
python scripts/platinum_demo.py

# Run presentation
python scripts/platinum_integrated_demo.py

# Check system health
python scripts/health_check.py

# View done tasks
ls AI_Employee_Vault/Done/

# View logs
cat AI_Employee_Vault/Logs/system_health.md
```

Good luck with your demo! 🚀
