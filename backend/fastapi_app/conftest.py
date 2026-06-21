"""
Shared pytest fixtures for the FastAPI service.

Tests run against a real Postgres server (the same one docker-compose starts),
but in a DEDICATED throwaway database so they never touch the shared `portal`
data. We point the app's single `SessionLocal` at that test database, which
covers BOTH the REST layer (via the get_db dependency) and the GraphQL
resolvers (which open `SessionLocal()` directly).

Isolation between tests is by truncation rather than transaction rollback,
because each request opens its own session/connection.
"""
# Core
import os
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ProgrammingError
from fastapi.testclient import TestClient
# Local
from app import database
from app.database import Base, SessionLocal
from app.models import BusinessItem, Todo
from app.main import app

TEST_DB_NAME = "fastapi_test"


def _build_urls():
    base = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://portal:portal@db:5432/portal"
    )
    url = make_url(base)
    admin_url = url.set(database="postgres")
    test_url = url.set(database=TEST_DB_NAME)
    return admin_url, test_url


@pytest.fixture(scope="session")
def _test_engine():
    admin_url, test_url = _build_urls()

    # Create the throwaway database (CREATE DATABASE cannot run in a tx block).
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        try:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
        except ProgrammingError:
            pass  # already exists
    admin_engine.dispose()

    engine = create_engine(test_url, pool_pre_ping=True, future=True)
    # Point the app's session factory (and the module engine) at the test DB.
    SessionLocal.configure(bind=engine)
    database.engine = engine

    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_tables(_test_engine):
    """Empty the tables before every test for a clean slate."""
    with _test_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE todos, business_items"))
    yield


@pytest.fixture
def client(_test_engine):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session(_test_engine):
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# --------------------------- data factories ---------------------------------
@pytest.fixture
def make_item(db_session):
    def _make(**overrides):
        defaults = {
            "name": "Vienna Logistics Hub",
            "country": "AT",
            "status": "active",
            "revenue": 1250000.00,
            "owner": "a.huber",
            "updated_at": datetime.now(timezone.utc),
        }
        defaults.update(overrides)
        item = BusinessItem(**defaults)
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        return item

    return _make


@pytest.fixture
def items(make_item):
    return [
        make_item(name="Vienna Logistics Hub", country="AT", status="active"),
        make_item(name="Berlin Retail Network", country="DE", status="active"),
        make_item(name="Munich Data Center", country="DE", status="pending"),
        make_item(name="Kyiv Engineering Office", country="UA", status="active"),
    ]


@pytest.fixture
def make_todo(db_session):
    def _make(**overrides):
        now = datetime.now(timezone.utc)
        defaults = {
            "title": "Sample todo",
            "description": "",
            "completed": False,
            "priority": "medium",
            "due_date": None,
            "created_at": now,
            "updated_at": now,
        }
        defaults.update(overrides)
        todo = Todo(**defaults)
        db_session.add(todo)
        db_session.commit()
        db_session.refresh(todo)
        return todo

    return _make


@pytest.fixture
def todos(make_todo):
    past = datetime.now(timezone.utc) - timedelta(days=2)
    future = datetime.now(timezone.utc) + timedelta(days=2)
    return [
        make_todo(title="Write report", priority="high", due_date=future),
        make_todo(title="Review PR", priority="medium", completed=True),
        make_todo(title="Refactor module", priority="low"),
        make_todo(title="Pay invoice", priority="high", due_date=past),  # overdue
    ]
