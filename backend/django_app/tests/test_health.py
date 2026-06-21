"""Health endpoint for the Django service."""
# Core
import pytest

pytestmark = pytest.mark.django_db


def test_health_ok(client, items):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "django"
    assert body["database"] is True
    assert body["items"] == len(items)


def test_root_lists_endpoints(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["service"] == "django"
    assert body["endpoints"]["graphql"] == "/graphql"
