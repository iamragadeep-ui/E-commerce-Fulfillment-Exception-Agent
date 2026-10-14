from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text

from app.database.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(64), unique=True, nullable=False)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(64), nullable=True)
    market = Column(String(64), nullable=False, default="US")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), unique=True, nullable=False)
    customer_id = Column(String(64), ForeignKey("customers.customer_id"), nullable=False)
    order_status = Column(String(64), nullable=False, default="PENDING")
    order_total = Column(Float, nullable=False, default=0.0)
    shipping_address = Column(Text, nullable=True)
    channel = Column(String(64), nullable=False, default="WEB")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class OrderLine(Base):
    __tablename__ = "order_lines"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), nullable=False)
    sku = Column(String(64), nullable=False)
    product_name = Column(String(255), nullable=False)
    qty = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0.0)
    status = Column(String(64), nullable=False, default="READY")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(64), nullable=False, unique=True)
    warehouse_code = Column(String(64), nullable=False)
    available_qty = Column(Integer, nullable=False, default=0)
    reserved_qty = Column(Integer, nullable=False, default=0)
    in_transit_qty = Column(Integer, nullable=False, default=0)
    status = Column(String(64), nullable=False, default="AVAILABLE")
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class AllocationRecord(Base):
    __tablename__ = "allocation_records"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), nullable=False)
    sku = Column(String(64), nullable=False)
    warehouse_code = Column(String(64), nullable=False)
    allocated_qty = Column(Integer, nullable=False, default=0)
    status = Column(String(64), nullable=False, default="ALLOCATED")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class WarehouseEvent(Base):
    __tablename__ = "warehouse_events"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), nullable=False)
    event_type = Column(String(64), nullable=False)
    warehouse_code = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    event_ts = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    payload = Column(JSON, nullable=True)


class CarrierMilestone(Base):
    __tablename__ = "carrier_milestones"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), nullable=False)
    carrier = Column(String(128), nullable=False)
    tracking_number = Column(String(128), nullable=False)
    milestone = Column(String(128), nullable=False)
    status = Column(String(64), nullable=False)
    event_ts = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    location = Column(String(128), nullable=True)


class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), nullable=False)
    payment_id = Column(String(128), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    status = Column(String(64), nullable=False, default="AUTHORIZED")
    auth_code = Column(String(128), nullable=True)
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class ServicePolicy(Base):
    __tablename__ = "service_policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String(64), unique=True, nullable=False)
    policy_type = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    effective_from = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    effective_to = Column(DateTime(timezone=True), nullable=True)
    version = Column(String(32), nullable=False, default="v1")
    region = Column(String(64), nullable=False, default="US")
    requires_approval = Column(Boolean, nullable=False, default=False)


class HistoricalResolution(Base):
    __tablename__ = "historical_resolutions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), nullable=False)
    resolution_type = Column(String(128), nullable=False)
    outcome_code = Column(String(64), nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class ExceptionCase(Base):
    __tablename__ = "exception_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(64), unique=True, nullable=False)
    order_id = Column(String(64), ForeignKey("orders.order_id"), nullable=False)
    exception_type = Column(String(64), nullable=False)
    reason_code = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, default="OPEN")
    priority = Column(String(32), nullable=False, default="MEDIUM")
    confidence = Column(Float, nullable=False, default=0.0)
    root_cause = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class RecoveryProposal(Base):
    __tablename__ = "recovery_proposals"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("exception_cases.case_id"), nullable=False)
    action_code = Column(String(64), nullable=False)
    action_name = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    eligibility_score = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String(32), nullable=False, default="LOW")
    expected_impact = Column(String(128), nullable=True)
    policy_eligible = Column(Boolean, nullable=False, default=False)
    requires_approval = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("exception_cases.case_id"), nullable=False)
    proposal_id = Column(Integer, ForeignKey("recovery_proposals.id"), nullable=True)
    approver_user = Column(String(128), nullable=False)
    approval_status = Column(String(32), nullable=False, default="PENDING_APPROVAL")
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    evidence_version = Column(String(64), nullable=True)
    action_hash = Column(String(128), nullable=True)
    approval_token = Column(String(128), nullable=True)


class ActionExecution(Base):
    __tablename__ = "action_executions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("exception_cases.case_id"), nullable=False)
    proposal_id = Column(Integer, ForeignKey("recovery_proposals.id"), nullable=True)
    approval_record_id = Column(Integer, ForeignKey("approval_records.id"), nullable=True)
    execution_status = Column(String(32), nullable=False, default="PENDING")
    executed_by = Column(String(128), nullable=False)
    executed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    idempotency_key = Column(String(128), nullable=False, unique=True)
    result_summary = Column(Text, nullable=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("exception_cases.case_id"), nullable=False)
    event_type = Column(String(64), nullable=False)
    actor = Column(String(128), nullable=False)
    details_json = Column(JSON, nullable=True)
    event_ts = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    correlation_id = Column(String(128), nullable=True)
