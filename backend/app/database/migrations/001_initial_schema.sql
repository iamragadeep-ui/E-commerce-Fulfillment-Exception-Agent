CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id VARCHAR(64) NOT NULL UNIQUE,
    first_name VARCHAR(128) NOT NULL,
    last_name VARCHAR(128) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(64),
    market VARCHAR(64) NOT NULL DEFAULT 'US',
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id VARCHAR(64) NOT NULL UNIQUE,
    customer_id VARCHAR(64) NOT NULL,
    order_status VARCHAR(64) NOT NULL,
    order_total REAL NOT NULL,
    shipping_address TEXT,
    channel VARCHAR(64) NOT NULL DEFAULT 'WEB',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS order_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id VARCHAR(64) NOT NULL,
    sku VARCHAR(64) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    qty INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    status VARCHAR(64) NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku VARCHAR(64) NOT NULL UNIQUE,
    warehouse_code VARCHAR(64) NOT NULL,
    available_qty INTEGER NOT NULL,
    reserved_qty INTEGER NOT NULL,
    in_transit_qty INTEGER NOT NULL,
    status VARCHAR(64) NOT NULL,
    last_updated DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS allocation_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id VARCHAR(64) NOT NULL,
    sku VARCHAR(64) NOT NULL,
    warehouse_code VARCHAR(64) NOT NULL,
    allocated_qty INTEGER NOT NULL,
    status VARCHAR(64) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    warehouse_code VARCHAR(64) NOT NULL,
    status VARCHAR(64) NOT NULL,
    event_ts DATETIME NOT NULL,
    payload JSON
);

CREATE TABLE IF NOT EXISTS carrier_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id VARCHAR(64) NOT NULL,
    carrier VARCHAR(128) NOT NULL,
    tracking_number VARCHAR(128) NOT NULL,
    milestone VARCHAR(128) NOT NULL,
    status VARCHAR(64) NOT NULL,
    event_ts DATETIME NOT NULL,
    location VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS payment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id VARCHAR(64) NOT NULL,
    payment_id VARCHAR(128) NOT NULL,
    amount REAL NOT NULL,
    status VARCHAR(64) NOT NULL,
    auth_code VARCHAR(128),
    last_updated DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS service_policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id VARCHAR(64) NOT NULL UNIQUE,
    policy_type VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    effective_from DATETIME NOT NULL,
    effective_to DATETIME,
    version VARCHAR(32) NOT NULL,
    region VARCHAR(64) NOT NULL,
    requires_approval BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS historical_resolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id VARCHAR(64) NOT NULL,
    resolution_type VARCHAR(128) NOT NULL,
    outcome_code VARCHAR(64) NOT NULL,
    summary TEXT NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS exception_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id VARCHAR(64) NOT NULL UNIQUE,
    order_id VARCHAR(64) NOT NULL,
    exception_type VARCHAR(64) NOT NULL,
    reason_code VARCHAR(64) NOT NULL,
    status VARCHAR(64) NOT NULL,
    priority VARCHAR(32) NOT NULL,
    confidence REAL NOT NULL,
    root_cause TEXT,
    summary TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS recovery_proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id VARCHAR(64) NOT NULL,
    action_code VARCHAR(64) NOT NULL,
    action_name VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    eligibility_score REAL NOT NULL,
    risk_level VARCHAR(32) NOT NULL,
    expected_impact VARCHAR(128),
    policy_eligible BOOLEAN NOT NULL DEFAULT 0,
    requires_approval BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS approval_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id VARCHAR(64) NOT NULL,
    proposal_id INTEGER,
    approver_user VARCHAR(128) NOT NULL,
    approval_status VARCHAR(32) NOT NULL,
    requested_at DATETIME NOT NULL,
    decided_at DATETIME,
    evidence_version VARCHAR(64),
    action_hash VARCHAR(128),
    approval_token VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS action_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id VARCHAR(64) NOT NULL,
    proposal_id INTEGER,
    approval_record_id INTEGER,
    execution_status VARCHAR(32) NOT NULL,
    executed_by VARCHAR(128) NOT NULL,
    executed_at DATETIME NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    result_summary TEXT
);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    actor VARCHAR(128) NOT NULL,
    details_json JSON,
    event_ts DATETIME NOT NULL,
    correlation_id VARCHAR(128)
);
