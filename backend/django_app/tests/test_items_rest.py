"""REST contract for /api/items on the Django service."""
# Core
import pytest

pytestmark = pytest.mark.django_db

ITEM_KEYS = {"id", "name", "country", "status", "revenue", "updatedAt", "owner"}


def test_list_returns_all_ordered_by_updated_desc(client, make_item):
    from django.utils import timezone
    from datetime import timedelta

    older = make_item(name="Old", updated_at=timezone.now() - timedelta(days=10))
    newer = make_item(name="New", updated_at=timezone.now())

    resp = client.get("/api/items")
    assert resp.status_code == 200
    data = resp.json()
    assert [row["name"] for row in data] == ["New", "Old"]
    assert set(data[0].keys()) == ITEM_KEYS
    # revenue must be a JSON number, not a string.
    assert isinstance(data[0]["revenue"], (int, float))


def test_filter_by_country(client, items):
    resp = client.get("/api/items", {"country": "DE"})
    data = resp.json()
    assert len(data) == 2
    assert {row["country"] for row in data} == {"DE"}


def test_filter_by_status(client, items):
    resp = client.get("/api/items", {"status": "pending"})
    data = resp.json()
    assert all(row["status"] == "pending" for row in data)
    assert len(data) == 1


def test_search_is_case_insensitive(client, items):
    resp = client.get("/api/items", {"search": "berlin"})
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Berlin Retail Network"


def test_retrieve_single(client, make_item):
    item = make_item(name="Solo")
    resp = client.get(f"/api/items/{item.id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Solo"


def test_retrieve_missing_returns_404(client):
    resp = client.get("/api/items/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_create_item(client):
    payload = {
        "name": "New Branch",
        "country": "US",
        "status": "active",
        "revenue": 4200.5,
        "owner": "j.doe",
    }
    resp = client.post("/api/items", payload, format="json")
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "New Branch"
    assert body["revenue"] == 4200.5
    assert body["updatedAt"]  # server-stamped


def test_partial_update(client, make_item):
    item = make_item(status="active")
    resp = client.patch(
        f"/api/items/{item.id}", {"status": "inactive"}, format="json"
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "inactive"


def test_delete_item(client, make_item):
    item = make_item()
    resp = client.delete(f"/api/items/{item.id}")
    assert resp.status_code == 204
    assert client.get(f"/api/items/{item.id}").status_code == 404
