"""REST contract for /api/items on the FastAPI service."""
# Core
from datetime import datetime, timedelta, timezone

ITEM_KEYS = {"id", "name", "country", "status", "revenue", "updatedAt", "owner"}


def test_list_ordered_by_updated_desc(client, make_item):
    make_item(name="Old", updated_at=datetime.now(timezone.utc) - timedelta(days=10))
    make_item(name="New", updated_at=datetime.now(timezone.utc))
    resp = client.get("/api/items")
    assert resp.status_code == 200
    data = resp.json()
    assert [row["name"] for row in data] == ["New", "Old"]
    assert set(data[0].keys()) == ITEM_KEYS
    assert isinstance(data[0]["revenue"], (int, float))


def test_filter_by_country(client, items):
    data = client.get("/api/items", params={"country": "DE"}).json()
    assert len(data) == 2
    assert {row["country"] for row in data} == {"DE"}


def test_filter_by_status(client, items):
    data = client.get("/api/items", params={"status": "pending"}).json()
    assert all(row["status"] == "pending" for row in data)
    assert len(data) == 1


def test_search_case_insensitive(client, items):
    data = client.get("/api/items", params={"search": "berlin"}).json()
    assert len(data) == 1
    assert data[0]["name"] == "Berlin Retail Network"


def test_retrieve_single(client, make_item):
    item = make_item(name="Solo")
    resp = client.get(f"/api/items/{item.id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Solo"


def test_retrieve_missing_404(client):
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
    resp = client.post("/api/items", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "New Branch"
    assert body["revenue"] == 4200.5
    assert body["updatedAt"]


def test_create_item_validation_error(client):
    # `name` and `owner` are required.
    resp = client.post("/api/items", json={"country": "US", "status": "active"})
    assert resp.status_code == 422


def test_partial_update(client, make_item):
    item = make_item(status="active")
    resp = client.patch(f"/api/items/{item.id}", json={"status": "inactive"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "inactive"


def test_update_missing_404(client):
    resp = client.patch(
        "/api/items/00000000-0000-0000-0000-000000000000", json={"status": "x"}
    )
    assert resp.status_code == 404


def test_delete_item(client, make_item):
    item = make_item()
    resp = client.delete(f"/api/items/{item.id}")
    assert resp.status_code == 204
    assert client.get(f"/api/items/{item.id}").status_code == 404
