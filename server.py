import os

from mcp.server.fastmcp import FastMCP

import gmail_client

mcp = FastMCP(
    "HappyRobot MCP Server",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000)),
)


# ──────────────────────────────────────────────
# Gmail Tools
# ──────────────────────────────────────────────

@mcp.tool()
def check_inbox(query: str = "is:unread", max_results: int = 10) -> list[dict]:
    """Fetch recent emails from Gmail. Use query like 'is:unread', 'from:client@email.com', 'subject:commande'."""
    return gmail_client.list_messages(query=query, max_results=max_results)


@mcp.tool()
def get_email_content(email_id: str) -> dict:
    """Get the full content of an email by its ID. Returns sender, subject, body, and labels."""
    return gmail_client.get_message(email_id)


@mcp.tool()
def mark_email_processed(email_id: str) -> dict:
    """Mark an email as read and add the 'PROCESSED' label to avoid re-processing."""
    gmail_client.modify_message(email_id, remove_labels=["UNREAD"])
    return {"email_id": email_id, "status": "marked_as_processed"}


# ──────────────────────────────────────────────
# Client Tools
# ──────────────────────────────────────────────

@mcp.tool()
def lookup_client(name: str = "", email: str = "", phone: str = "") -> dict:
    """Search for an existing client by name, email, or phone number. Returns client info if found, or not_found."""
    # TODO: Replace with real CRM/database lookup
    known_clients = {
        "durand@example.com": {
            "client_id": "CLI-001",
            "name": "Boulangerie Durand",
            "email": "durand@example.com",
            "phone": "+33612345678",
            "address": "12 Rue de la Paix, Paris",
        },
        "martin@example.com": {
            "client_id": "CLI-002",
            "name": "Restaurant Martin",
            "email": "martin@example.com",
            "phone": "+33698765432",
            "address": "45 Avenue des Champs, Lyon",
        },
    }

    for client in known_clients.values():
        if (email and client["email"] == email) or \
           (name and name.lower() in client["name"].lower()) or \
           (phone and client["phone"] == phone):
            return {"found": True, "client": client}

    return {"found": False, "search": {"name": name, "email": email, "phone": phone}}


@mcp.tool()
def create_client(name: str, email: str, phone: str, address: str = "") -> dict:
    """Create a new client record. Use this when a client is not found in the system."""
    # TODO: Replace with real CRM/database insert
    return {
        "client_id": "CLI-NEW-001",
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "status": "created",
    }


# ──────────────────────────────────────────────
# Product / Catalog Tools
# ──────────────────────────────────────────────

@mcp.tool()
def get_product_catalog(search: str = "") -> list[dict]:
    """Search the product catalog. Returns matching products with SKU, name, unit, and price."""
    # TODO: Replace with real catalog/ERP lookup
    catalog = [
        {"sku": "FARINE-T55-25", "name": "Farine T55 25kg", "unit": "sac", "price": 18.50},
        {"sku": "FARINE-T65-25", "name": "Farine T65 25kg", "unit": "sac", "price": 19.00},
        {"sku": "SUCRE-BLANC-10", "name": "Sucre blanc 10kg", "unit": "sac", "price": 12.00},
        {"sku": "BEURRE-PLAQ-10", "name": "Beurre plaque 10kg", "unit": "plaque", "price": 45.00},
        {"sku": "LEVURE-500", "name": "Levure fraîche 500g", "unit": "bloc", "price": 3.50},
        {"sku": "OEUFS-PLAT-30", "name": "Oeufs plateau 30", "unit": "plateau", "price": 8.90},
        {"sku": "CHOCOLAT-NOIR-5", "name": "Chocolat noir 55% 5kg", "unit": "bloc", "price": 32.00},
        {"sku": "LAIT-ENTIER-10", "name": "Lait entier 10L", "unit": "bidon", "price": 11.50},
    ]

    if not search:
        return catalog
    search_lower = search.lower()
    return [p for p in catalog if search_lower in p["name"].lower() or search_lower in p["sku"].lower()]


# ──────────────────────────────────────────────
# Order Tools
# ──────────────────────────────────────────────

@mcp.tool()
def create_order(client_id: str, items: list[dict]) -> dict:
    """Create a new order for a client. Each item should have: sku, quantity, and optionally unit_price.
    Example items: [{"sku": "FARINE-T55-25", "quantity": 10}, {"sku": "SUCRE-BLANC-10", "quantity": 5}]"""
    # TODO: Replace with real order creation in ERP
    total = 0.0
    order_lines = []
    for item in items:
        price = item.get("unit_price", 0)
        line_total = price * item["quantity"]
        total += line_total
        order_lines.append({
            "sku": item["sku"],
            "quantity": item["quantity"],
            "unit_price": price,
            "line_total": line_total,
        })

    return {
        "order_id": "ORD-20260416-001",
        "client_id": client_id,
        "lines": order_lines,
        "total": total,
        "status": "pending_confirmation",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
