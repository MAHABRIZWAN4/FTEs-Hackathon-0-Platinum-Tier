# Business MCP Server

Production-ready MCP server for business automation actions.

## Overview

This MCP (Model Context Protocol) server exposes three business automation tools:

- **send_email**: Send emails via SMTP
- **post_linkedin**: Post content to LinkedIn using browser automation
- **log_activity**: Log business activities to vault/logs/business.log

The server wraps existing Python scripts (`scripts/send_email.py` and `scripts/post_linkedin.py`) without duplicating code.

## Features

- ✅ Zero code duplication - wraps existing scripts
- ✅ Production-ready error handling and logging
- ✅ Comprehensive activity logging to vault/logs/business.log
- ✅ MCP-compliant tool definitions
- ✅ Async/await support for non-blocking operations
- ✅ Environment-based configuration

## Installation

### 1. Install Dependencies

```bash
pip install mcp python-dotenv playwright
playwright install chromium
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Email Configuration
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# LinkedIn Configuration
LINKEDIN_EMAIL=your-linkedin@email.com
LINKEDIN_PASSWORD=your-linkedin-password
```

**Gmail Users**: Use an [App Password](https://myaccount.google.com/apppasswords) instead of your regular password.

**LinkedIn Warning**: Automated posting may violate LinkedIn's Terms of Service. Use at your own risk.

## Running the Server

### Standalone Mode

```bash
python mcp/business_mcp/server.py
```

The server runs on stdio and communicates via JSON-RPC.

### With Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

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

### With Other MCP Clients

The server uses stdio transport and follows the MCP specification. Configure your client to execute:

```bash
python /path/to/mcp/business_mcp/server.py
```

## Available Tools

### 1. send_email

Send an email via SMTP.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject line
- `body` (string, required): Email body content
- `html` (boolean, optional): Whether body is HTML format (default: false)

**Example:**
```json
{
  "to": "recipient@example.com",
  "subject": "Weekly Report",
  "body": "Here is your weekly report...",
  "html": false
}
```

**Returns:**
- Success: "✓ Email sent successfully to {recipient}"
- Failure: "✗ Failed to send email. Check logs/actions.log"

### 2. post_linkedin

Post text content to LinkedIn using browser automation.

**Parameters:**
- `content` (string, required): Text content to post
- `headless` (boolean, optional): Run browser in headless mode (default: true)

**Example:**
```json
{
  "content": "Excited to share our latest product update! 🚀",
  "headless": true
}
```

**Returns:**
- Success: "✓ LinkedIn post published successfully"
- Failure: "✗ Failed to publish LinkedIn post. Check logs/actions.log"

**Notes:**
- First run may require CAPTCHA solving
- Set `headless: false` to see the browser window
- May require manual intervention for 2FA

### 3. log_activity

Log a business activity message to vault/logs/business.log.

**Parameters:**
- `message` (string, required): Activity message to log
- `level` (string, optional): Log level - INFO, SUCCESS, WARNING, ERROR (default: INFO)

**Example:**
```json
{
  "message": "Completed quarterly report generation",
  "level": "SUCCESS"
}
```

**Returns:**
- Success: "✓ Activity logged: [LEVEL] message"
- Failure: "✗ Failed to log activity"

## Logging

### Activity Logs

All business activities are logged to:
```
vault/logs/business.log
```

Format:
```
[2026-03-03 14:30:45] [INFO] Sending email to client@example.com: Project Update
[2026-03-03 14:30:47] [SUCCESS] Email sent successfully to client@example.com
[2026-03-03 14:31:02] [INFO] Posting to LinkedIn: Excited to share...
[2026-03-03 14:31:15] [SUCCESS] LinkedIn post published successfully
```

### Script Logs

Individual scripts also log to:
```
logs/actions.log
```

This contains detailed execution logs from send_email.py and post_linkedin.py.

## Architecture

```
mcp/business_mcp/
├── server.py          # MCP server implementation
└── README.md          # This file

scripts/
├── send_email.py      # Email sending logic (wrapped by MCP)
└── post_linkedin.py   # LinkedIn posting logic (wrapped by MCP)

vault/logs/
└── business.log       # Business activity log

logs/
└── actions.log        # Detailed script execution logs
```

## Error Handling

The server includes comprehensive error handling:

- **Missing credentials**: Returns clear error messages
- **Network failures**: Logged with details in actions.log
- **CAPTCHA/2FA**: LinkedIn poster pauses for manual intervention
- **Invalid parameters**: Validated before execution
- **Script failures**: Caught and logged with context

## Security Considerations

1. **Credentials**: Store in `.env` file, never commit to version control
2. **App Passwords**: Use app-specific passwords for Gmail
3. **LinkedIn ToS**: Automated posting may violate terms of service
4. **Logs**: May contain sensitive information, secure appropriately
5. **Access Control**: Restrict access to the MCP server endpoint

## Troubleshooting

### Email Not Sending

1. Check `.env` has correct EMAIL_ADDRESS and EMAIL_PASSWORD
2. For Gmail, use an App Password, not your regular password
3. Check logs/actions.log for detailed error messages
4. Verify SMTP_SERVER and SMTP_PORT are correct

### LinkedIn Post Failing

1. Check `.env` has correct LINKEDIN_EMAIL and LINKEDIN_PASSWORD
2. Run with `headless: false` to see what's happening
3. Solve any CAPTCHA challenges manually
4. Check logs/actions.log for detailed error messages
5. LinkedIn may have rate limits or security checks

### MCP Server Not Starting

1. Ensure MCP SDK is installed: `pip install mcp`
2. Check Python path includes project root
3. Verify scripts/send_email.py and scripts/post_linkedin.py exist
4. Check vault/logs directory is writable

## Development

### Testing Tools Individually

```bash
# Test email sending
python scripts/send_email.py --to test@example.com --subject "Test" --body "Hello"

# Test LinkedIn posting
python scripts/post_linkedin.py "Test post content"
```

### Adding New Tools

1. Create the business logic script in `scripts/`
2. Import the function in `server.py`
3. Add tool definition in `list_tools()`
4. Add handler function in `call_tool()`
5. Update this README

## License

Part of the Gold Tier FTE automation system.

## Support

For issues or questions:
1. Check logs/actions.log for detailed error messages
2. Check vault/logs/business.log for activity history
3. Verify environment variables are set correctly
4. Ensure all dependencies are installed
