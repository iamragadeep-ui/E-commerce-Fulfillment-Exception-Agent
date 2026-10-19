
from backend.app.guardrails.rules import (
    validate_exception,
    approval_required,
)


def test_empty_order_id_is_rejected():
    result = validate_exception(
        "",
        "Shipment is delayed",
    )
    assert result["allowed"] is False


def test_empty_issue_is_rejected():
    result = validate_exception(
        "ORD-1001",
        "",
    )
    assert result["allowed"] is False


def test_short_issue_is_rejected():
    result = validate_exception(
        "ORD-1001",
        "Late",
    )
    assert result["allowed"] is False


def test_valid_request_is_allowed():
    result = validate_exception(
        "ORD-1001",
        "Shipment is delayed",
    )
    assert result["allowed"] is True


def test_approval_is_required():
    assert approval_required() is True
