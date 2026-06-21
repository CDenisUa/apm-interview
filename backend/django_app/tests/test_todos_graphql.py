"""GraphQL contract for todos on the Django service."""
# Core
import pytest
# Local
from config.schema import schema

pytestmark = pytest.mark.django_db


def _run(query, variables=None):
    result = schema.execute_sync(query, variable_values=variables or {})
    assert result.errors is None, result.errors
    return result.data


def test_query_todos_page(todos):
    data = _run(
        "{ todos { total pageSize totalPages items { id title priority } } }"
    )
    page = data["todos"]
    assert page["total"] == len(todos)
    assert {"id", "title", "priority"} <= set(page["items"][0].keys())


def test_query_todos_filter_priority(todos):
    data = _run('{ todos(priority: "high") { items { priority } } }')
    assert all(t["priority"] == "high" for t in data["todos"]["items"])


def test_query_todos_sort_priority_semantic(make_todo):
    make_todo(title="low", priority="low")
    make_todo(title="high", priority="high")
    make_todo(title="medium", priority="medium")
    data = _run('{ todos(sortBy: "priority", order: "asc") { items { title } } }')
    assert [t["title"] for t in data["todos"]["items"]] == ["high", "medium", "low"]


def test_todo_stats(todos):
    data = _run(
        "{ todoStats { total active completed overdue byPriority { low medium high } } }"
    )
    stats = data["todoStats"]
    assert stats["total"] == len(todos)
    assert stats["completed"] == 1
    assert stats["overdue"] == 1
    assert stats["byPriority"] == {"low": 1, "medium": 1, "high": 2}


def test_single_todo_and_missing(make_todo):
    todo = make_todo(title="Solo")
    data = _run("query($id: ID!) { todo(id: $id) { title } }", {"id": str(todo.id)})
    assert data["todo"]["title"] == "Solo"
    data = _run(
        "query($id: ID!) { todo(id: $id) { title } }",
        {"id": "00000000-0000-0000-0000-000000000000"},
    )
    assert data["todo"] is None


def test_create_toggle_delete_mutations():
    created = _run(
        """
        mutation($input: TodoInput!) { createTodo(input: $input) { id completed } }
        """,
        {"input": {"title": "GraphQL todo", "priority": "high"}},
    )["createTodo"]
    assert created["completed"] is False
    todo_id = created["id"]

    toggled = _run(
        "mutation($id: ID!) { toggleTodo(id: $id) { completed } }", {"id": todo_id}
    )
    assert toggled["toggleTodo"]["completed"] is True

    deleted = _run("mutation($id: ID!) { deleteTodo(id: $id) }", {"id": todo_id})
    assert deleted["deleteTodo"] is True


def test_bulk_mutations(make_todo):
    make_todo(completed=True)
    make_todo(completed=False)
    marked = _run("mutation { markAll(completed: true) }")
    assert marked["markAll"] == 2
    cleared = _run("mutation { clearCompleted }")
    assert cleared["clearCompleted"] == 2
