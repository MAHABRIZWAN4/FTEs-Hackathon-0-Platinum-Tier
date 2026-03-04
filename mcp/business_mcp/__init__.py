"""
Business MCP Server Package

Exposes business automation tools via Model Context Protocol.
"""

__version__ = "1.0.0"
__author__ = "Gold Tier FTE System"

from pathlib import Path

# Package metadata
PACKAGE_ROOT = Path(__file__).parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent

__all__ = ["PACKAGE_ROOT", "PROJECT_ROOT"]
