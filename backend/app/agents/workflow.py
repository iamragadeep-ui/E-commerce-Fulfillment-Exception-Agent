
from backend.app.retrieval.policy import retrieve_policy

from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from backend.app.tools.lookups import (
    classify_failure,
    lookup_order,
)


class InvestigationState(TypedDict, total=False):
    order_id: str
    issue_description: str
    failure_category: str
    order_data: dict
    evidence: list[str]
    recommendation: str
    approval_required: bool
    data_source: str
    policy: dict


def classify_issue(state: InvestigationState) -> dict:
    category = classify_failure(state["issue_description"])

    return {"failure_category": category}


def investigate_order(state: InvestigationState) -> dict:
    order_data = lookup_order(state["order_id"])
    evidence = [
        f"Reported issue: {state['issue_description']}",
    ]

    if order_data.get("found"):
        evidence.append(order_data["evidence"])
    else:
        evidence.append(order_data["message"])

    return {
        "order_data": order_data,
        "evidence": evidence,
        "data_source": "simulated_demo_data",
    }



def get_policy(state: InvestigationState) -> dict:
    policy = retrieve_policy(state["failure_category"])

    return {"policy": policy}


def recommend_action(state: InvestigationState) -> dict:
    category = state["failure_category"]

    recommendations = {
        "inventory_shortage": (
            "Verify stock availability and check replenishment or "
            "an approved alternative before promising a new delivery date."
        ),
        "address_issue": (
            "Ask an authorized support team to verify the delivery "
            "address before dispatch."
        ),
        "warehouse_delay": (
            "Review the warehouse queue and ask the warehouse team "
            "to confirm the processing status."
        ),
        "carrier_delay": (
            "Check the carrier tracking details and request a shipment "
            "status update."
        ),
        "other": (
            "Review the order details and gather more evidence before "
            "choosing a recovery action."
        ),
    }

    return {
        "recommendation": recommendations[category],
        "approval_required": True,
    }



builder = StateGraph(InvestigationState)

builder.add_node("classify_issue", classify_issue)
builder.add_node("investigate_order", investigate_order)
builder.add_node("get_policy", get_policy)
builder.add_node("recommend_action", recommend_action)

builder.add_edge(START, "classify_issue")
builder.add_edge("classify_issue", "investigate_order")
builder.add_edge("investigate_order", "get_policy")
builder.add_edge("get_policy", "recommend_action")
builder.add_edge("recommend_action", END)

investigation_graph = builder.compile()



def run_investigation(order_id: str, issue_description: str) -> dict:
    initial_state: InvestigationState = {
        "order_id": order_id,
        "issue_description": issue_description,
    }

    return investigation_graph.invoke(initial_state)
