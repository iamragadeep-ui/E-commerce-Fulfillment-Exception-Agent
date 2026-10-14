import pytest
from sqlalchemy import text

from app.database.session import SessionLocal
from app.tools.deterministic import (
    RecoveryActionExecutor,
    address_validation,
    allocation_lookup,
    carrier_tracking_lookup,
    historical_resolution_lookup,
    inventory_lookup,
    order_lookup,
    policy_retrieval,
)
from app.tools.schemas import AuthContext


@pytest.fixture(autouse=True)
def reset_tool_state() -> None:
    with SessionLocal() as session:
        session.execute(text("DELETE FROM action_executions"))
        session.commit()


def test_order_lookup_returns_order_for_known_order() -> None:
    auth = AuthContext(user_id="ops-analyst", roles=["fulfillment_ops"], permissions=["read:orders"])
    result = order_lookup(order_id="ORD-2001", auth=auth)

    assert result.is_success is True
    assert result.data["order_id"] == "ORD-2001"
    assert result.data["customer_id"] == "CUST-1001"


def test_inventory_lookup_detects_shortage() -> None:
    auth = AuthContext(user_id="ops-analyst", roles=["fulfillment_ops"], permissions=["read:inventory"])
    result = inventory_lookup(sku="SKU-043", auth=auth)

    assert result.is_success is True
    assert result.data["available_qty"] == 0
    assert result.data["status"] == "LOW_STOCK"


def test_address_validation_rejects_invalid_address() -> None:
    auth = AuthContext(user_id="ops-analyst", roles=["fulfillment_ops"], permissions=["read:addresses"])
    result = address_validation(address="123 Fake Street, Invalid City", auth=auth)

    assert result.is_success is False
    assert "invalid" in result.error.lower()


def test_policy_retrieval_returns_eligibility_rules() -> None:
    auth = AuthContext(user_id="ops-analyst", roles=["fulfillment_ops"], permissions=["read:policies"])
    result = policy_retrieval(policy_type="inventory", auth=auth)

    assert result.is_success is True
    assert any(item["policy_type"] == "inventory" for item in result.data)


def test_recovery_action_executor_requires_approval_for_state_change() -> None:
    auth = AuthContext(user_id="ops-manager", roles=["fulfillment_ops", "approver"], permissions=["write:recovery"])
    executor = RecoveryActionExecutor()

    result = executor.execute(
        case_id="CASE-0001",
        action_code="ALT_WHS",
        reason="Alternate warehouse investigation",
        approved_by="ops-manager",
        approval_status="APPROVED",
        auth=auth,
    )

    assert result.is_success is True
    assert result.data["execution_status"] == "EXECUTED"


def test_recovery_action_executor_blocks_duplicate_execution() -> None:
    auth = AuthContext(user_id="ops-manager", roles=["fulfillment_ops", "approver"], permissions=["write:recovery"])
    executor = RecoveryActionExecutor()

    first = executor.execute(
        case_id="CASE-0001",
        action_code="ALT_WHS",
        reason="Alternate warehouse investigation",
        approved_by="ops-manager",
        approval_status="APPROVED",
        auth=auth,
    )
    second = executor.execute(
        case_id="CASE-0001",
        action_code="ALT_WHS",
        reason="Alternate warehouse investigation",
        approved_by="ops-manager",
        approval_status="APPROVED",
        auth=auth,
    )

    assert first.is_success is True
    assert second.is_success is False
    assert "duplicate" in second.error.lower()


def test_historical_resolution_lookup_returns_related_cases() -> None:
    auth = AuthContext(user_id="ops-analyst", roles=["fulfillment_ops"], permissions=["read:history"])
    result = historical_resolution_lookup(order_id="ORD-2001", auth=auth)

    assert result.is_success is True
    assert len(result.data) >= 1
    assert result.data[0]["resolution_type"] in {"alternative_warehouse", "manual_review"}


def test_carrier_tracking_lookup_returns_milestone_data() -> None:
    auth = AuthContext(user_id="ops-analyst", roles=["fulfillment_ops"], permissions=["read:carrier"])
    result = carrier_tracking_lookup(order_id="ORD-2003", auth=auth)

    assert result.is_success is True
    assert result.data["status"] == "HOLD"
