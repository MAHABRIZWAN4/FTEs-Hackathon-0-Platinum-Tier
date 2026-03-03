#!/usr/bin/env python3
"""
Gmail Watcher Agent Skill
Monitors Gmail inbox for new unread emails and processes them automatically.
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import os
import time
from datetime import datetime
from pathlib import Path
import sys
from dotenv import load_dotenv

# Rich library for beautiful terminal output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Load environment variables
load_dotenv()

# Configuration
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
INBOX_PATH = Path('AI_Employee_Vault/Inbox')
LOG_PATH = Path('logs/actions.log')
CHECK_INTERVAL = 60  # seconds

# Gmail IMAP/SMTP settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Auto-reply message
AUTO_REPLY_MESSAGE = """Thank you for your email. This is an automated response
from AI Employee. I have received your message and will
get back to you shortly."""


def log_message(message, level="INFO"):
    """Log message to both console and log file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"

    # Ensure log directory exists
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Cyber-Silver Professional console output
    if RICH_AVAILABLE:
        if level == "ERROR":
            console.print(f"[bold red]🚫 FAIL:[/] [red]{message}[/red]")
        elif level == "SUCCESS":
            console.print(f"[bold green]✅ DONE:[/] [green]{message}[/green]")
        elif level == "WARNING":
            console.print(f"[bold yellow]🔍 SCAN:[/] [yellow]{message}[/yellow]")
        elif level in ["GMAIL", "HEARTBEAT"]:
            console.print(f"[bold blue]⚡ EXEC:[/] [bold cyan]{message}[/bold cyan]")
        elif level in ["DETECTED", "SAVED", "REPLY", "MARKED"]:
            console.print(f"[bold green]✅ DONE:[/] [bright_white]{message}[/bright_white]")
        else:
            console.print(f"[bold cyan]⚡ EXEC:[/] [cyan]{message}[/cyan]")
    else:
        print(log_entry)

    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]🚫 FAIL:[/] Could not write to log file: {e}")
        else:
            print(f"Warning: Could not write to log file: {e}")


def validate_credentials():
    """Validate that required credentials are present."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        log_message("ERROR: EMAIL_ADDRESS and EMAIL_PASSWORD must be set in .env file", "ERROR")
        log_message("Please create a .env file with your Gmail credentials", "ERROR")
        log_message("Use an App Password, not your regular Gmail password", "ERROR")
        return False
    return True


def decode_email_header(header):
    """Decode email header to handle various encodings."""
    if header is None:
        return ""

    decoded_parts = decode_header(header)
    decoded_string = ""

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                decoded_string += part.decode(encoding or 'utf-8', errors='replace')
            except:
                decoded_string += part.decode('utf-8', errors='replace')
        else:
            decoded_string += str(part)

    return decoded_string


def extract_email_body(msg):
    """Extract email body from message, handling both plain text and HTML."""
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Skip attachments
            if "attachment" in content_disposition:
                continue

            # Get plain text or HTML
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    break  # Prefer plain text
                except:
                    pass
            elif content_type == "text/html" and not body:
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='replace')
        except:
            body = str(msg.get_payload())

    return body.strip()


def save_email_to_vault(sender, subject, date_str, body):
    """Save email details to vault as markdown file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"email_{timestamp}.md"
    filepath = INBOX_PATH / filename

    # Ensure inbox directory exists
    INBOX_PATH.mkdir(parents=True, exist_ok=True)

    # Create markdown content
    content = f"""# Email from {sender}

**From:** {sender}
**Subject:** {subject}
**Date:** {date_str}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Message

{body}

---

**Status:** Auto-reply sent ✓
**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        log_message(f"Email saved to: {filename}", "SAVED")
        return filename
    except Exception as e:
        log_message(f"Failed to save email: {e}", "ERROR")
        return None


def send_auto_reply(to_address, original_subject):
    """Send auto-reply via SMTP."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_address
        msg['Subject'] = f"Re: {original_subject}"

        # Add body
        msg.attach(MIMEText(AUTO_REPLY_MESSAGE, 'plain'))

        # Connect to SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        log_message(f"Auto-reply sent to: {to_address}", "REPLY")
        return True
    except Exception as e:
        log_message(f"Failed to send auto-reply: {e}", "ERROR")
        return False


def mark_as_read(mail, email_id):
    """Mark email as read in Gmail."""
    try:
        mail.store(email_id, '+FLAGS', '\\Seen')
        log_message("Email marked as read", "MARKED")
        return True
    except Exception as e:
        log_message(f"Failed to mark as read: {e}", "ERROR")
        return False


