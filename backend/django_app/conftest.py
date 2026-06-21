"""
Shared pytest fixtures for the Django service.

The two models this service uses (`business_items`, `todos`) are declared
`managed = False` because the schema is owned by db/init.sql. That means the
normal test-DB setup (which runs migrations) never creates them. We therefore
create those tables explicitly in the throwaway test database via the schema
editor — once per test session.
"""
# Core
from datetime import timedelta
import pytest
from django.db import connection
from django.utils import timezone
from rest_framework.test import APIClient
# Local
from items.models import BusinessItem
from todos.models import Todo


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Create the unmanaged tables in the fresh test database."""
    with django_db_blocker.unblock():
        with connection.schema_editor() as editor:
            editor.create_model(BusinessItem)
            editor.create_model(Todo)
    yield


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def make_item(db):
    """Factory that inserts a BusinessItem row and returns it."""
    def _make(**overrides):
        defaults = {
            "name": "Vienna Logistics Hub",
            "country": "AT",
            "status": "active",
            "revenue": 1250000.00,
            "owner": "a.huber",
            "updated_at": timezone.now(),
        }
        defaults.update(overrides)
        return BusinessItem.objects.create(**defaults)

    return _make


@pytest.fixture
def items(make_item):
    """A small, deterministic set spanning countries/statuses."""
    return [
        make_item(name="Vienna Logistics Hub", country="AT", status="active"),
        make_item(name="Berlin Retail Network", country="DE", status="active"),
        make_item(name="Munich Data Center", country="DE", status="pending"),
        make_item(name="Kyiv Engineering Office", country="UA", status="active"),
    ]


@pytest.fixture
def make_todo(db):
    """Factory that inserts a Todo row and returns it."""
    def _make(**overrides):
        now = timezone.now()
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
        return Todo.objects.create(**defaults)

    return _make


@pytest.fixture
def todos(make_todo):
    """Mixed todos: priorities, completion and one overdue item."""
    past = timezone.now() - timedelta(days=2)
    future = timezone.now() + timedelta(days=2)
    return [
        make_todo(title="Write report", priority="high", due_date=future),
        make_todo(title="Review PR", priority="medium", completed=True),
        make_todo(title="Refactor module", priority="low"),
        make_todo(title="Pay invoice", priority="high", due_date=past),  # overdue
    ]
