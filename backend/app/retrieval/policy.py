
POLICIES = {
    "carrier_delay": {
        "policy_id": "POL-001",
        "title": "Delivery Delay Policy",
        "guidance": (
            "Verify carrier tracking information. "
            "Escalate unresolved delays to the support team. "
            "Do not promise refunds without approval."
        ),
    },
    "inventory_shortage": {
        "policy_id": "POL-002",
        "title": "Inventory Shortage Policy",
        "guidance": (
            "Check stock availability and replenishment. "
            "Offer alternatives only after verification and approval."
        ),
    },
    "address_issue": {
        "policy_id": "POL-003",
        "title": "Address Verification Policy",
        "guidance": (
            "Verify the address with the authorized customer. "
            "Do not modify shipping details without approval."
        ),
    },
    "warehouse_delay": {
        "policy_id": "POL-004",
        "title": "Warehouse Delay Policy",
        "guidance": (
            "Check warehouse processing status. "
            "Escalate delays to the warehouse team."
        ),
    },
}


def retrieve_policy(category: str) -> dict:
    policy = POLICIES.get(category)

    if policy is None:
        return {
            "policy_id": None,
            "title": "Manual Review Required",
            "guidance": (
                "No matching policy found. "
                "Escalate for manual review."
            ),
        }

    return policy
