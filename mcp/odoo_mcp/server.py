"""
Odoo MCP Server - Gold Tier AI Employee

This MCP server exposes Odoo ERP operations via JSON-RPC:
- create_invoice: Create customer invoices
- list_invoices: List and filter invoices
- record_payment: Record invoice payments

Uses Odoo's JSON-RPC API for integration.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

# Add parent directories to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("[ERROR] MCP SDK not installed. Run: pip install mcp")
    sys.exit(1)

# Import required libraries
try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] Required libraries not installed. Run: pip install requests python-dotenv")
    sys.exit(1)

# Configuration
VAULT_LOGS_DIR = project_root / "vault" / "logs"
ODOO_LOG = VAULT_LOGS_DIR / "odoo.log"

# Ensure vault logs directory exists
VAULT_LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv()

# Odoo configuration from environment
ODOO_URL = os.getenv("ODOO_URL", "https://your-odoo-instance.odoo.com")
ODOO_DB = os.getenv("ODOO_DB", "your-database")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

# Initialize MCP server
app = Server("odoo-mcp")


def log_activity(message: str, level: str = "INFO") -> bool:
    """
    Log an Odoo activity to vault/logs/odoo.log.

    Args:
        message (str): Activity message to log
        level (str): Log level (INFO, SUCCESS, WARNING, ERROR)

    Returns:
        bool: True if logged successfully
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        with open(ODOO_LOG, "a", encoding="utf-8") as f:
            f.write(log_entry)

        return True
    except Exception as e:
        print(f"[ERROR] Failed to log activity: {e}")
        return False


class OdooClient:
    """
    Odoo JSON-RPC client for API operations.
    """

    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.uid = None

    def authenticate(self) -> bool:
        """
        Authenticate with Odoo and get user ID.

        Returns:
            bool: True if authentication successful
        """
        try:
            response = requests.post(
                f"{self.url}/jsonrpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "service": "common",
                        "method": "authenticate",
                        "args": [self.db, self.username, self.password, {}]
                    },
                    "id": 1
                },
                timeout=30
            )

            result = response.json()
            if "result" in result and result["result"]:
                self.uid = result["result"]
                log_activity(f"Authenticated as user ID: {self.uid}", "SUCCESS")
                return True
            else:
                log_activity("Authentication failed: Invalid credentials", "ERROR")
                return False

        except Exception as e:
            log_activity(f"Authentication error: {str(e)}", "ERROR")
            return False

    def call(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """
        Make a JSON-RPC call to Odoo.

        Args:
            model (str): Odoo model name (e.g., 'account.move')
            method (str): Method to call (e.g., 'create', 'search_read')
            args (List): Positional arguments
            kwargs (Dict): Keyword arguments

        Returns:
            Any: Result from Odoo API
        """
        if not self.uid:
            if not self.authenticate():
                raise Exception("Authentication failed")

        try:
            response = requests.post(
                f"{self.url}/jsonrpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "service": "object",
                        "method": "execute_kw",
                        "args": [
                            self.db,
                            self.uid,
                            self.password,
                            model,
                            method,
                            args or [],
                            kwargs or {}
                        ]
                    },
                    "id": 1
                },
                timeout=60
            )

            result = response.json()
            if "error" in result:
                error_msg = result["error"].get("data", {}).get("message", str(result["error"]))
                raise Exception(f"Odoo API error: {error_msg}")

            return result.get("result")

        except Exception as e:
            log_activity(f"API call error: {str(e)}", "ERROR")
            raise


# Global Odoo client instance
odoo_client = None


