from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class GuardrailResult:
    is_allowed: bool
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class GuardrailEngine:
    """Central, explicit guardrail checks for access and approval-sensitive actions."""

    _allowed_roles = {"fulfillment_ops", "approver", "admin"}

    def validate_access(
        self,
        user_roles: Sequence[str],
        user_permissions: Sequence[str],
        required_permission: str | None = None,
        required_role: str | None = None,
    ) -> GuardrailResult:
        role_set = {role.lower() for role in user_roles}
        permission_set = {permission.lower() for permission in user_permissions}

        if not role_set.intersection(self._allowed_roles):
            return GuardrailResult(
                is_allowed=False,
                reason="User is not authorized for fulfillment operations.",
            )

        if required_role and required_role.lower() not in role_set and "admin" not in role_set:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Missing required role: {required_role}.",
            )

        if required_permission and required_permission.lower() not in permission_set and "admin" not in role_set:
            return GuardrailResult(
                is_allowed=False,
                reason=f"Permission denied: missing '{required_permission}'.",
            )

        return GuardrailResult(
            is_allowed=True,
            reason=None,
            metadata={
                "user_roles": list(role_set),
                "user_permissions": list(permission_set),
                "required_permission": required_permission,
                "required_role": required_role,
            },
        )

    def validate_action(
        self,
        *,
        order_id: str,
        user_roles: Sequence[str],
        user_permissions: Sequence[str],
        approval_status: str | None,
        required_permission: str = "write:recovery",
    ) -> GuardrailResult:
        access = self.validate_access(
            user_roles=user_roles,
            user_permissions=user_permissions,
            required_permission=required_permission,
        )

        if not access.is_allowed:
            return access

        normalized_status = (approval_status or "").upper()
        if normalized_status != "APPROVED":
            return GuardrailResult(
                is_allowed=False,
                reason="Action cannot be executed without explicit approval.",
                metadata={
                    "order_id": order_id,
                    "approval_status": normalized_status or "NOT_SET",
                },
            )

        return GuardrailResult(
            is_allowed=True,
            reason=None,
            metadata={
                "order_id": order_id,
                "approval_status": normalized_status,
                "required_permission": required_permission,
            },
        )


__all__ = ["GuardrailEngine", "GuardrailResult"]
