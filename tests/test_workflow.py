
from backend.app.agents.workflow import run_investigation


def test_carrier_delay():
    result = run_investigation(
        "ORD-1001",
        "Order has not arrived and shipment is delayed",
    )
    assert result["failure_category"] == "carrier_delay"
    assert result["order_data"]["found"] is True


def test_inventory_shortage():
    result = run_investigation(
        "ORD-1002",
        "Item is out of stock",
    )
    assert result["failure_category"] == "inventory_shortage"


def test_address_issue():
    result = run_investigation(
        "ORD-1003",
        "The delivery address is incorrect",
    )
    assert result["failure_category"] == "address_issue"


def test_warehouse_delay():
    result = run_investigation(
        "ORD-1004",
        "Warehouse has not processed the order",
    )
    assert result["failure_category"] == "warehouse_delay"
    assert result["approval_required"] is True


def test_unknown_order():
    result = run_investigation(
        "ORD-9999",
        "Please investigate this order",
    )
    assert result["order_data"]["found"] is False
    assert result["data_source"] == "simulated_demo_data"
