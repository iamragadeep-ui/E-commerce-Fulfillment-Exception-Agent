from app.graph.workflow import build_graph


def test_workflow_classifies_inventory_shortage_and_waits_for_approval() -> None:
    workflow = build_graph()
    result = workflow.invoke(
        {
            "request_text": "Check ORD-2001 order exception",
            "order_id": "ORD-2001",
            "user_id": "ops-analyst",
            "user_roles": ["fulfillment_ops"],
            "user_permissions": ["read:orders", "read:inventory", "read:policies"],
        },
        config={"configurable": {"thread_id": "wf-inventory-case"}},
    )

    assert result["status"] in {"AWAITING_APPROVAL", "PENDING_APPROVAL"}
    assert result["exception_type"] == "INVENTORY_SHORTAGE"
    assert result["approval_required"] is True


def test_workflow_executes_approved_recovery_action() -> None:
    workflow = build_graph()
    result = workflow.invoke(
        {
            "request_text": "Approve alternate warehouse fix for ORD-2001",
            "order_id": "ORD-2001",
            "user_id": "ops-manager",
            "user_roles": ["fulfillment_ops", "approver"],
            "user_permissions": ["read:orders", "read:inventory", "read:policies", "write:recovery"],
            "approval_decision": "APPROVED",
            "approval_status": "APPROVED",
            "approved_by": "ops-manager",
        },
        config={"configurable": {"thread_id": "wf-approved-exec"}},
    )

    assert result["status"] == "COMPLETED"
    assert result["execution_status"] == "EXECUTED"
    assert result["final_report"]["order_id"] == "ORD-2001"
