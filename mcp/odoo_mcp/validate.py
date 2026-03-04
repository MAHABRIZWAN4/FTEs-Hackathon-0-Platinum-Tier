#!/usr/bin/env python3
"""
Odoo MCP Server - Setup Validator

Validates Odoo connection and credentials before running the server.
"""

import sys
import os
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_status(message, status="info"):
    """Print colored status message."""
    if status == "success":
        print(f"{GREEN}[+]{RESET} {message}")
    elif status == "error":
        print(f"{RED}[!]{RESET} {message}")
    elif status == "warning":
        print(f"{YELLOW}[*]{RESET} {message}")
    else:
        print(f"{BLUE}[i]{RESET} {message}")


def check_dependencies():
    """Check required Python packages."""
    required = {
        "mcp": "MCP SDK",
        "requests": "Requests",
        "dotenv": "python-dotenv"
    }

    all_installed = True
    for module, name in required.items():
        try:
            __import__(module)
            print_status(f"{name} installed", "success")
        except ImportError:
            print_status(f"{name} NOT installed", "error")
            all_installed = False

    return all_installed


def check_env_file():
    """Check .env file and Odoo credentials."""
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"

    if not env_file.exists():
        print_status(".env file NOT found", "error")
        return False

    print_status(".env file found", "success")

    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)

        required_vars = [
            "ODOO_URL",
            "ODOO_DB",
            "ODOO_USERNAME",
            "ODOO_PASSWORD"
        ]

        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)

        if missing:
            print_status(f"Missing variables: {', '.join(missing)}", "error")
            return False
        else:
            print_status("All Odoo credentials configured", "success")
            return True

    except Exception as e:
        print_status(f"Error reading .env: {e}", "error")
        return False


def test_odoo_connection():
    """Test connection to Odoo instance."""
    try:
        import requests
        from dotenv import load_dotenv

        load_dotenv()

        url = os.getenv("ODOO_URL")
        db = os.getenv("ODOO_DB")
        username = os.getenv("ODOO_USERNAME")
        password = os.getenv("ODOO_PASSWORD")

        print_status(f"Testing connection to {url}...", "info")

        # Test authentication
        response = requests.post(
            f"{url}/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "common",
                    "method": "authenticate",
                    "args": [db, username, password, {}]
                },
                "id": 1
            },
            timeout=10
        )

        result = response.json()

        if "result" in result and result["result"]:
            print_status(f"Authentication successful (User ID: {result['result']})", "success")
            return True
        else:
            print_status("Authentication failed: Invalid credentials", "error")
            return False

    except requests.exceptions.Timeout:
        print_status("Connection timeout - check ODOO_URL", "error")
        return False
    except requests.exceptions.ConnectionError:
        print_status("Connection failed - check network and ODOO_URL", "error")
        return False
    except Exception as e:
        print_status(f"Connection test error: {str(e)}", "error")
        return False


def check_directories():
    """Check required directories exist."""
    project_root = Path(__file__).parent.parent.parent
    dirs = [project_root / "vault" / "logs"]

    for directory in dirs:
        if directory.exists():
            print_status(f"{directory.relative_to(project_root)} exists", "success")
        else:
            print_status(f"Creating {directory.relative_to(project_root)}...", "warning")
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print_status(f"Created {directory.relative_to(project_root)}", "success")
            except Exception as e:
                print_status(f"Failed to create: {e}", "error")
                return False

    return True


def main():
    """Run all validation checks."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Odoo MCP Server - Setup Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    checks = [
        ("Python Dependencies", check_dependencies),
        ("Environment Configuration", check_env_file),
        ("Directory Structure", check_directories),
        ("Odoo Connection", test_odoo_connection)
    ]

    results = {}
    for name, check_func in checks:
        print(f"\n{BLUE}[{name}]{RESET}")
        results[name] = check_func()

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Validation Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "success" if result else "error"
        print_status(f"{name}: {'PASS' if result else 'FAIL'}", status)

    print(f"\n{BLUE}Result: {passed}/{total} checks passed{RESET}\n")

    if passed == total:
        print_status("All checks passed! Server is ready to run.", "success")
        print(f"\n{BLUE}To start the server:{RESET}")
        print(f"  python mcp/odoo_mcp/server.py\n")
        return 0
    else:
        print_status("Some checks failed. Fix issues before running server.", "warning")
        return 1


if __name__ == "__main__":
    sys.exit(main())
