
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_warehouse_exception_includes_policy():
    response = client.post(
        "/exceptions",
        json={
            "order_id": "ORD-1004",
            "issue_description": "Warehouse has not processed the order",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["preliminary_failure_category"] == "warehouse_delay"
    assert data["policy"]["policy_id"] == "POL-004"
    assert data["approval_required"] is True
    assert data["data_source"] == "simulated_demo_data"


def test_inventory_exception():
    response = client.post(
        "/exceptions",
        json={
            "order_id": "ORD-1002",
            "issue_description": "Item is out of stock",
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["preliminary_failure_category"]
        == "inventory_shortage"
    )


def test_empty_order_id_is_rejected():
    response = client.post(
        "/exceptions",
        json={
            "order_id": "",
            "issue_description": "Shipment is delayed",
        },
    )

    assert response.status_code == 422


def test_short_issue_description_is_rejected():
    response = client.post(
        "/exceptions",
        json={
            "order_id": "ORD-1001",
            "issue_description": "Late",
        },
    )

    assert response.status_code == 422
