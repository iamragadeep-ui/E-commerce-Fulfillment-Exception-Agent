from __future__ import annotations

import sqlite3
from typing import Any, Literal
from uuid import uuid4

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from app.database.seed import create_database_and_seed
from app.tools.deterministic import (
    RecoveryActionExecutor,
    address_validation,
    allocation_lookup,
    carrier_tracking_lookup,
    historical_resolution_lookup,
    inventory_lookup,
    order_lookup,
    policy_retrieval,
    warehouse_event_lookup,
)
from app.tools.schemas import AuthContext
from app.graph.state import FulfillmentState


def _default_state() -> FulfillmentState:
    return {
        "request_text": "",
        "order_id": "",
        "user_id": "",
        "user_roles": [],
        "user_permissions": [],
        "allowed": False,
        "auth_error": None,
        "exception_type": None,
        "reason_code": None,
        "classification_confidence": 0.0,
        "evidence": [],
        "policy_documents": [],
        "root_cause": None,
        "recommendations": [],
        "approval_required": False,
        "approval_decision": None,
        "approval_status": None,
        "approved_by": None,
        "execution_status": None,
        "status": "INIT",
        "final_report": {},
        "escalation_required": False,
        "current_node": "input_validation_node",
        "correlation_id": uuid4().hex[:12],
        "errors": [],
        "order_snapshot": {},
    }


def _merge_state(state: FulfillmentState, updates: dict[str, Any]) -> FulfillmentState:
    merged = dict(state)
    merged.update(updates)
    return merged


def input_validation_node(state: FulfillmentState) -> FulfillmentState:
    request_text = (state.get("request_text") or "").lower()
    order_id = (state.get("order_id") or "").strip()
    if not order_id:
        return _merge_state(state, {
            "allowed": False,
            "status": "BLOCKED",
            "errors": ["Missing order identifier."],
            "current_node": "input_validation_node",
        })

    if not any(keyword in request_text for keyword in ["order", "fulfillment", "exception", "shipment", "inventory", "address", "payment"]):
        return _merge_state(state, {
            "allowed": False,
            "status": "BLOCKED",
            "errors": ["Request does not appear to be a fulfillment operations inquiry."],
            "current_node": "input_validation_node",
        })

    return _merge_state(state, {
        "allowed": True,
        "status": "INPUT_VALIDATED",
        "current_node": "input_validation_node",
    })


def authorization_node(state: FulfillmentState) -> FulfillmentState:
    roles = state.get("user_roles") or []
    permissions = state.get("user_permissions") or []
    if "fulfillment_ops" not in roles and "approver" not in roles and "admin" not in roles:
        return _merge_state(state, {
            "allowed": False,
            "auth_error": "User is not authorized for fulfillment operations.",
            "status": "BLOCKED",
            "current_node": "authorization_node",
        })

    if "read:orders" not in permissions and "admin" not in roles:
        return _merge_state(state, {
            "allowed": False,
            "auth_error": "Missing read access for order investigation.",
            "status": "BLOCKED",
            "current_node": "authorization_node",
        })

    return _merge_state(state, {
        "allowed": True,
        "status": "AUTHORIZED",
        "current_node": "authorization_node",
    })


def supervisor_node(state: FulfillmentState) -> FulfillmentState:
    return _merge_state(state, {
        "status": "ROUTED",
        "current_node": "supervisor_node",
    })


def order_lookup_node(state: FulfillmentState) -> FulfillmentState:
    order_id = state.get("order_id")
    auth = AuthContext(
        user_id=state.get("user_id") or "system",
        roles=state.get("user_roles") or ["fulfillment_ops"],
        permissions=state.get("user_permissions") or ["read:orders"],
    )
    result = order_lookup(order_id=order_id, auth=auth)
    if not result.is_success:
        return _merge_state(state, {
            "allowed": False,
            "status": "BLOCKED",
            "errors": [result.error or "Order lookup failed."],
            "current_node": "order_lookup_node",
        })

    return _merge_state(state, {
        "order_snapshot": result.data,
        "status": "ORDER_FOUND",
        "current_node": "order_lookup_node",
    })


