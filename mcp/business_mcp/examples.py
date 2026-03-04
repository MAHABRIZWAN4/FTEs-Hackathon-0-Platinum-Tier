#!/usr/bin/env python3
"""
Business MCP Server - Example Usage

Demonstrates how to interact with the business MCP server tools.
This is for testing and demonstration purposes.
"""

import asyncio
import json
from pathlib import Path

# Example 1: Simulating MCP tool calls
def example_tool_calls():
    """
    Examples of tool call payloads that would be sent to the MCP server.
    """

    print("=" * 60)
    print("Example MCP Tool Calls")
    print("=" * 60)

    # Example 1: Send Email
    send_email_call = {
        "tool": "send_email",
        "arguments": {
            "to": "client@example.com",
            "subject": "Weekly Project Update",
            "body": "Dear Client,\n\nHere is your weekly project update...",
            "html": False
        }
    }

    print("\n1. Send Email Tool Call:")
    print(json.dumps(send_email_call, indent=2))

    # Example 2: Post to LinkedIn
    post_linkedin_call = {
        "tool": "post_linkedin",
        "arguments": {
            "content": "Excited to announce our latest product feature! 🚀\n\n#ProductUpdate #Innovation",
            "headless": True
        }
    }

    print("\n2. Post LinkedIn Tool Call:")
    print(json.dumps(post_linkedin_call, indent=2))

    # Example 3: Log Activity
    log_activity_call = {
        "tool": "log_activity",
        "arguments": {
            "message": "Completed quarterly report generation and distribution",
            "level": "SUCCESS"
        }
    }

    print("\n3. Log Activity Tool Call:")
    print(json.dumps(log_activity_call, indent=2))

    print("\n" + "=" * 60)


# Example 2: Direct function usage (bypassing MCP)
async def example_direct_usage():
    """
    Examples of calling the wrapped functions directly.
    """
    import sys
    from pathlib import Path

    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "scripts"))

    print("\n" + "=" * 60)
    print("Direct Function Usage Examples")
    print("=" * 60)

    # Example 1: Log Activity
    print("\n1. Logging an activity...")
    from mcp.business_mcp.server import log_activity

    success = log_activity("Test activity from example script", "INFO")
    if success:
        print("   ✓ Activity logged successfully")
    else:
        print("   ✗ Failed to log activity")

    # Example 2: Send Email (requires credentials)
    print("\n2. Sending email...")
    print("   (Skipped - requires EMAIL_ADDRESS and EMAIL_PASSWORD in .env)")

    # Example 3: Post LinkedIn (requires credentials)
    print("\n3. Posting to LinkedIn...")
    print("   (Skipped - requires LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env)")

    print("\n" + "=" * 60)


# Example 3: Reading the business log
def example_read_log():
    """
    Example of reading the business activity log.
    """
    project_root = Path(__file__).parent.parent.parent
    log_file = project_root / "vault" / "logs" / "business.log"

    print("\n" + "=" * 60)
    print("Reading Business Activity Log")
    print("=" * 60)

    if not log_file.exists():
        print("\nNo log file found yet. Run some activities first.")
        return

    print(f"\nLog file: {log_file}")
    print("\nLast 10 entries:")
    print("-" * 60)

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-10:]:
                print(line.rstrip())
    except Exception as e:
        print(f"Error reading log: {e}")

    print("-" * 60)


# Example 4: MCP Server Communication Protocol
def example_mcp_protocol():
    """
    Example of the JSON-RPC protocol used by MCP.
    """
    print("\n" + "=" * 60)
    print("MCP JSON-RPC Protocol Examples")
    print("=" * 60)

    # List tools request
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }

    print("\n1. List Tools Request:")
    print(json.dumps(list_tools_request, indent=2))

    # Call tool request
    call_tool_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "log_activity",
            "arguments": {
                "message": "Test message",
                "level": "INFO"
            }
        }
    }

    print("\n2. Call Tool Request:")
    print(json.dumps(call_tool_request, indent=2))

    print("\n" + "=" * 60)


def main():
    """
    Run all examples.
    """
    print("\n" + "=" * 60)
    print("BUSINESS MCP SERVER - USAGE EXAMPLES")
    print("=" * 60)

    # Show tool call examples
    example_tool_calls()

    # Show direct usage
    asyncio.run(example_direct_usage())

    # Show log reading
    example_read_log()

    # Show MCP protocol
    example_mcp_protocol()

    print("\n" + "=" * 60)
    print("For more information, see README.md")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
