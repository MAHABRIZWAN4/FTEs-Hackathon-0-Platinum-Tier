# Business MCP Server - Quick Start Guide

## What Was Created

```
mcp/business_mcp/
├── server.py           # Main MCP server (wraps existing scripts)
├── __init__.py         # Package initialization
├── requirements.txt    # Python dependencies
├── .env.example        # Configuration template
├── validate.py         # Setup validation script
├── launch.py           # Quick launcher
└── README.md           # Full documentation

vault/logs/
└── business.log        # Business activity log (auto-created)
```

## Installation

### 1. Install MCP SDK

```bash
pip install mcp
```

### 2. Verify Setup

```bash
python mcp/business_mcp/validate.py
```

This checks:
- Python version (3.8+)
- Dependencies (mcp, python-dotenv, playwright)
- Existing scripts (send_email.py, post_linkedin.py)
- Environment configuration (.env file)
- Directory structure (vault/logs, logs)

### 3. Run the Server

```bash
# Option 1: Direct launch
python mcp/business_mcp/server.py

# Option 2: With validation
python mcp/business_mcp/launch.py
```

## Available Tools

1. **send_email** - Send emails via SMTP
2. **post_linkedin** - Post to LinkedIn (browser automation)
3. **log_activity** - Log business activities to vault/logs/business.log

## Integration with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "business-mcp": {
      "command": "python",
      "args": ["F:/FTEs/Gold Tier/mcp/business_mcp/server.py"]
    }
  }
}
```

## Key Features

✅ Zero code duplication - wraps existing scripts
✅ Production-ready error handling
✅ Comprehensive logging to vault/logs/business.log
✅ MCP-compliant tool definitions
✅ Async/await support
✅ Environment-based configuration

## Next Steps

1. Install MCP SDK: `pip install mcp`
2. Run validation: `python mcp/business_mcp/validate.py`
3. Test the server: `python mcp/business_mcp/server.py`
4. Integrate with Claude Desktop (optional)

See README.md for full documentation.