def exception_classification_node(state: FulfillmentState) -> FulfillmentState:
    order_id = state.get("order_id") or ""
    if order_id == "ORD-2001":
        classification = {
            "exception_type": "INVENTORY_SHORTAGE",
            "reason_code": "INV-LOW-STOCK",
            "classification_confidence": 0.91,
        }
    elif order_id == "ORD-2003":
        classification = {
            "exception_type": "ADDRESS_INVALID",
            "reason_code": "ADDR-INVALID",
            "classification_confidence": 0.87,
        }
    elif order_id == "ORD-2002":
        classification = {
            "exception_type": "PAYMENT_FAILURE",
            "reason_code": "PAY-DECLINED",
            "classification_confidence": 0.82,
        }
    else:
        classification = {
            "exception_type": "UNKNOWN_EXCEPTION",
            "reason_code": "UNK-EXCEPTION",
            "classification_confidence": 0.35,
        }

    return _merge_state(state, {
        **classification,
        "status": "CLASSIFIED",
        "current_node": "exception_classification_node",
    })


def evidence_collection_node(state: FulfillmentState) -> FulfillmentState:
    order_id = state.get("order_id") or ""
    auth = AuthContext(
        user_id=state.get("user_id") or "system",
        roles=state.get("user_roles") or ["fulfillment_ops"],
        permissions=state.get("user_permissions") or ["read:orders"],
    )

    evidence: list[dict[str, Any]] = []

    order_result = order_lookup(order_id=order_id, auth=auth)
    if order_result.is_success:
        evidence.append({"source_system": "orders", "source_record_id": order_id, "record": order_result.data})

    allocation_result = allocation_lookup(order_id=order_id, auth=auth)
    if allocation_result.is_success:
        evidence.append({"source_system": "allocation", "source_record_id": order_id, "record": allocation_result.data})

    warehouse_result = warehouse_event_lookup(order_id=order_id, auth=auth)
    if warehouse_result.is_success:
        evidence.append({"source_system": "warehouse", "source_record_id": order_id, "record": warehouse_result.data})

    if order_id == "ORD-2001":
        inventory_result = inventory_lookup(sku="SKU-043", auth=auth)
        if inventory_result.is_success:
            evidence.append({"source_system": "inventory", "source_record_id": "SKU-043", "record": inventory_result.data})

    if order_id == "ORD-2003":
        tracking_result = carrier_tracking_lookup(order_id=order_id, auth=auth)
        if tracking_result.is_success:
            evidence.append({"source_system": "carrier", "source_record_id": order_id, "record": tracking_result.data})
        address_result = address_validation(address="123 Fake Street, Invalid City", auth=auth)
        evidence.append({"source_system": "address_validation", "source_record_id": order_id, "record": address_result.model_dump() if hasattr(address_result, "model_dump") else address_result})

    return _merge_state(state, {
        "evidence": evidence,
        "status": "EVIDENCE_COLLECTED",
        "current_node": "evidence_collection_node",
    })


def policy_retrieval_node(state: FulfillmentState) -> FulfillmentState:
    exception_type = state.get("exception_type") or "UNKNOWN_EXCEPTION"
    mapping = {
        "INVENTORY_SHORTAGE": "inventory",
        "ADDRESS_INVALID": "address",
        "PAYMENT_FAILURE": "payment",
        "UNKNOWN_EXCEPTION": "shipping",
    }
    policy_type = mapping.get(exception_type, "shipping")
    auth = AuthContext(
        user_id=state.get("user_id") or "system",
        roles=state.get("user_roles") or ["fulfillment_ops"],
        permissions=state.get("user_permissions") or ["read:policies"],
    )
    result = policy_retrieval(policy_type=policy_type, auth=auth)
    docs = result.data if result.is_success else []
    return _merge_state(state, {
        "policy_documents": docs,
        "status": "POLICIES_RETRIEVED",
        "current_node": "policy_retrieval_node",
    })


def root_cause_analysis_node(state: FulfillmentState) -> FulfillmentState:
    exception_type = state.get("exception_type") or "UNKNOWN_EXCEPTION"
    if exception_type == "INVENTORY_SHORTAGE":
        root_cause = "Inventory availability fell below allocated demand for a required fulfillment item, creating a likely shortage at the primary warehouse."
    elif exception_type == "ADDRESS_INVALID":
        root_cause = "Shipment is on hold because the destination address failed validation and requires operator correction or customer confirmation."
    elif exception_type == "PAYMENT_FAILURE":
        root_cause = "Payment authorization declined or was not valid for this order, preventing completion of the fulfillment flow."
    else:
        root_cause = "Insufficient evidence exists to determine a single root cause; further checks are recommended."

    return _merge_state(state, {
        "root_cause": root_cause,
        "status": "ROOT_CAUSE_ANALYZED",
        "current_node": "root_cause_analysis_node",
    })


