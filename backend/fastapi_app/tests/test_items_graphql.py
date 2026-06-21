"""GraphQL contract for items on the FastAPI service (over HTTP /graphql)."""


def _gql(client, query, variables=None):
    resp = client.post("/graphql", json={"query": query, "variables": variables or {}})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("errors") is None, body["errors"]
    return body["data"]


def test_query_items(client, items):
    data = _gql(client, "{ items { id name country status revenue updatedAt owner } }")
    assert len(data["items"]) == len(items)
    assert {"id", "name", "country"} <= set(data["items"][0].keys())


def test_query_items_filtered(client, items):
    data = _gql(client, '{ items(country: "DE") { country } }')
    assert {row["country"] for row in data["items"]} == {"DE"}


def test_query_single_item(client, make_item):
    item = make_item(name="Solo")
    data = _gql(
        client, "query($id: ID!) { item(id: $id) { name } }", {"id": str(item.id)}
    )
    assert data["item"]["name"] == "Solo"


def test_query_missing_item_returns_null(client):
    data = _gql(
        client,
        "query($id: ID!) { item(id: $id) { name } }",
        {"id": "00000000-0000-0000-0000-000000000000"},
    )
    assert data["item"] is None


def test_create_item_mutation(client):
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
    data = _gql(client, mutation, variables)
    assert data["createItem"]["name"] == "GraphQL Branch"
    assert data["createItem"]["revenue"] == 999.0


def test_update_and_delete_item(client, make_item):
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
    assert _gql(client, update, payload)["updateItem"]["status"] == "inactive"
    deleted = _gql(
        client, "mutation($id: ID!) { deleteItem(id: $id) }", {"id": str(item.id)}
    )
    assert deleted["deleteItem"] is True
