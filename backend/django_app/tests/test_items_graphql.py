"""GraphQL contract for items on the Django service (executed via the schema)."""
# Core
import pytest
# Local
from config.schema import schema

pytestmark = pytest.mark.django_db


def _run(query, variables=None):
    result = schema.execute_sync(query, variable_values=variables or {})
    assert result.errors is None, result.errors
    return result.data


def test_query_items(items):
    data = _run("{ items { id name country status revenue updatedAt owner } }")
    assert len(data["items"]) == len(items)
    assert {"id", "name", "country"} <= set(data["items"][0].keys())


def test_query_items_filtered(items):
    data = _run('{ items(country: "DE") { country } }')
    assert {row["country"] for row in data["items"]} == {"DE"}


def test_query_single_item(make_item):
    item = make_item(name="Solo")
    data = _run(
        "query($id: ID!) { item(id: $id) { name } }", {"id": str(item.id)}
    )
    assert data["item"]["name"] == "Solo"


def test_query_missing_item_returns_null():
    data = _run(
        "query($id: ID!) { item(id: $id) { name } }",
        {"id": "00000000-0000-0000-0000-000000000000"},
    )
    assert data["item"] is None


def test_create_item_mutation():
    mutation = """
    mutation($input: BusinessItemInput!) {
      createItem(input: $input) { id name revenue }
    }
    """
    variables = {
        "input": {
            "name": "GraphQL Branch",
            "country": "UA",
            "status": "active",
            "revenue": 999.0,
            "owner": "o.k",
        }
    }
    data = _run(mutation, variables)
    assert data["createItem"]["name"] == "GraphQL Branch"
    assert data["createItem"]["revenue"] == 999.0


def test_update_and_delete_item(make_item):
    item = make_item(status="active")
    update = """
    mutation($id: ID!, $input: BusinessItemInput!) {
      updateItem(id: $id, input: $input) { status }
    }
    """
    payload = {
        "id": str(item.id),
        "input": {
            "name": item.name,
            "country": item.country,
            "status": "inactive",
            "revenue": float(item.revenue),
            "owner": item.owner,
        },
    }
    data = _run(update, payload)
    assert data["updateItem"]["status"] == "inactive"

    data = _run(
        "mutation($id: ID!) { deleteItem(id: $id) }", {"id": str(item.id)}
    )
    assert data["deleteItem"] is True
