# Odoo MCP Server

Production-ready MCP server for Odoo ERP integration via JSON-RPC.

## Overview

This MCP server exposes three Odoo operations:

- **create_invoice**: Create customer invoices with line items
- **list_invoices**: List and filter invoices by customer, state, etc.
- **record_payment**: Record payments against invoices

Uses Odoo's JSON-RPC API for seamless integration.

## Features

- ✅ JSON-RPC API integration with Odoo
- ✅ Customer invoice creation with multiple line items
- ✅ Invoice listing with flexible filtering
- ✅ Payment recording and reconciliation
- ✅ Comprehensive error handling and logging
- ✅ Activity logging to vault/logs/odoo.log

## Installation

### 1. Install Dependencies

```bash
pip install mcp requests python-dotenv
```

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# Odoo Configuration
ODOO_URL=https://your-instance.odoo.com
ODOO_DB=your-database-name
ODOO_USERNAME=your-email@example.com
ODOO_PASSWORD=your-api-key-or-password
```

**Important**: For production, use an API key instead of your password. Generate one in Odoo under Settings → Users → API Keys.

### 3. Run the Server

```bash
python mcp/odoo_mcp/server.py
```

## Available Tools

### 1. create_invoice

Create a customer invoice in Odoo.

**Parameters:**
- `partner_id` (integer, required): Customer/Partner ID
- `invoice_lines` (array, required): Invoice line items
  - `name` (string): Line description
  - `quantity` (number): Quantity
  - `price_unit` (number): Unit price
  - `product_id` (integer, optional): Product ID
- `invoice_date` (string, optional): Invoice date (YYYY-MM-DD)

**Example:**
```json
{
  "partner_id": 123,
  "invoice_lines": [
    {
      "name": "Consulting Services",
      "quantity": 10,
      "price_unit": 150.00,
      "product_id": 456
    },
    {
      "name": "Travel Expenses",
      "quantity": 1,
      "price_unit": 250.00
    }
  ],
  "invoice_date": "2026-03-03"
}
```

**Returns:**
```
✓ Invoice created successfully

Invoice ID: 789
Reference: INV/2026/0123
Total: 1750.00
Status: draft
```

### 2. list_invoices

List and filter customer invoices.

**Parameters:**
- `partner_id` (integer, optional): Filter by customer ID
- `state` (string, optional): Filter by state (draft, posted, cancel)
- `limit` (integer, optional): Max results (default: 10)

**Example:**
```json
{
  "partner_id": 123,
  "state": "posted",
  "limit": 5
}
```

**Returns:**
```
✓ Found 2 invoice(s):

ID: 789
Reference: INV/2026/0123
Customer: ABC Corporation
Date: 2026-03-03
Total: 1750.00
Due: 1750.00
Status: posted
----------------------------------------
ID: 788
Reference: INV/2026/0122
Customer: ABC Corporation
Date: 2026-03-01
Total: 500.00
Due: 0.00
Status: posted
```

### 3. record_payment

Record a payment for an invoice.

**Parameters:**
- `invoice_id` (integer, required): Invoice ID
- `amount` (number, required): Payment amount
- `payment_date` (string, optional): Payment date (YYYY-MM-DD)
- `journal_id` (integer, optional): Payment journal ID

**Example:**
```json
{
  "invoice_id": 789,
  "amount": 1750.00,
  "payment_date": "2026-03-05"
}
```

**Returns:**
```
✓ Payment recorded successfully

Payment ID: 456
Invoice: INV/2026/0123
Amount: 1750.00
Date: 2026-03-05
Remaining: 0.00
```

## Integration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo-mcp": {
      "command": "python",
      "args": ["F:/FTEs/Gold Tier/mcp/odoo_mcp/server.py"]
    }
  }
}
```

### Other MCP Clients

Point to: `python F:/FTEs/Gold Tier/mcp/odoo_mcp/server.py`

## Logging

All Odoo operations are logged to:
```
vault/logs/odoo.log
```

Format:
```
[2026-03-03 14:30:45] [INFO] Creating invoice for partner 123 with 2 lines
[2026-03-03 14:30:47] [SUCCESS] Invoice created: INV/2026/0123 (ID: 789)
[2026-03-03 14:31:02] [INFO] Recording payment of 1750.00 for invoice 789
[2026-03-03 14:31:05] [SUCCESS] Payment recorded: 1750.00 for invoice INV/2026/0123
```

## Odoo Setup

### Required Modules

Ensure these Odoo modules are installed:
- **Invoicing** (account)
- **Sales** (sale_management) - optional, for products

### User Permissions

The Odoo user needs these access rights:
- Invoicing: Billing Manager or Billing Administrator
- Payments: Ability to create and post payments

### Finding IDs

**Partner ID:**
```python
# In Odoo, go to Contacts → Select customer → Check URL
# URL will be: /web#id=123&model=res.partner
# Partner ID is 123
```

**Product ID:**
```python
# Go to Products → Select product → Check URL
# URL will be: /web#id=456&model=product.product
# Product ID is 456
```

**Journal ID:**
```python
# Go to Accounting → Configuration → Journals
# Select journal → Check URL
# Journal ID is in the URL
```

## Error Handling

Common errors and solutions:

### Authentication Failed
- Check ODOO_USERNAME and ODOO_PASSWORD in .env
- Verify user has API access enabled
- Use API key instead of password for security

### Model Access Error
- User lacks permissions for invoicing/payments
- Grant "Billing Manager" role in Odoo

### Invalid Partner/Product ID
- Verify IDs exist in Odoo
- Check that records are active (not archived)

### Connection Timeout
- Check ODOO_URL is correct and accessible
- Verify network connectivity
- Increase timeout in server.py if needed

## Security Considerations

1. **API Keys**: Use Odoo API keys, not passwords
2. **HTTPS**: Always use HTTPS URLs for Odoo
3. **Credentials**: Never commit .env file to version control
4. **Permissions**: Grant minimum required permissions
5. **Logs**: Secure vault/logs/odoo.log (may contain sensitive data)

## Troubleshooting

### Test Connection

```python
import requests

response = requests.post(
    "https://your-instance.odoo.com/jsonrpc",
    json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "version"
        },
        "id": 1
    }
)
print(response.json())
```

### Enable Debug Logging

Edit server.py and add:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Testing Tools

Test individual operations:

```bash
# Test authentication
python -c "from mcp.odoo_mcp.server import OdooClient, ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD; client = OdooClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD); print('Auth:', client.authenticate())"
```

### Adding New Tools

1. Add tool definition in `list_tools()`
2. Add handler function `handle_<tool_name>()`
3. Add case in `call_tool()`
4. Update this README

## API Reference

### Odoo Models Used

- `account.move`: Invoices and bills
- `account.payment`: Payments
- `res.partner`: Customers/partners
- `product.product`: Products

### Common Fields

**account.move (Invoice):**
- `partner_id`: Customer ID
- `move_type`: 'out_invoice' for customer invoice
- `invoice_date`: Invoice date
- `amount_total`: Total amount
- `amount_residual`: Amount due
- `state`: draft, posted, cancel

**account.payment:**
- `payment_type`: 'inbound' or 'outbound'
- `partner_type`: 'customer' or 'supplier'
- `amount`: Payment amount
- `date`: Payment date

## License

Part of the Gold Tier FTE automation system.

## Support

For issues:
1. Check vault/logs/odoo.log for detailed errors
2. Verify Odoo credentials and permissions
3. Test connection to Odoo instance
4. Check Odoo version compatibility (tested on v14+)
