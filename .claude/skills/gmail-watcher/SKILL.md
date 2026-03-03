# Gmail Watcher Agent Skill

## Description
Continuously monitors Gmail inbox for new unread emails and automatically processes them. This skill acts as an email gateway for the AI Employee, detecting incoming messages, logging them, saving details to the vault, sending auto-replies, and marking emails as read.

## Trigger
- Command: `/gmail-watcher` or `gmail-watcher`
- Auto-start: Can be configured to run as a background service
- Manual: `python scripts/watch_gmail.py`

## Capabilities
- Real-time monitoring of Gmail inbox via IMAP
- Detects new unread emails every 60 seconds
- Extracts email metadata (From, Subject, Date, Body)
- Saves email details to `AI_Employee_Vault/Inbox/email_<timestamp>.md`
- Sends professional auto-reply via SMTP
- Marks processed emails as read
- Comprehensive logging to `logs/actions.log`
- Handles both plain text and HTML emails
- Graceful error handling and recovery
- Production-ready with secure credential management

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. Connect to Gmail via IMAP (every 60 seconds)        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  2. Search for unread emails                            │
│     - Query: UNSEEN flag                                │
│     - Fetch email headers and body                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  3. Parse email content                                 │
│     - Extract: From, Subject, Date, Body                │
│     - Handle plain text and HTML formats                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  4. Log detection                                       │
│     - Timestamp + sender + subject → logs/actions.log   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  5. Save to Vault                                       │
│     - Create: email_<timestamp>.md in Inbox             │
│     - Include all email metadata and content            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  6. Send auto-reply via SMTP                            │
│     - Professional acknowledgment message               │
│     - Reply to sender's email address                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  7. Mark email as read                                  │
│     - Set SEEN flag via IMAP                            │
│     - Prevent duplicate processing                      │
└─────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables
Required in `.env` file:
- `EMAIL_ADDRESS`: Gmail address (e.g., your-email@gmail.com)
- `EMAIL_PASSWORD`: Gmail app password (NOT regular password)

### Gmail Setup Requirements
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
3. Use the App Password as `EMAIL_PASSWORD` in `.env`

### File Locations
- **Log File**: `logs/actions.log`
- **Email Storage**: `AI_Employee_Vault/Inbox/email_<timestamp>.md`
- **Script**: `scripts/watch_gmail.py`

## Auto-Reply Message

The skill sends this professional auto-reply to all incoming emails:

```
Thank you for your email. This is an automated response
from AI Employee. I have received your message and will
get back to you shortly.
```

## Usage Examples

### Start Watcher (Foreground)
```bash
python scripts/watch_gmail.py
```

### Start Watcher (Background - Windows)
```powershell
Start-Process python -ArgumentList "scripts/watch_gmail.py" -WindowStyle Hidden
```

### Via Claude Code
```
/gmail-watcher
```

### Check Logs
```bash
tail -f logs/actions.log
```

## Email Storage Format

Each email is saved as a markdown file in `AI_Employee_Vault/Inbox/`:

```markdown
# Email from sender@example.com

**From:** sender@example.com
**Subject:** Project Update
**Date:** 2026-03-02 14:30:00
**Received:** 2026-03-02 14:30:15

---

## Message

[Email body content here...]

---

**Status:** Auto-reply sent ✓
**Processed:** 2026-03-02 14:30:16
```

## Logging Format

All actions are logged to `logs/actions.log`:

```
[2026-03-02 14:30:00] [GMAIL] Started monitoring inbox (interval: 60s)
[2026-03-02 14:30:15] [DETECTED] New email from: sender@example.com
[2026-03-02 14:30:15] [SUBJECT] Project Update
[2026-03-02 14:30:15] [SAVED] Email saved to: email_20260302_143015.md
[2026-03-02 14:30:16] [REPLY] Auto-reply sent to: sender@example.com
[2026-03-02 14:30:16] [MARKED] Email marked as read
[2026-03-02 14:30:16] [SUCCESS] Email processed successfully
```

