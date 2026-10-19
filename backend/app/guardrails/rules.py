
def validate_exception(
    order_id: str,
    issue_description: str,
) -> dict:
    """Validate an exception request before investigation."""

    if not order_id.strip():
        return {
            "allowed": False,
            "reason": "Order ID cannot be empty.",
        }

    if not issue_description.strip():
        return {
            "allowed": False,
            "reason": "Issue description cannot be empty.",
        }

    if len(issue_description.strip()) < 5:
        return {
            "allowed": False,
            "reason": "Issue description must contain at least 5 characters.",
        }

    return {
        "allowed": True,
        "reason": "Input passed basic validation.",
    }


def approval_required() -> bool:
    """Require human approval before any impactful recovery action."""
    return True