def process_email(mail, email_id):
    """Process a single email: parse, save, reply, mark as read."""
    try:
        # Fetch email data
        status, data = mail.fetch(email_id, '(RFC822)')
        if status != 'OK':
            log_message(f"Failed to fetch email {email_id}", "ERROR")
            return False

        # Parse email
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract headers
        sender = decode_email_header(msg.get('From', ''))
        subject = decode_email_header(msg.get('Subject', '(No Subject)'))
        date_str = msg.get('Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        log_message(f"New email from: {sender}", "DETECTED")
        log_message(f"Subject: {subject}", "SUBJECT")

        # Extract body
        body = extract_email_body(msg)

        # Save to vault
        saved_file = save_email_to_vault(sender, subject, date_str, body)
        if not saved_file:
            return False

        # Extract sender email address (remove name if present)
        sender_email = sender
        if '<' in sender and '>' in sender:
            sender_email = sender.split('<')[1].split('>')[0].strip()

        # Send auto-reply
        send_auto_reply(sender_email, subject)

        # Mark as read
        mark_as_read(mail, email_id)

        log_message("Email processed successfully", "SUCCESS")
        return True

    except Exception as e:
        log_message(f"Error processing email: {e}", "ERROR")
        return False


def check_inbox():
    """Check Gmail inbox for new unread emails."""
    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)

        # Login
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        # Select inbox
        mail.select('INBOX')

        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK':
            log_message("Failed to search for unread emails", "ERROR")
            mail.logout()
            return 0

        # Get list of email IDs
        email_ids = messages[0].split()

        if not email_ids:
            return 0

        log_message(f"Found {len(email_ids)} unread email(s)", "INFO")

        # Process each email
        processed_count = 0
        for email_id in email_ids:
            if process_email(mail, email_id):
                processed_count += 1

        # Logout
        mail.logout()

        return processed_count

    except imaplib.IMAP4.error as e:
        log_message(f"IMAP error: {e}", "ERROR")
        log_message("Check your EMAIL_ADDRESS and EMAIL_PASSWORD in .env", "ERROR")
        return -1
    except Exception as e:
        log_message(f"Connection error: {e}", "ERROR")
        return -1


def main():
    """Main loop: continuously monitor Gmail inbox."""
    # Cyber-Silver Professional Header Panel
    if RICH_AVAILABLE:
        console.print()
        console.print(Panel.fit(
            "[bold cyan]★ ════════════════════════════════════════ ★[/bold cyan]\n"
            "[bold bright_white]📧 GMAIL WATCHER AGENT[/bold bright_white]\n"
            "[dim cyan]Silver Tier AI Employee[/dim cyan]\n"
            "[bold cyan]★ ════════════════════════════════════════ ★[/bold cyan]",
            border_style="bold cyan",
            padding=(1, 2)
        ))
        console.print()
    else:
        log_message("=" * 60, "INFO")
        log_message("Gmail Watcher Agent Skill Started", "GMAIL")
        log_message(f"Monitoring: {EMAIL_ADDRESS}", "GMAIL")
        log_message(f"Check interval: {CHECK_INTERVAL} seconds", "GMAIL")
        log_message("=" * 60, "INFO")
        return

    log_message(f"Monitoring: {EMAIL_ADDRESS}", "GMAIL")
    log_message(f"Check interval: {CHECK_INTERVAL} seconds", "GMAIL")

    # Validate credentials
    if not validate_credentials():
        sys.exit(1)

    # Test connection
    log_message("Testing Gmail connection...", "INFO")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.logout()
        log_message("Connection successful!", "SUCCESS")
    except Exception as e:
        log_message(f"Connection failed: {e}", "ERROR")
        log_message("Please check your credentials and internet connection", "ERROR")
        sys.exit(1)

    # Main monitoring loop
    cycle_count = 0
    total_processed = 0

    try:
        while True:
            cycle_count += 1

            # Check inbox
            processed = check_inbox()

            if processed > 0:
                total_processed += processed
                log_message(f"Processed {processed} email(s) this cycle", "INFO")
            elif processed == -1:
                log_message("Connection error, will retry next cycle", "WARNING")

            # Heartbeat every 10 cycles
            if cycle_count % 10 == 0:
                log_message(f"Gmail watcher active - {total_processed} emails processed", "HEARTBEAT")

            # Wait before next check
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print()
            console.print(Panel(
                "[bold cyan]★ ═══════════════════════════════════ ★[/bold cyan]\n"
                "[bold yellow]⚠️  Gmail Watcher Stopped[/bold yellow]\n"
                f"[cyan]Total emails processed:[/cyan] [bright_white]{total_processed}[/bright_white]\n"
                "[bold cyan]★ ═══════════════════════════════════ ★[/bold cyan]",
                border_style="bold yellow",
                padding=(1, 2)
            ))
            console.print()
        else:
            log_message("=" * 60, "INFO")
            log_message("Gmail Watcher stopped by user", "GMAIL")
            log_message(f"Total emails processed: {total_processed}", "GMAIL")
            log_message("=" * 60, "INFO")
        sys.exit(0)
    except Exception as e:
        log_message(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
