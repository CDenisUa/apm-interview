"""Health endpoint for the FastAPI service."""


def test_health_ok(client, items):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "fastapi"
    assert body["database"] is True
    assert body["items"] == len(items)


def test_served_by_header(client):
    resp = client.get("/api/health")
    assert resp.headers["X-Served-By"] == "fastapi"


def test_root_lists_endpoints(client):
    body = client.get("/").json()
    assert body["service"] == "fastapi"
    assert body["endpoints"]["graphql"] == "/graphql"
