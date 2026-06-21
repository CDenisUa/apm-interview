"""GraphQL contract for todos on the FastAPI service (over HTTP /graphql)."""


def _gql(client, query, variables=None):
    resp = client.post("/graphql", json={"query": query, "variables": variables or {}})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("errors") is None, body["errors"]
    return body["data"]


def test_query_todos_page(client, todos):
    page = _gql(
        client, "{ todos { total pageSize totalPages items { id title priority } } }"
    )["todos"]
    assert page["total"] == len(todos)
    assert {"id", "title", "priority"} <= set(page["items"][0].keys())


def test_query_todos_filter_priority(client, todos):
    data = _gql(client, '{ todos(priority: "high") { items { priority } } }')
    assert all(t["priority"] == "high" for t in data["todos"]["items"])


def test_query_todos_sort_priority_semantic(client, make_todo):
    make_todo(title="low", priority="low")
    make_todo(title="high", priority="high")
    make_todo(title="medium", priority="medium")
    data = _gql(
        client, '{ todos(sortBy: "priority", order: "asc") { items { title } } }'
    )
    assert [t["title"] for t in data["todos"]["items"]] == ["high", "medium", "low"]


def test_todo_stats(client, todos):
    stats = _gql(
        client,
        "{ todoStats { total active completed overdue byPriority { low medium high } } }",
    )["todoStats"]
    assert stats["total"] == len(todos)
    assert stats["completed"] == 1
    assert stats["overdue"] == 1
    assert stats["byPriority"] == {"low": 1, "medium": 1, "high": 2}


def test_single_todo_and_missing(client, make_todo):
    todo = make_todo(title="Solo")
    data = _gql(
        client, "query($id: ID!) { todo(id: $id) { title } }", {"id": str(todo.id)}
    )
    assert data["todo"]["title"] == "Solo"
    data = _gql(
        client,
        "query($id: ID!) { todo(id: $id) { title } }",
        {"id": "00000000-0000-0000-0000-000000000000"},
    )
    assert data["todo"] is None


def test_create_toggle_delete(client):
    created = _gql(
        client,
        "mutation($input: TodoInput!) { createTodo(input: $input) { id completed } }",
        {"input": {"title": "GraphQL todo", "priority": "high"}},
    )["createTodo"]
    assert created["completed"] is False
    todo_id = created["id"]

    toggled = _gql(
        client, "mutation($id: ID!) { toggleTodo(id: $id) { completed } }", {"id": todo_id}
    )
    assert toggled["toggleTodo"]["completed"] is True

    deleted = _gql(client, "mutation($id: ID!) { deleteTodo(id: $id) }", {"id": todo_id})
    assert deleted["deleteTodo"] is True


def test_bulk_mutations(client, make_todo):
    make_todo(completed=True)
    make_todo(completed=False)
    assert _gql(client, "mutation { markAll(completed: true) }")["markAll"] == 2
    assert _gql(client, "mutation { clearCompleted }")["clearCompleted"] == 2
