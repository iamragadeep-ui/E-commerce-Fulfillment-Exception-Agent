from app.guardrails.safety import GuardrailEngine


def test_guardrail_blocks_missing_permission() -> None:
    engine = GuardrailEngine()

    result = engine.validate_access(
        user_roles=["fulfillment_ops"],
        user_permissions=["read:orders"],
        required_permission="write:recovery",
    )

    assert result.is_allowed is False
    assert "write:recovery" in result.reason


def test_guardrail_allows_approved_sensitive_action() -> None:
    engine = GuardrailEngine()

    result = engine.validate_action(
        order_id="ORD-2001",
        user_roles=["fulfillment_ops", "approver"],
        user_permissions=["read:orders", "write:recovery"],
        approval_status="APPROVED",
    )

    assert result.is_allowed is True
    assert result.metadata["order_id"] == "ORD-2001"
    assert result.metadata["approval_status"] == "APPROVED"
