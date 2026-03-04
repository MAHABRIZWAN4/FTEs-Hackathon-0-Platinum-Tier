#!/usr/bin/env python3
"""
Business MCP Server - Setup Validator

Validates that all dependencies and configurations are correct before running the server.
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

def check_python_version():
    """Check Python version is 3.8+."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro}", "success")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor} (requires 3.8+)", "error")
        return False

def check_dependencies():
    """Check required Python packages are installed."""
    required = {
        "mcp": "MCP SDK",
        "dotenv": "python-dotenv",
        "playwright": "Playwright"
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

def check_scripts():
    """Check that wrapped scripts exist."""
    project_root = Path(__file__).parent.parent.parent
    scripts = [
        project_root / "scripts" / "send_email.py",
        project_root / "scripts" / "post_linkedin.py"
    ]

    all_exist = True
    for script in scripts:
        if script.exists():
            print_status(f"{script.name} found", "success")
        else:
            print_status(f"{script.name} NOT found at {script}", "error")
            all_exist = False

    return all_exist

def check_env_file():
    """Check .env file exists and has required variables."""
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"

    if not env_file.exists():
        print_status(".env file NOT found", "warning")
        print_status(f"  Copy .env.example to {env_file} and configure", "info")
        return False

    print_status(".env file found", "success")

    # Check for required variables
    required_vars = [
        "EMAIL_ADDRESS",
        "EMAIL_PASSWORD",
        "LINKEDIN_EMAIL",
        "LINKEDIN_PASSWORD"
    ]

    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)

        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)

        if missing:
            print_status(f"Missing variables: {', '.join(missing)}", "warning")
            return False
        else:
            print_status("All required environment variables set", "success")
            return True
    except Exception as e:
        print_status(f"Error reading .env: {e}", "error")
        return False

def check_directories():
    """Check required directories exist."""
    project_root = Path(__file__).parent.parent.parent
    dirs = [
        project_root / "vault" / "logs",
        project_root / "logs"
    ]

    all_exist = True
    for directory in dirs:
        if directory.exists():
            print_status(f"{directory.relative_to(project_root)} exists", "success")
        else:
            print_status(f"{directory.relative_to(project_root)} NOT found, creating...", "warning")
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print_status(f"  Created {directory.relative_to(project_root)}", "success")
            except Exception as e:
                print_status(f"  Failed to create: {e}", "error")
                all_exist = False

    return all_exist

def check_playwright():
    """Check if Playwright browsers are installed."""
    try:
        import subprocess
        result = subprocess.run(
            ["playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if "is already installed" in result.stdout or result.returncode == 0:
            print_status("Playwright Chromium browser installed", "success")
            return True
        else:
            print_status("Playwright Chromium NOT installed", "warning")
            print_status("  Run: playwright install chromium", "info")
            return False
    except Exception:
        print_status("Could not verify Playwright installation", "warning")
        return False

def main():
    """Run all validation checks."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Business MCP Server - Setup Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    checks = [
        ("Python Version", check_python_version),
        ("Python Dependencies", check_dependencies),
        ("Business Scripts", check_scripts),
        ("Environment Configuration", check_env_file),
        ("Directory Structure", check_directories),
        ("Playwright Browsers", check_playwright)
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
        print(f"  python mcp/business_mcp/server.py\n")
        return 0
    else:
        print_status("Some checks failed. Fix issues before running server.", "warning")
        return 1

if __name__ == "__main__":
    sys.exit(main())
