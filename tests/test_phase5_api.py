from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_investigate_inventory_exception_route() -> None:
    response = client.post(
        "/api/v1/exception/investigate",
        json={
            "request_text": "Check ORD-2001 order exception",
            "order_id": "ORD-2001",
            "user_id": "ops-analyst",
            "user_roles": ["fulfillment_ops"],
            "user_permissions": ["read:orders", "read:inventory", "read:policies"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"AWAITING_APPROVAL", "PENDING_APPROVAL"}
    assert payload["exception_type"] == "INVENTORY_SHORTAGE"
    assert payload["approval_required"] is True


def test_approve_recovery_action_route() -> None:
    response = client.post(
        "/api/v1/exception/approve",
        json={
            "request_text": "Approve alternate warehouse fix for ORD-2001",
            "order_id": "ORD-2001",
            "user_id": "ops-manager",
            "user_roles": ["fulfillment_ops", "approver"],
            "user_permissions": [
                "read:orders",
                "read:inventory",
                "read:policies",
                "write:recovery",
            ],
            "approval_decision": "APPROVED",
            "approval_status": "APPROVED",
            "approved_by": "ops-manager",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "COMPLETED"
    assert payload["execution_status"] == "EXECUTED"
    assert payload["final_report"]["order_id"] == "ORD-2001"
