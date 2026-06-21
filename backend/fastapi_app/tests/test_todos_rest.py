"""REST contract for /api/todos on the FastAPI service."""

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


def test_list_pagination_envelope(client, todos):
    body = client.get("/api/todos").json()
    assert set(body.keys()) == ENVELOPE_KEYS
    assert body["total"] == len(todos)
    assert set(body["items"][0].keys()) == TODO_KEYS


def test_pagination_slices(client, make_todo):
    for i in range(25):
        make_todo(title=f"T{i:02d}")
    body = client.get("/api/todos", params={"page": 2, "page_size": 10}).json()
    assert body["total"] == 25
    assert body["page"] == 2
    assert body["pageSize"] == 10
    assert body["totalPages"] == 3
    assert len(body["items"]) == 10


def test_page_size_capped_by_validation(client, make_todo):
    make_todo()
    # FastAPI enforces le=100 at the query-param level -> 422.
    resp = client.get("/api/todos", params={"page_size": 9999})
    assert resp.status_code == 422


def test_filter_completed(client, todos):
    items = client.get("/api/todos", params={"completed": "true"}).json()["items"]
    assert all(t["completed"] for t in items)


def test_filter_priority(client, todos):
    items = client.get("/api/todos", params={"priority": "high"}).json()["items"]
    assert all(t["priority"] == "high" for t in items)


def test_filter_overdue(client, todos):
    items = client.get("/api/todos", params={"overdue": "true"}).json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Pay invoice"


def test_search_matches_title_or_description(client, make_todo):
    make_todo(title="Find me", description="x")
    make_todo(title="x", description="also find me")
    make_todo(title="nope", description="nope")
    body = client.get("/api/todos", params={"search": "find"}).json()
    assert body["total"] == 2


def test_sort_by_priority_semantic(client, make_todo):
    make_todo(title="low", priority="low")
    make_todo(title="high", priority="high")
    make_todo(title="medium", priority="medium")
    items = client.get(
        "/api/todos", params={"sort_by": "priority", "order": "asc"}
    ).json()["items"]
    assert [t["title"] for t in items] == ["high", "medium", "low"]


def test_stats(client, todos):
    body = client.get("/api/todos/stats").json()
    assert body["total"] == len(todos)
    assert body["completed"] == 1
    assert body["active"] == len(todos) - 1
    assert body["overdue"] == 1
    assert body["byPriority"] == {"low": 1, "medium": 1, "high": 2}


def test_create_todo(client):
    resp = client.post("/api/todos", json={"title": "New", "priority": "high"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "New"
    assert body["priority"] == "high"
    assert body["createdAt"] and body["updatedAt"]


def test_create_todo_invalid_priority(client):
    resp = client.post("/api/todos", json={"title": "x", "priority": "urgent"})
    assert resp.status_code == 422


def test_retrieve_and_404(client, make_todo):
    todo = make_todo(title="Solo")
    assert client.get(f"/api/todos/{todo.id}").json()["title"] == "Solo"
    assert (
        client.get("/api/todos/00000000-0000-0000-0000-000000000000").status_code
        == 404
    )


def test_put_replaces(client, make_todo):
    todo = make_todo(title="old", description="keep")
    body = client.put(
        f"/api/todos/{todo.id}", json={"title": "new", "priority": "low"}
    ).json()
    assert body["title"] == "new"
    assert body["description"] == ""


def test_patch_updates(client, make_todo):
    todo = make_todo(completed=False)
    body = client.patch(f"/api/todos/{todo.id}", json={"completed": True}).json()
    assert body["completed"] is True


def test_toggle(client, make_todo):
    todo = make_todo(completed=False)
    assert client.post(f"/api/todos/{todo.id}/toggle").json()["completed"] is True
    assert client.post(f"/api/todos/{todo.id}/toggle").json()["completed"] is False


def test_mark_all(client, todos):
    resp = client.post("/api/todos/mark-all", json={"completed": True})
    assert resp.json()["updated"] == len(todos)
    assert client.get("/api/todos/stats").json()["completed"] == len(todos)


def test_clear_completed(client, make_todo):
    make_todo(completed=True)
    make_todo(completed=True)
    make_todo(completed=False)
    assert client.post("/api/todos/clear-completed").json()["deleted"] == 2
    assert client.get("/api/todos").json()["total"] == 1


def test_bulk_delete(client, make_todo):
    a = make_todo()
    b = make_todo()
    keep = make_todo()
    resp = client.post(
        "/api/todos/bulk-delete", json={"ids": [str(a.id), str(b.id)]}
    )
    assert resp.json()["deleted"] == 2
    remaining = client.get("/api/todos").json()["items"]
    assert [t["id"] for t in remaining] == [str(keep.id)]


def test_static_routes_match_before_dynamic(client, todos):
    # /todos/stats must not be swallowed by /todos/{todo_id}.
    assert client.get("/api/todos/stats").status_code == 200
