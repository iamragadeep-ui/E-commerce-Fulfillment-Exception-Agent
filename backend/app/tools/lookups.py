
def classify_failure(issue_description: str) -> str:
    issue = issue_description.lower()

    if any(word in issue for word in [
        "out of stock", "inventory", "unavailable item"
    ]):
        return "inventory_shortage"

    if any(word in issue for word in [
        "address", "wrong address", "invalid address"
    ]):
        return "address_issue"

    if any(word in issue for word in [
        "warehouse", "not processed", "processing delay"
    ]):
        return "warehouse_delay"

    if any(word in issue for word in [
        "carrier", "shipment delayed", "shipment is delayed",
        "shipping delay", "late delivery", "order has not arrived"
    ]):
        return "carrier_delay"

    return "other"


# Sample records for local development only.
# These are not connected to a real retailer system.
SAMPLE_ORDERS = {
    "ORD-1001": {
        "status": "delayed",
        "inventory_status": "available",
        "warehouse_status": "dispatched",
        "carrier_status": "delay reported",
        "evidence": "Demo record: carrier delay is reported."
    },
    "ORD-1002": {
        "status": "on_hold",
        "inventory_status": "out_of_stock",
        "warehouse_status": "not_started",
        "carrier_status": "not_dispatched",
        "evidence": "Demo record: item is out of stock."
    },
    "ORD-1003": {
        "status": "address_review",
        "inventory_status": "available",
        "warehouse_status": "pending",
        "carrier_status": "not_dispatched",
        "evidence": "Demo record: delivery address needs review."
    },
    "ORD-1004": {
        "status": "processing",
        "inventory_status": "available",
        "warehouse_status": "processing_delay",
        "carrier_status": "not_dispatched",
        "evidence": "Demo record: warehouse processing is delayed."
    }
}


def lookup_order(order_id: str) -> dict:
    record = SAMPLE_ORDERS.get(order_id)

    if record is None:
        return {
            "found": False,
            "message": "No matching order exists in the simulated dataset."
        }

    return {
        "found": True,
        **record
    }