def get_odoo_client() -> OdooClient:
    """Get or create Odoo client instance."""
    global odoo_client

    if not all([ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD]):
        raise Exception("Missing Odoo credentials. Check .env file for ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD")

    if odoo_client is None:
        odoo_client = OdooClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)

    return odoo_client


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available Odoo tools.
    """
    return [
        Tool(
            name="create_invoice",
            description="Create a customer invoice in Odoo. Returns the invoice ID and reference number.",
            inputSchema={
                "type": "object",
                "properties": {
                    "partner_id": {
                        "type": "integer",
                        "description": "Customer/Partner ID in Odoo"
                    },
                    "invoice_lines": {
                        "type": "array",
                        "description": "List of invoice line items",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {
                                    "type": "integer",
                                    "description": "Product ID"
                                },
                                "quantity": {
                                    "type": "number",
                                    "description": "Quantity"
                                },
                                "price_unit": {
                                    "type": "number",
                                    "description": "Unit price"
                                },
                                "name": {
                                    "type": "string",
                                    "description": "Line description"
                                }
                            },
                            "required": ["name", "quantity", "price_unit"]
                        }
                    },
                    "invoice_date": {
                        "type": "string",
                        "description": "Invoice date (YYYY-MM-DD format, optional)"
                    }
                },
                "required": ["partner_id", "invoice_lines"]
            }
        ),
        Tool(
            name="list_invoices",
            description="List and filter customer invoices from Odoo. Returns invoice details including status, amounts, and dates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "partner_id": {
                        "type": "integer",
                        "description": "Filter by customer/partner ID (optional)"
                    },
                    "state": {
                        "type": "string",
                        "description": "Filter by state: draft, posted, cancel (optional)",
                        "enum": ["draft", "posted", "cancel"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of invoices to return (default: 10)",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="record_payment",
            description="Record a payment for an invoice in Odoo. Marks the invoice as paid or partially paid.",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "integer",
                        "description": "Invoice ID to record payment for"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Payment amount"
                    },
                    "payment_date": {
                        "type": "string",
                        "description": "Payment date (YYYY-MM-DD format, optional)"
                    },
                    "journal_id": {
                        "type": "integer",
                        "description": "Payment journal ID (optional, uses default if not provided)"
                    }
                },
                "required": ["invoice_id", "amount"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool execution requests.
    """
    try:
        if name == "create_invoice":
            return await handle_create_invoice(arguments)
        elif name == "list_invoices":
            return await handle_list_invoices(arguments)
        elif name == "record_payment":
            return await handle_record_payment(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
    except Exception as e:
        error_msg = f"Tool execution error: {str(e)}"
        log_activity(f"[{name}] {error_msg}", "ERROR")
        return [TextContent(
            type="text",
            text=error_msg
        )]


async def handle_create_invoice(args: dict) -> list[TextContent]:
    """
    Handle create_invoice tool execution.
    """
    partner_id = args.get("partner_id")
    invoice_lines = args.get("invoice_lines", [])
    invoice_date = args.get("invoice_date")

    if not partner_id or not invoice_lines:
        return [TextContent(
            type="text",
            text="Error: Missing required parameters (partner_id, invoice_lines)"
        )]

    log_activity(f"Creating invoice for partner {partner_id} with {len(invoice_lines)} lines", "INFO")

    try:
        client = get_odoo_client()

        # Prepare invoice data
        invoice_data = {
            "partner_id": partner_id,
            "move_type": "out_invoice",  # Customer invoice
            "invoice_line_ids": [
                (0, 0, {
                    "name": line.get("name"),
                    "quantity": line.get("quantity"),
                    "price_unit": line.get("price_unit"),
                    "product_id": line.get("product_id") if line.get("product_id") else False
                })
                for line in invoice_lines
            ]
        }

        if invoice_date:
            invoice_data["invoice_date"] = invoice_date

        # Create invoice
        invoice_id = client.call("account.move", "create", [[invoice_data]])

        # Get invoice details
        invoice = client.call("account.move", "read", [[invoice_id]], {"fields": ["name", "amount_total", "state"]})

        if invoice:
            invoice_info = invoice[0]
            log_activity(f"Invoice created: {invoice_info['name']} (ID: {invoice_id})", "SUCCESS")

            return [TextContent(
                type="text",
                text=f"✓ Invoice created successfully\n\nInvoice ID: {invoice_id}\nReference: {invoice_info['name']}\nTotal: {invoice_info['amount_total']}\nStatus: {invoice_info['state']}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"✓ Invoice created with ID: {invoice_id}"
            )]

    except Exception as e:
        log_activity(f"Failed to create invoice: {str(e)}", "ERROR")
        return [TextContent(
            type="text",
            text=f"✗ Failed to create invoice: {str(e)}"
        )]


async def handle_list_invoices(args: dict) -> list[TextContent]:
    """
    Handle list_invoices tool execution.
    """
    partner_id = args.get("partner_id")
    state = args.get("state")
    limit = args.get("limit", 10)

    log_activity(f"Listing invoices (partner: {partner_id}, state: {state}, limit: {limit})", "INFO")

    try:
        client = get_odoo_client()

        # Build domain filter
        domain = [("move_type", "=", "out_invoice")]
        if partner_id:
            domain.append(("partner_id", "=", partner_id))
        if state:
            domain.append(("state", "=", state))

        # Search invoices
        invoices = client.call(
            "account.move",
            "search_read",
            [domain],
            {
                "fields": ["name", "partner_id", "invoice_date", "amount_total", "amount_residual", "state"],
                "limit": limit,
                "order": "invoice_date desc"
            }
        )

        if not invoices:
            log_activity("No invoices found", "INFO")
            return [TextContent(
                type="text",
                text="No invoices found matching the criteria."
            )]

        # Format results
        result_text = f"✓ Found {len(invoices)} invoice(s):\n\n"
        for inv in invoices:
            result_text += f"ID: {inv['id']}\n"
            result_text += f"Reference: {inv['name']}\n"
            result_text += f"Customer: {inv['partner_id'][1] if isinstance(inv['partner_id'], list) else inv['partner_id']}\n"
            result_text += f"Date: {inv['invoice_date']}\n"
            result_text += f"Total: {inv['amount_total']}\n"
            result_text += f"Due: {inv['amount_residual']}\n"
            result_text += f"Status: {inv['state']}\n"
            result_text += "-" * 40 + "\n"

        log_activity(f"Listed {len(invoices)} invoices", "SUCCESS")
        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        log_activity(f"Failed to list invoices: {str(e)}", "ERROR")
        return [TextContent(
            type="text",
            text=f"✗ Failed to list invoices: {str(e)}"
        )]


async def handle_record_payment(args: dict) -> list[TextContent]:
    """
    Handle record_payment tool execution.
    """
    invoice_id = args.get("invoice_id")
    amount = args.get("amount")
    payment_date = args.get("payment_date", datetime.now().strftime("%Y-%m-%d"))
    journal_id = args.get("journal_id")

    if not invoice_id or not amount:
        return [TextContent(
            type="text",
            text="Error: Missing required parameters (invoice_id, amount)"
        )]

    log_activity(f"Recording payment of {amount} for invoice {invoice_id}", "INFO")

    try:
        client = get_odoo_client()

        # Get invoice details
        invoice = client.call("account.move", "read", [[invoice_id]], {"fields": ["name", "partner_id", "amount_residual"]})

        if not invoice:
            return [TextContent(
                type="text",
                text=f"✗ Invoice {invoice_id} not found"
            )]

        invoice_info = invoice[0]

        # Prepare payment data
        payment_data = {
            "payment_type": "inbound",
            "partner_type": "customer",
            "partner_id": invoice_info["partner_id"][0] if isinstance(invoice_info["partner_id"], list) else invoice_info["partner_id"],
            "amount": amount,
            "date": payment_date,
            "ref": f"Payment for {invoice_info['name']}"
        }

        if journal_id:
            payment_data["journal_id"] = journal_id

        # Create payment
        payment_id = client.call("account.payment", "create", [[payment_data]])

        # Post payment
        client.call("account.payment", "action_post", [[payment_id]])

        # Reconcile with invoice
        client.call("account.payment", "action_create_payments", [[payment_id]])

        log_activity(f"Payment recorded: {amount} for invoice {invoice_info['name']}", "SUCCESS")

        return [TextContent(
            type="text",
            text=f"✓ Payment recorded successfully\n\nPayment ID: {payment_id}\nInvoice: {invoice_info['name']}\nAmount: {amount}\nDate: {payment_date}\nRemaining: {invoice_info['amount_residual'] - amount}"
        )]

    except Exception as e:
        log_activity(f"Failed to record payment: {str(e)}", "ERROR")
        return [TextContent(
            type="text",
            text=f"✗ Failed to record payment: {str(e)}"
        )]


async def main():
    """
    Main entry point for the MCP server.
    """
    log_activity("Odoo MCP Server starting", "INFO")

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        log_activity("Odoo MCP Server running on stdio", "INFO")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_activity("Odoo MCP Server stopped by user", "INFO")
    except Exception as e:
        log_activity(f"Odoo MCP Server error: {e}", "ERROR")
        sys.exit(1)
