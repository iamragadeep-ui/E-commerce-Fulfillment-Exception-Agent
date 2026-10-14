from sqlalchemy import text

from app.database.session import SessionLocal, engine
from app.database.seed import create_database_and_seed


def test_database_seed_initializes_expected_tables_and_records() -> None:
    create_database_and_seed()

    with SessionLocal() as session:
        table_names = session.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
            )
        ).scalars().all()

        assert "customers" in table_names
        assert "orders" in table_names
        assert "order_lines" in table_names
        assert "inventory" in table_names
        assert "allocation_records" in table_names
        assert "warehouse_events" in table_names
        assert "carrier_milestones" in table_names
        assert "payment_records" in table_names
        assert "service_policies" in table_names
        assert "historical_resolutions" in table_names
        assert "exception_cases" in table_names
        assert "recovery_proposals" in table_names
        assert "approval_records" in table_names
        assert "action_executions" in table_names
        assert "audit_events" in table_names

        customer_count = session.execute(text("SELECT COUNT(*) FROM customers")).scalar_one()
        order_count = session.execute(text("SELECT COUNT(*) FROM orders")).scalar_one()
        inventory_count = session.execute(text("SELECT COUNT(*) FROM inventory")).scalar_one()

        assert customer_count >= 2
        assert order_count >= 2
        assert inventory_count >= 2


def test_database_engine_uses_sqlite() -> None:
    assert str(engine.url).startswith("sqlite")
