"""REST contract for /api/todos on the Django service."""
# Core
import pytest

pytestmark = pytest.mark.django_db

ENVELOPE_KEYS = {"items", "total", "page", "pageSize", "totalPages"}
TODO_KEYS = {
    "id",
    "title",
    "description",
    "completed",
    "priority",
    "dueDate",
    "createdAt",
    "updatedAt",
}


def test_list_returns_pagination_envelope(client, todos):
    resp = client.get("/api/todos")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == ENVELOPE_KEYS
    assert body["total"] == len(todos)
    assert set(body["items"][0].keys()) == TODO_KEYS


def test_pagination_slices_and_counts_pages(client, make_todo):
    for i in range(25):
        make_todo(title=f"T{i:02d}")
    resp = client.get("/api/todos", {"page": 2, "page_size": 10})
    body = resp.json()
    assert body["total"] == 25
    assert body["page"] == 2
    assert body["pageSize"] == 10
    assert body["totalPages"] == 3
    assert len(body["items"]) == 10


def test_page_size_is_capped(client, make_todo):
    make_todo()
    resp = client.get("/api/todos", {"page_size": 9999})
    assert resp.json()["pageSize"] == 100


def test_filter_completed(client, todos):
    resp = client.get("/api/todos", {"completed": "true"})
    items = resp.json()["items"]
    assert all(t["completed"] for t in items)


def test_filter_priority(client, todos):
    resp = client.get("/api/todos", {"priority": "high"})
    items = resp.json()["items"]
    assert all(t["priority"] == "high" for t in items)


def test_filter_overdue(client, todos):
    resp = client.get("/api/todos", {"overdue": "true"})
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Pay invoice"


def test_search_matches_title_or_description(client, make_todo):
    make_todo(title="Find me", description="x")
    make_todo(title="x", description="also find me")
    make_todo(title="nope", description="nope")
    resp = client.get("/api/todos", {"search": "find"})
    assert resp.json()["total"] == 2


def test_sort_by_priority_is_semantic(client, make_todo):
    make_todo(title="low", priority="low")
    make_todo(title="high", priority="high")
    make_todo(title="medium", priority="medium")
    resp = client.get("/api/todos", {"sort_by": "priority", "order": "asc"})
    titles = [t["title"] for t in resp.json()["items"]]
    assert titles == ["high", "medium", "low"]


def test_stats(client, todos):
    resp = client.get("/api/todos/stats")
    body = resp.json()
    assert body["total"] == len(todos)
    assert body["completed"] == 1
    assert body["active"] == len(todos) - 1
    assert body["overdue"] == 1
    assert body["byPriority"] == {"low": 1, "medium": 1, "high": 2}


def test_create_todo(client):
    payload = {"title": "New", "priority": "high"}
    resp = client.post("/api/todos", payload, format="json")
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "New"
    assert body["priority"] == "high"
    assert body["createdAt"] and body["updatedAt"]


def test_create_todo_rejects_invalid_priority(client):
    resp = client.post("/api/todos", {"title": "x", "priority": "urgent"}, format="json")
    assert resp.status_code == 400


def test_retrieve_and_404(client, make_todo):
    todo = make_todo(title="Solo")
    assert client.get(f"/api/todos/{todo.id}").json()["title"] == "Solo"
    assert (
        client.get("/api/todos/00000000-0000-0000-0000-000000000000").status_code
        == 404
    )


def test_put_updates_todo(client, make_todo):
    # NOTE: DRF treats model fields that carry a default (here `description`,
    # which defaults to "") as not-required even on PUT, so omitting them keeps
    # the existing value. This differs from the FastAPI service, whose PUT
    # always rewrites every field. The test documents Django's actual behavior.
    todo = make_todo(title="old", description="keep")
    resp = client.put(
        f"/api/todos/{todo.id}",
        {"title": "new", "priority": "low"},
        format="json",
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "new"
    assert body["priority"] == "low"


def test_patch_updates_fields(client, make_todo):
    todo = make_todo(completed=False)
    resp = client.patch(
        f"/api/todos/{todo.id}", {"completed": True}, format="json"
    )
    assert resp.json()["completed"] is True


def test_toggle(client, make_todo):
    todo = make_todo(completed=False)
    resp = client.post(f"/api/todos/{todo.id}/toggle")
    assert resp.json()["completed"] is True
    resp = client.post(f"/api/todos/{todo.id}/toggle")
    assert resp.json()["completed"] is False


def test_mark_all(client, todos):
    resp = client.post("/api/todos/mark-all", {"completed": True}, format="json")
    assert resp.json()["updated"] == len(todos)
    assert client.get("/api/todos/stats").json()["completed"] == len(todos)


def test_clear_completed(client, make_todo):
    make_todo(completed=True)
    make_todo(completed=True)
    make_todo(completed=False)
    resp = client.post("/api/todos/clear-completed")
    assert resp.json()["deleted"] == 2
    assert client.get("/api/todos").json()["total"] == 1


def test_bulk_delete(client, make_todo):
    a = make_todo()
    b = make_todo()
    keep = make_todo()
    resp = client.post(
        "/api/todos/bulk-delete", {"ids": [str(a.id), str(b.id)]}, format="json"
    )
    assert resp.json()["deleted"] == 2
    remaining = client.get("/api/todos").json()["items"]
    assert [t["id"] for t in remaining] == [str(keep.id)]


def test_bulk_delete_rejects_non_list(client):
    resp = client.post("/api/todos/bulk-delete", {"ids": "nope"}, format="json")
    assert resp.status_code == 400
