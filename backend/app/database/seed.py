from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from app.database.base import Base
from app.database.models import (
    ActionExecution,
    AllocationRecord,
    ApprovalRecord,
    AuditEvent,
    CarrierMilestone,
    Customer,
    ExceptionCase,
    HistoricalResolution,
    Inventory,
    Order,
    OrderLine,
    PaymentRecord,
    RecoveryProposal,
    ServicePolicy,
    WarehouseEvent,
)
from app.database.session import SessionLocal, engine


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_database_and_seed() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        existing_customers = session.execute(text("SELECT COUNT(*) FROM customers")).scalar_one()
        if existing_customers > 0:
            return

        customers = [
            Customer(
                customer_id="CUST-1001",
                first_name="Alicia",
                last_name="Bennett",
                email="alicia.bennett@example.com",
                phone="555-0101",
                market="US",
            ),
            Customer(
                customer_id="CUST-1002",
                first_name="Marcus",
                last_name="Hughes",
                email="marcus.hughes@example.com",
                phone="555-0102",
                market="US",
            ),
            Customer(
                customer_id="CUST-1003",
                first_name="Sofia",
                last_name="Nguyen",
                email="sofia.nguyen@example.com",
                phone="555-0103",
                market="CA",
            ),
        ]
        session.add_all(customers)

        orders = [
            Order(
                order_id="ORD-2001",
                customer_id="CUST-1001",
                order_status="PENDING",
                order_total=149.98,
                shipping_address="123 Main St, Seattle, WA",
                channel="WEB",
                created_at=_utc_now() - timedelta(days=2),
                updated_at=_utc_now() - timedelta(days=2),
            ),
            Order(
                order_id="ORD-2002",
                customer_id="CUST-1002",
                order_status="ALLOCATED",
                order_total=82.41,
                shipping_address="88 River Ave, Austin, TX",
                channel="MOBILE",
                created_at=_utc_now() - timedelta(days=1),
                updated_at=_utc_now() - timedelta(days=1),
            ),
            Order(
                order_id="ORD-2003",
                customer_id="CUST-1003",
                order_status="ADDRESS_REVIEW",
                order_total=230.15,
                shipping_address="14 Maple Lane, Scranton, PA",
                channel="WEB",
                created_at=_utc_now() - timedelta(days=5),
                updated_at=_utc_now() - timedelta(days=1),
            ),
        ]
        session.add_all(orders)

        order_lines = [
            OrderLine(order_id="ORD-2001", sku="SKU-001", product_name="Premium Headphones", qty=1, unit_price=129.99, status="READY"),
            OrderLine(order_id="ORD-2001", sku="SKU-017", product_name="USB-C Cable", qty=1, unit_price=19.99, status="READY"),
            OrderLine(order_id="ORD-2002", sku="SKU-043", product_name="Wireless Mouse", qty=1, unit_price=42.50, status="PACKED"),
            OrderLine(order_id="ORD-2002", sku="SKU-088", product_name="Desk Lamp", qty=1, unit_price=39.91, status="ALLOCATED"),
            OrderLine(order_id="ORD-2003", sku="SKU-120", product_name="Running Shoes", qty=1, unit_price=180.00, status="REVIEW"),
            OrderLine(order_id="ORD-2003", sku="SKU-900", product_name="Socks", qty=1, unit_price=50.15, status="REVIEW"),
        ]
        session.add_all(order_lines)

        inventory_rows = [
            Inventory(sku="SKU-001", warehouse_code="WHS-01", available_qty=3, reserved_qty=2, in_transit_qty=1, status="AVAILABLE", last_updated=_utc_now() - timedelta(hours=2)),
            Inventory(sku="SKU-017", warehouse_code="WHS-01", available_qty=12, reserved_qty=0, in_transit_qty=0, status="AVAILABLE", last_updated=_utc_now() - timedelta(hours=1)),
            Inventory(sku="SKU-043", warehouse_code="WHS-02", available_qty=0, reserved_qty=8, in_transit_qty=0, status="LOW_STOCK", last_updated=_utc_now() - timedelta(hours=6)),
            Inventory(sku="SKU-088", warehouse_code="WHS-02", available_qty=9, reserved_qty=1, in_transit_qty=2, status="AVAILABLE", last_updated=_utc_now() - timedelta(hours=3)),
            Inventory(sku="SKU-120", warehouse_code="WHS-03", available_qty=14, reserved_qty=2, in_transit_qty=1, status="AVAILABLE", last_updated=_utc_now() - timedelta(hours=4)),
        ]
        session.add_all(inventory_rows)

        allocation_rows = [
            AllocationRecord(order_id="ORD-2001", sku="SKU-001", warehouse_code="WHS-01", allocated_qty=1, status="ALLOCATED"),
            AllocationRecord(order_id="ORD-2002", sku="SKU-043", warehouse_code="WHS-02", allocated_qty=0, status="INSUFFICIENT_STOCK"),
            AllocationRecord(order_id="ORD-2003", sku="SKU-120", warehouse_code="WHS-03", allocated_qty=1, status="ALLOCATED"),
        ]
        session.add_all(allocation_rows)

        warehouse_events = [
            WarehouseEvent(order_id="ORD-2001", event_type="PICK_STARTED", warehouse_code="WHS-01", status="IN_PROGRESS", payload={"picker_id": "P-221"}, event_ts=_utc_now() - timedelta(hours=5)),
            WarehouseEvent(order_id="ORD-2002", event_type="PACK_DELAY", warehouse_code="WHS-02", status="DELAYED", payload={"reason": "low stock"}, event_ts=_utc_now() - timedelta(hours=8)),
            WarehouseEvent(order_id="ORD-2003", event_type="PICK_COMPLETE", warehouse_code="WHS-03", status="COMPLETE", payload={"scan_count": 2}, event_ts=_utc_now() - timedelta(hours=3)),
        ]
        session.add_all(warehouse_events)

        carrier_milestones = [
            CarrierMilestone(order_id="ORD-2001", carrier="UPS", tracking_number="1Z-UPS-1001", milestone="IN_TRANSIT", status="ACTIVE", event_ts=_utc_now() - timedelta(hours=12), location="Seattle, WA"),
            CarrierMilestone(order_id="ORD-2002", carrier="FedEx", tracking_number="FDX-2102", milestone="DELAYED", status="DELAYED", event_ts=_utc_now() - timedelta(hours=18), location="Dallas, TX"),
            CarrierMilestone(order_id="ORD-2003", carrier="DHL", tracking_number="DHL-3003", milestone="ADDRESS_HOLD", status="HOLD", event_ts=_utc_now() - timedelta(hours=8), location="Scranton, PA"),
        ]
        session.add_all(carrier_milestones)

        payment_records = [
            PaymentRecord(order_id="ORD-2001", payment_id="PAY-9001", amount=149.98, status="AUTHORIZED", auth_code="AUTH-9001", last_updated=_utc_now() - timedelta(hours=2)),
            PaymentRecord(order_id="ORD-2002", payment_id="PAY-9002", amount=82.41, status="DECLINED", auth_code="AUTH-9002", last_updated=_utc_now() - timedelta(hours=12)),
            PaymentRecord(order_id="ORD-2003", payment_id="PAY-9003", amount=230.15, status="AUTHORIZED", auth_code="AUTH-9003", last_updated=_utc_now() - timedelta(hours=1)),
        ]
        session.add_all(payment_records)

        policies = [
            ServicePolicy(
                policy_id="POL-INV-001",
                policy_type="inventory",
                title="Inventory Allocation Safety Rule",
                content="When available stock drops below the allocated quantity, do not auto-fulfill without a manual check and policy approval.",
                effective_from=_utc_now() - timedelta(days=365),
                version="v1",
                region="US",
                requires_approval=True,
            ),
            ServicePolicy(
                policy_id="POL-SHIP-001",
                policy_type="shipping",
                title="Carrier Delay Escalation",
                content="Carrier delays longer than 24 hours require escalation and customer communication if the parcel is in the final-mile stage.",
                effective_from=_utc_now() - timedelta(days=730),
                version="v2",
                region="US",
                requires_approval=False,
            ),
            ServicePolicy(
                policy_id="POL-ADDR-001",
                policy_type="address",
                title="Address Correction Procedure",
                content="For invalid or incomplete delivery addresses, request customer confirmation before re-routing or reshipping.",
                effective_from=_utc_now() - timedelta(days=365),
                version="v1",
                region="US",
                requires_approval=True,
            ),
            ServicePolicy(
                policy_id="POL-PAY-001",
                policy_type="payment",
                title="Payment Failure Handling",
                content="Payment authorization failures require manual review and cannot be retried automatically without customer consent.",
                effective_from=_utc_now() - timedelta(days=540),
                version="v3",
                region="US",
                requires_approval=True,
            ),
        ]
        session.add_all(policies)

        historical_resolutions = [
            HistoricalResolution(
                order_id="ORD-2001",
                resolution_type="alternative_warehouse",
                outcome_code="RESOLVED",
                summary="Alternative warehouse routing resolved a delayed pick using comparable stock availability.",
            ),
            HistoricalResolution(
                order_id="ORD-2002",
                resolution_type="manual_review",
                outcome_code="ESCALATED",
                summary="Manual inventory review prevented a partial fulfillment that would have violated stock safety rules.",
            ),
        ]
        session.add_all(historical_resolutions)

        exception_cases = [
            ExceptionCase(
                case_id="CASE-0001",
                order_id="ORD-2001",
                exception_type="INVENTORY_SHORTAGE",
                reason_code="INV-LOW-STOCK",
                status="OPEN",
                priority="HIGH",
                confidence=0.91,
                root_cause="Inventory count for SKU-001 fell below allocated demand and no alternate warehouse stock was available.",
                summary="Potential stock shortage detected after allocation failed.",
                created_at=_utc_now() - timedelta(days=1),
                updated_at=_utc_now() - timedelta(hours=2),
            ),
            ExceptionCase(
                case_id="CASE-0002",
                order_id="ORD-2003",
                exception_type="ADDRESS_INVALID",
                reason_code="ADDR-INVALID",
                status="PENDING_APPROVAL",
                priority="MEDIUM",
                confidence=0.87,
                root_cause="Carrier milestone indicates address hold after a failed validation against the delivered address.",
                summary="Address validation exception requires review before reshipment.",
                created_at=_utc_now() - timedelta(days=2),
                updated_at=_utc_now() - timedelta(hours=1),
            ),
        ]
        session.add_all(exception_cases)

        proposals = [
            RecoveryProposal(
                case_id="CASE-0001",
                action_code="ALT_WHS",
                action_name="Offer alternate warehouse fulfillment",
                description="Try alternative warehouse fulfillment if preferred inventory is unavailable in the primary site.",
                eligibility_score=0.94,
                risk_level="MEDIUM",
                expected_impact="Delivery within 2-4 days",
                policy_eligible=True,
                requires_approval=True,
            ),
            RecoveryProposal(
                case_id="CASE-0002",
                action_code="ADDR_CORRECTION",
                action_name="Request address correction",
                description="Pause the shipment and request customer confirmation of the corrected address before requeueing.",
                eligibility_score=0.9,
                risk_level="LOW",
                expected_impact="Avoid failed delivery and rework",
                policy_eligible=True,
                requires_approval=True,
            ),
        ]
        session.add_all(proposals)
        session.flush()

        approval_records = [
            ApprovalRecord(
                case_id="CASE-0001",
                proposal_id=1,
                approver_user="ops-manager-01",
                approval_status="PENDING_APPROVAL",
                requested_at=_utc_now() - timedelta(hours=3),
                evidence_version="v1.4",
                action_hash="hash-case-0001-alt-whs",
                approval_token="token-case-0001-alt-whs",
            ),
            ApprovalRecord(
                case_id="CASE-0002",
                proposal_id=2,
                approver_user="ops-manager-02",
                approval_status="APPROVED",
                decided_at=_utc_now() - timedelta(hours=2),
                requested_at=_utc_now() - timedelta(hours=5),
                evidence_version="v1.2",
                action_hash="hash-case-0002-addr-correction",
                approval_token="token-case-0002-addr-correction",
            ),
        ]
        session.add_all(approval_records)
        session.flush()

        action_executions = [
            ActionExecution(
                case_id="CASE-0002",
                proposal_id=2,
                approval_record_id=2,
                execution_status="EXECUTED",
                executed_by="ops-manager-02",
                executed_at=_utc_now() - timedelta(hours=1),
                idempotency_key="exec-case-0002-addr-correction",
                result_summary="Carrier was notified of address correction hold and shipment was paused.",
            )
        ]
        session.add_all(action_executions)

        audit_events = [
            AuditEvent(
                case_id="CASE-0001",
                event_type="CLASSIFICATION",
                actor="system",
                details_json={"type": "INVENTORY_SHORTAGE", "confidence": 0.91},
                event_ts=_utc_now() - timedelta(hours=4),
                correlation_id="corr-0001",
            ),
            AuditEvent(
                case_id="CASE-0002",
                event_type="APPROVAL",
                actor="ops-manager-02",
                details_json={"status": "APPROVED", "proposal": "ADDR_CORRECTION"},
                event_ts=_utc_now() - timedelta(hours=2),
                correlation_id="corr-0002",
            ),
        ]
        session.add_all(audit_events)

        session.commit()


if __name__ == "__main__":
    create_database_and_seed()
    print("Database initialized and seeded with synthetic fulfillment data.")
