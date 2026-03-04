#!/usr/bin/env python3
"""
Business MCP Server - Quick Start Launcher

Validates setup and launches the MCP server.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Validate and launch the server."""
    script_dir = Path(__file__).parent

    print("🔍 Validating setup...\n")

    # Run validation
    validate_script = script_dir / "validate.py"
    result = subprocess.run([sys.executable, str(validate_script)])

    if result.returncode != 0:
        print("\n❌ Validation failed. Please fix the issues above.")
        return 1

    print("\n🚀 Starting Business MCP Server...\n")

    # Launch server
    server_script = script_dir / "server.py"
    try:
        subprocess.run([sys.executable, str(server_script)])
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n\n❌ Server error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