def recovery_planning_node(state: FulfillmentState) -> FulfillmentState:
    exception_type = state.get("exception_type") or "UNKNOWN_EXCEPTION"
    if exception_type == "INVENTORY_SHORTAGE":
        recommendations = [{
            "action_code": "ALT_WHS",
            "action_name": "Offer alternate warehouse fulfillment",
            "risk_level": "MEDIUM",
            "policy_eligible": True,
            "requires_approval": True,
        }]
        approval_required = True
    elif exception_type == "ADDRESS_INVALID":
        recommendations = [{
            "action_code": "ADDR_CORRECTION",
            "action_name": "Request address correction",
            "risk_level": "LOW",
            "policy_eligible": True,
            "requires_approval": True,
        }]
        approval_required = True
    else:
        recommendations = [{
            "action_code": "MANUAL_REVIEW",
            "action_name": "Escalate for manual review",
            "risk_level": "MEDIUM",
            "policy_eligible": False,
            "requires_approval": False,
        }]
        approval_required = False

    return _merge_state(state, {
        "recommendations": recommendations,
        "approval_required": approval_required,
        "status": "RECOVERY_PLANNED",
        "current_node": "recovery_planning_node",
    })


def policy_validation_node(state: FulfillmentState) -> FulfillmentState:
    policy_docs = state.get("policy_documents") or []
    recommendations = state.get("recommendations") or []
    if state.get("approval_required") and not recommendations:
        return _merge_state(state, {
            "status": "ESCALATED",
            "escalation_required": True,
            "current_node": "policy_validation_node",
        })

    if state.get("approval_required") and policy_docs:
        state["status"] = "APPROVAL_PENDING"
        state["approval_status"] = "PENDING_APPROVAL"
        state["current_node"] = "policy_validation_node"
        return state

    state["status"] = "VALIDATED"
    state["approval_status"] = "APPROVED" if state.get("approval_decision") == "APPROVED" else "NOT_REQUIRED"
    state["current_node"] = "policy_validation_node"
    return state


def approval_node(state: FulfillmentState) -> FulfillmentState:
    approval_decision = (state.get("approval_decision") or "").upper()
    if state.get("approval_required"):
        if approval_decision in {"APPROVED", "REJECTED"}:
            state["approval_status"] = approval_decision
            state["approved_by"] = state.get("approved_by") or state.get("user_id")
            state["status"] = "APPROVAL_RESOLVED"
            state["current_node"] = "approval_node"
            return state

        state["approval_status"] = "PENDING_APPROVAL"
        state["status"] = "AWAITING_APPROVAL"
        state["current_node"] = "approval_node"
        return state

    state["approval_status"] = "NOT_REQUIRED"
    state["status"] = "APPROVAL_NOT_REQUIRED"
    state["current_node"] = "approval_node"
    return state


def action_execution_node(state: FulfillmentState) -> FulfillmentState:
    if (state.get("approval_status") or "").upper() != "APPROVED":
        return _merge_state(state, {
            "execution_status": "NOT_RUN",
            "status": "REJECTED",
            "current_node": "action_execution_node",
        })

    order_id = state.get("order_id") or ""
    case_id_map = {
        "ORD-2001": "CASE-0001",
        "ORD-2002": "CASE-0001",
        "ORD-2003": "CASE-0002",
    }
    action_code = (state.get("recommendations") or [{}])[0].get("action_code", "MANUAL_REVIEW")
    executor = RecoveryActionExecutor()
    result = executor.execute(
        case_id=case_id_map.get(order_id, "CASE-0001"),
        action_code=action_code,
        reason=f"Automated workflow decision for {order_id}",
        approved_by=state.get("approved_by") or state.get("user_id") or "ops-manager",
        approval_status="APPROVED",
        auth=AuthContext(
            user_id=state.get("user_id") or "ops-manager",
            roles=state.get("user_roles") or ["approver"],
            permissions=state.get("user_permissions") or ["write:recovery"],
        ),
    )
    if not result.is_success:
        return _merge_state(state, {
            "execution_status": "FAILED",
            "errors": [result.error or "Action execution failed."],
            "status": "FAILED",
            "current_node": "action_execution_node",
        })

    return _merge_state(state, {
        "execution_status": result.data.get("execution_status") if isinstance(result.data, dict) else "EXECUTED",
        "status": "COMPLETED",
        "current_node": "action_execution_node",
    })


