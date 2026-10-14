from __future__ import annotations

from typing import Any, TypedDict


class FulfillmentState(TypedDict, total=False):
    request_text: str
    order_id: str
    user_id: str
    user_roles: list[str]
    user_permissions: list[str]
    allowed: bool
    auth_error: str | None
    exception_type: str | None
    reason_code: str | None
    classification_confidence: float
    evidence: list[dict[str, Any]]
    policy_documents: list[dict[str, Any]]
    root_cause: str | None
    recommendations: list[dict[str, Any]]
    approval_required: bool
    approval_decision: str | None
    approval_status: str | None
    approved_by: str | None
    execution_status: str | None
    status: str
    final_report: dict[str, Any]
    escalation_required: bool
    current_node: str
    correlation_id: str
    errors: list[str]
    order_snapshot: dict[str, Any]
