from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.database.models import (
    ActionExecution,
    AllocationRecord,
    CarrierMilestone,
    HistoricalResolution,
    Inventory,
    Order,
    PaymentRecord,
    RecoveryProposal,
    ServicePolicy,
    WarehouseEvent,
)
from app.database.session import SessionLocal
from app.tools.schemas import AuthContext, ToolResult


def _require_auth(auth: AuthContext, required_permission: str | None = None) -> ToolResult | None:
    if auth is None or not auth.user_id:
        return ToolResult(is_success=False, error="Authentication required for this tool call.")

    allowed_roles = {"fulfillment_ops", "approver", "admin"}
    if not set(auth.roles).intersection(allowed_roles):
        return ToolResult(is_success=False, error="User is not authorized for fulfillment operations.")

    if required_permission and required_permission not in auth.permissions and "admin" not in auth.roles:
        return ToolResult(is_success=False, error=f"Permission denied: missing '{required_permission}'.")

    return None


def _serialize_model(model: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key in model.__table__.columns.keys():
        value = getattr(model, key)
        if isinstance(value, datetime):
            payload[key] = value.isoformat()
        else:
            payload[key] = value
    return payload


def _serialize_rows(rows: list[Any]) -> list[dict[str, Any]]:
    return [_serialize_model(row) for row in rows]


def order_lookup(order_id: str, auth: AuthContext) -> ToolResult:
    auth_error = _require_auth(auth, "read:orders")
    if auth_error:
        return auth_error

    with SessionLocal() as session:
        order = session.execute(select(Order).where(Order.order_id == order_id)).scalar_one_or_none()
        if order is None:
            return ToolResult(is_success=False, error=f"Order '{order_id}' not found.")
        return ToolResult(is_success=True, data=_serialize_model(order))


def allocation_lookup(order_id: str, auth: AuthContext) -> ToolResult:
    auth_error = _require_auth(auth, "read:allocations")
    if auth_error:
        return auth_error

    with SessionLocal() as session:
        allocations = session.execute(select(AllocationRecord).where(AllocationRecord.order_id == order_id)).scalars().all()
        return ToolResult(is_success=True, data=_serialize_rows(allocations))


def inventory_lookup(sku: str, auth: AuthContext) -> ToolResult:
    auth_error = _require_auth(auth, "read:inventory")
    if auth_error:
        return auth_error

    with SessionLocal() as session:
        inventory = session.execute(select(Inventory).where(Inventory.sku == sku)).scalar_one_or_none()
        if inventory is None:
            return ToolResult(is_success=False, error=f"Inventory row for '{sku}' not found.")
        return ToolResult(is_success=True, data=_serialize_model(inventory))


def warehouse_event_lookup(order_id: str, auth: AuthContext) -> ToolResult:
    auth_error = _require_auth(auth, "read:warehouse")
    if auth_error:
        return auth_error

    with SessionLocal() as session:
        events = session.execute(select(WarehouseEvent).where(WarehouseEvent.order_id == order_id)).scalars().all()
        return ToolResult(is_success=True, data=_serialize_rows(events))


def carrier_tracking_lookup(order_id: str, auth: AuthContext) -> ToolResult:
    auth_error = _require_auth(auth, "read:carrier")
    if auth_error:
        return auth_error

    with SessionLocal() as session:
        milestone = session.execute(select(CarrierMilestone).where(CarrierMilestone.order_id == order_id)).scalar_one_or_none()
        if milestone is None:
            return ToolResult(is_success=False, error=f"No carrier milestone found for '{order_id}'.")
        return ToolResult(is_success=True, data=_serialize_model(milestone))


def payment_status_lookup(order_id: str, auth: AuthContext) -> ToolResult:
    auth_error = _require_auth(auth, "read:payments")
    if auth_error:
        return auth_error

    with SessionLocal() as session:
        payment = session.execute(select(PaymentRecord).where(PaymentRecord.order_id == order_id)).scalar_one_or_none()
        if payment is None:
            return ToolResult(is_success=False, error=f"No payment record found for '{order_id}'.")
        return ToolResult(is_success=True, data=_serialize_model(payment))


def address_validation(address: str, auth: AuthContext) -> ToolResult:
    auth_error = _require_auth(auth, "read:addresses")
    if auth_error:
        return auth_error

    normalized = (address or "").strip()
    invalid_markers = ("fake", "invalid", "example", "test", "po box")
    is_valid = bool(normalized) and not any(marker in normalized.lower() for marker in invalid_markers)

    if not is_valid:
        return ToolResult(
            is_success=False,
            error="Address validation failed: invalid or suspicious address provided.",
            data={"is_valid": False, "normalized_address": normalized, "validation_status": "INVALID"},
        )

    return ToolResult(
        is_success=True,
        data={"is_valid": True, "normalized_address": normalized, "validation_status": "VALID"},
    )


def policy_retrieval(policy_type: str, auth: AuthContext, region: str = "US") -> ToolResult:
    auth_error = _require_auth(auth, "read:policies")
    if auth_error:
        return auth_error

    with SessionLocal() as session:
        rows = session.execute(
            select(ServicePolicy).where(ServicePolicy.policy_type == policy_type, ServicePolicy.region == region)
        ).scalars().all()
        return ToolResult(is_success=True, data=_serialize_rows(rows))


def historical_resolution_lookup(order_id: str, auth: AuthContext) -> ToolResult:
    auth_error = _require_auth(auth, "read:history")
    if auth_error:
        return auth_error

    with SessionLocal() as session:
        rows = session.execute(select(HistoricalResolution).where(HistoricalResolution.order_id == order_id)).scalars().all()
        return ToolResult(is_success=True, data=_serialize_rows(rows))


class RecoveryActionExecutor:
    def execute(
        self,
        case_id: str,
        action_code: str,
        reason: str,
        approved_by: str,
        approval_status: str,
        auth: AuthContext,
    ) -> ToolResult:
        auth_error = _require_auth(auth, "write:recovery")
        if auth_error:
            return auth_error

        if approval_status.upper() != "APPROVED":
            return ToolResult(is_success=False, error="Action cannot be executed without explicit approval.")

        with SessionLocal() as session:
            existing = session.execute(
                select(ActionExecution).where(
                    ActionExecution.case_id == case_id,
                    ActionExecution.idempotency_key == f"{case_id}:{action_code}:{approved_by}",
                )
            ).scalar_one_or_none()
            if existing is not None:
                return ToolResult(
                    is_success=False,
                    error=f"Duplicate execution blocked for case '{case_id}' and action '{action_code}'.",
                    data={
                        "case_id": case_id,
                        "action_code": action_code,
                        "execution_status": existing.execution_status,
                        "result_summary": existing.result_summary,
                        "idempotency_key": existing.idempotency_key,
                    },
                )

            proposal = session.execute(
                select(RecoveryProposal).where(RecoveryProposal.case_id == case_id, RecoveryProposal.action_code == action_code)
            ).scalar_one_or_none()
            if proposal is None:
                return ToolResult(is_success=False, error=f"No recovery proposal found for case '{case_id}' and action '{action_code}'.")

            execution = ActionExecution(
                case_id=case_id,
                proposal_id=proposal.id,
                approval_record_id=None,
                execution_status="EXECUTED",
                executed_by=approved_by,
                executed_at=datetime.now(timezone.utc),
                idempotency_key=f"{case_id}:{action_code}:{approved_by}",
                result_summary=reason,
            )
            session.add(execution)
            session.commit()
            session.refresh(execution)

            return ToolResult(
                is_success=True,
                data={
                    "case_id": case_id,
                    "action_code": action_code,
                    "execution_status": "EXECUTED",
                    "result_summary": reason,
                    "idempotency_key": execution.idempotency_key,
                },
            )


__all__ = [
    "AuthContext",
    "ToolResult",
    "order_lookup",
    "allocation_lookup",
    "inventory_lookup",
    "warehouse_event_lookup",
    "carrier_tracking_lookup",
    "payment_status_lookup",
    "address_validation",
    "policy_retrieval",
    "historical_resolution_lookup",
    "RecoveryActionExecutor",
]