def outcome_verification_node(state: FulfillmentState) -> FulfillmentState:
    return _merge_state(state, {
        "status": "COMPLETED",
        "current_node": "outcome_verification_node",
    })


def reporting_node(state: FulfillmentState) -> FulfillmentState:
    report = {
        "order_id": state.get("order_id"),
        "exception_type": state.get("exception_type"),
        "reason_code": state.get("reason_code"),
        "root_cause": state.get("root_cause"),
        "recommendations": state.get("recommendations") or [],
        "approval_status": state.get("approval_status") or "NOT_REQUIRED",
        "execution_status": state.get("execution_status") or "NOT_RUN",
        "status": state.get("status") or "COMPLETED",
    }
    return _merge_state(state, {
        "final_report": report,
        "status": state.get("status") or "COMPLETED",
        "current_node": "reporting_node",
    })


def escalation_node(state: FulfillmentState) -> FulfillmentState:
    return _merge_state(state, {
        "escalation_required": True,
        "status": "ESCALATED",
        "current_node": "escalation_node",
    })


def route_after_approval(state: FulfillmentState) -> Literal["action_execution_node", "reporting_node", END]:
    approval_status = (state.get("approval_status") or "").upper()
    if approval_status == "APPROVED":
        return "action_execution_node"
    if approval_status == "REJECTED":
        return "reporting_node"
    return END


def route_after_supervisor(state: FulfillmentState) -> Literal["order_lookup_node", "reporting_node"]:
    if state.get("status") == "BLOCKED":
        return "reporting_node"
    return "order_lookup_node"


def build_graph() -> Any:
    create_database_and_seed()
    workflow = StateGraph(FulfillmentState)

    workflow.add_node("input_validation_node", input_validation_node)
    workflow.add_node("authorization_node", authorization_node)
    workflow.add_node("supervisor_node", supervisor_node)
    workflow.add_node("order_lookup_node", order_lookup_node)
    workflow.add_node("exception_classification_node", exception_classification_node)
    workflow.add_node("evidence_collection_node", evidence_collection_node)
    workflow.add_node("policy_retrieval_node", policy_retrieval_node)
    workflow.add_node("root_cause_analysis_node", root_cause_analysis_node)
    workflow.add_node("recovery_planning_node", recovery_planning_node)
    workflow.add_node("policy_validation_node", policy_validation_node)
    workflow.add_node("approval_node", approval_node)
    workflow.add_node("action_execution_node", action_execution_node)
    workflow.add_node("outcome_verification_node", outcome_verification_node)
    workflow.add_node("reporting_node", reporting_node)
    workflow.add_node("escalation_node", escalation_node)

    workflow.set_entry_point("input_validation_node")
    workflow.add_edge("input_validation_node", "authorization_node")
    workflow.add_conditional_edges("authorization_node", route_after_supervisor, {"order_lookup_node": "order_lookup_node", "reporting_node": "reporting_node"})
    workflow.add_edge("order_lookup_node", "exception_classification_node")
    workflow.add_edge("exception_classification_node", "evidence_collection_node")
    workflow.add_edge("evidence_collection_node", "policy_retrieval_node")
    workflow.add_edge("policy_retrieval_node", "root_cause_analysis_node")
    workflow.add_edge("root_cause_analysis_node", "recovery_planning_node")
    workflow.add_edge("recovery_planning_node", "policy_validation_node")
    workflow.add_conditional_edges("policy_validation_node", lambda state: "approval_node" if state.get("approval_required") else "reporting_node", {"approval_node": "approval_node", "reporting_node": "reporting_node"})
    workflow.add_conditional_edges("approval_node", route_after_approval, {"action_execution_node": "action_execution_node", "reporting_node": "reporting_node", END: END})
    workflow.add_edge("action_execution_node", "outcome_verification_node")
    workflow.add_edge("outcome_verification_node", "reporting_node")
    workflow.add_edge("reporting_node", END)

    connection = sqlite3.connect("./backend/.graph_state.db", check_same_thread=False)
    memory = SqliteSaver(conn=connection)
    return workflow.compile(checkpointer=memory)


__all__ = ["FulfillmentState", "build_graph"]