## Error Handling

The watcher handles various error scenarios:

- **Connection Failures**: Retries connection on next cycle
- **Authentication Errors**: Logs error and exits (requires credential fix)
- **SMTP Failures**: Logs error but continues processing
- **Missing Directories**: Automatically creates required folders
- **Malformed Emails**: Logs error and skips to next email
- **Network Issues**: Retries on next polling cycle
- **Keyboard Interrupt**: Graceful shutdown with cleanup

## Security Considerations

- **App Passwords**: Uses Gmail App Passwords (more secure than regular passwords)
- **Environment Variables**: Credentials stored in `.env` (not in code)
- **No Plaintext Storage**: Passwords never logged or saved to files
- **IMAP SSL**: Uses encrypted connection (port 993)
- **SMTP TLS**: Uses encrypted connection (port 587)
- **Credential Validation**: Validates credentials on startup

## Performance

- **CPU Usage**: Minimal (sleeps between polls)
- **Memory Usage**: Low (processes one email at a time)
- **Network I/O**: Efficient (only fetches unread emails)
- **Polling Interval**: 60 seconds (configurable)
- **Scalability**: Handles hundreds of emails efficiently

## Integration Points

### Upstream
- **Gmail Inbox**: Monitors for new unread emails
- **External Senders**: Anyone can email the monitored address

### Downstream
- **Vault Inbox**: Emails saved as .md files
- **Vault Watcher**: Can pick up email files for further processing
- **Task Planner**: Email content can trigger task creation
- **Dashboard**: Email activity visible in logs

## Production Deployment

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
5. Program: `python`
6. Arguments: `F:\FTEs\Silver Tier\scripts\watch_gmail.py`
7. Start in: `F:\FTEs\Silver Tier`

### Systemd Service (Linux)
```ini
[Unit]
Description=AI Employee Gmail Watcher
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 scripts/watch_gmail.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker
```dockerfile
CMD ["python", "scripts/watch_gmail.py"]
```

## Monitoring & Health Checks

The watcher logs heartbeat messages every 10 cycles:
```
[2026-03-02 14:40:00] [HEARTBEAT] Gmail watcher active - 5 emails processed
```

Monitor `logs/actions.log` for:
- Regular heartbeat messages
- Connection status
- Processing success rate
- Error patterns

## Limitations

- **Polling-Based**: 60-second delay (not real-time)
- **Gmail Only**: Designed for Gmail IMAP/SMTP
- **Single Account**: Monitors one email address
- **Auto-Reply All**: Sends auto-reply to every email
- **No Filtering**: Processes all unread emails (no spam filtering)

## Future Enhancements

- Support for multiple email accounts
- Configurable auto-reply templates
- Spam/filter rules
- Email categorization (urgent, normal, low priority)
- Attachment handling and storage
- Email threading support
- Webhook notifications
- Metrics dashboard

## Dependencies

- Python 3.7+
- Standard library: `imaplib`, `smtplib`, `email`
- Requires `.env` file with credentials
- Compatible with existing AI Employee Vault structure

## Troubleshooting

### "Authentication failed"
- Verify EMAIL_ADDRESS and EMAIL_PASSWORD in `.env`
- Ensure you're using an App Password, not regular password
- Check 2FA is enabled on Google account

### "Connection refused"
- Check internet connection
- Verify Gmail IMAP/SMTP is enabled
- Check firewall settings

### "No emails detected"
- Verify emails are actually unread in Gmail
- Check IMAP folder (should be INBOX)
- Test by sending yourself an email

### "Auto-reply not sent"
- Check SMTP credentials
- Verify sender email is valid
- Check logs for specific SMTP errors

## Notes

- Designed for 24/7 operation
- Minimal resource footprint
- Self-healing (continues on errors)
- Integrates seamlessly with existing vault system
- Production-tested and reliable
- Respects Gmail API rate limits
