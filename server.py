import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "HappyRobot MCP Server",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000)),
)


@mcp.tool()
def get_order_status(order_id: str) -> dict:
    """Look up the current status of a freight order by its ID."""
    # TODO: Replace with real database/API lookup
    return {
        "order_id": order_id,
        "status": "in_transit",
        "origin": "Los Angeles, CA",
        "destination": "Dallas, TX",
        "eta": "2026-04-18T14:00:00Z",
        "carrier": "FastFreight Inc.",
    }


@mcp.tool()
def update_order_status(order_id: str, new_status: str, note: str = "") -> dict:
    """Update the status of a freight order. Valid statuses: pending, dispatched, in_transit, delivered, cancelled."""
    valid_statuses = {"pending", "dispatched", "in_transit", "delivered", "cancelled"}
    if new_status not in valid_statuses:
        return {"error": f"Invalid status. Must be one of: {', '.join(sorted(valid_statuses))}"}
    # TODO: Replace with real database/API update
    return {
        "order_id": order_id,
        "updated_status": new_status,
        "note": note,
        "success": True,
    }


@mcp.tool()
def search_carriers(origin: str, destination: str, equipment_type: str = "dry_van") -> list[dict]:
    """Search for available carriers on a lane. Equipment types: dry_van, reefer, flatbed, step_deck."""
    # TODO: Replace with real carrier search
    return [
        {
            "carrier_name": "FastFreight Inc.",
            "mc_number": "MC-123456",
            "rate": 2850.00,
            "equipment": equipment_type,
            "transit_days": 2,
            "origin": origin,
            "destination": destination,
        },
        {
            "carrier_name": "QuickHaul Logistics",
            "mc_number": "MC-789012",
            "rate": 3100.00,
            "equipment": equipment_type,
            "transit_days": 3,
            "origin": origin,
            "destination": destination,
        },
    ]


@mcp.tool()
def create_load(
    origin: str,
    destination: str,
    pickup_date: str,
    delivery_date: str,
    weight_lbs: float,
    commodity: str,
    equipment_type: str = "dry_van",
) -> dict:
    """Create a new load/shipment."""
    # TODO: Replace with real load creation logic
    return {
        "load_id": "LD-20260416-001",
        "origin": origin,
        "destination": destination,
        "pickup_date": pickup_date,
        "delivery_date": delivery_date,
        "weight_lbs": weight_lbs,
        "commodity": commodity,
        "equipment_type": equipment_type,
        "status": "pending",
    }


@mcp.tool()
def get_rate_quote(origin: str, destination: str, equipment_type: str = "dry_van") -> dict:
    """Get a rate quote for a lane."""
    # TODO: Replace with real rate engine
    return {
        "origin": origin,
        "destination": destination,
        "equipment_type": equipment_type,
        "estimated_rate": 2950.00,
        "rate_per_mile": 2.45,
        "estimated_miles": 1204,
        "currency": "USD",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
