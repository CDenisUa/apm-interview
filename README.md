# Business Modernization Portal — Backend

Two interchangeable backends behind **one shared database**, built to demo the
same React components against either a **Django** or a **FastAPI** server.

Both expose an **identical API contract** — the same REST paths, the same
GraphQL schema, and the same JSON shape — so the frontend never has to care
which one is running.

> Why two backends? Running Django *and* FastAPI side by side proves the
> frontend is decoupled from the backend choice: the same REST + GraphQL
> contract is served by both, so endpoints can move between services — or two
> implementations can run in parallel — without touching the UI.

---

## Architecture

```
                         ┌─────────────────────────┐
                         │   React + TypeScript     │
                         │   (frontend, added next) │
                         └───────────┬─────────────┘
                                     │  identical REST + GraphQL contract
                 ┌───────────────────┴───────────────────┐
                 ▼                                         ▼
        ┌─────────────────┐                       ┌──────────────────┐
        │  Django  :8001  │                       │  FastAPI  :8002  │
        │  DRF + strawberry│                      │  + strawberry    │
        │  ORM managed=False│                     │  SQLAlchemy      │
        └────────┬────────┘                       └────────┬─────────┘
                 │                                          │
                 └──────────────────┬───────────────────────┘
                                    ▼
                        ┌────────────────────────┐
                        │   PostgreSQL  :5433    │
                        │   table: business_items│
                        │   schema from init.sql │
                        └────────────────────────┘
```

| Service   | Host port | REST base        | GraphQL    | Interactive docs                 |
| --------- | --------- | ---------------- | ---------- | -------------------------------- |
| Django    | **8001**  | `/api/items`     | `/graphql` | Swagger `/api/docs` + GraphiQL   |
| FastAPI   | **8002**  | `/api/items`     | `/graphql` | Swagger `/docs` + GraphiQL       |
| Postgres  | **5433**  | —                | —          | — (5433→5432 inside)             |

> Both backends now expose auto-generated OpenAPI/Swagger UI. FastAPI ships it
> built in; Django gets it via **`drf-spectacular`** (OpenAPI schema at
> `/api/schema`, Swagger UI at `/api/docs`).

---

## How "no conflicts" is guaranteed

This was an explicit requirement. Four concrete decisions make it true:

1. **Distinct ports.** Django `8001`, FastAPI `8002`, Postgres `5432`. Nothing
   overlaps on the host.
2. **One schema owner.** `db/init.sql` is the single source of truth for the
   `business_items` table. It runs once on first DB init.
3. **No competing migrations.**
   - Django model is `managed = False` → Django never creates/alters/drops the
     table, it only reads & writes rows.
   - FastAPI never calls `Base.metadata.create_all()` → SQLAlchemy maps onto
     the existing table only.
4. **No ID coordination.** UUIDs are generated independently (DB default
   `gen_random_uuid()` / `uuid4()`), so concurrent writes from either backend
   can't collide.

See [`DATABASE.md`](./DATABASE.md) for the full reasoning behind the shared
data layer.

---

## Run it

```bash
cp .env.example .env          # optional, sensible defaults are baked in
docker compose up --build
```

Then:

```bash
# Health (note the "service" field differs)
curl http://localhost:8001/api/health
curl http://localhost:8002/api/health

# Same data from both backends
curl http://localhost:8001/api/items
curl http://localhost:8002/api/items

# Paginated TODOs (100k rows) — page 1, 5 per page
curl "http://localhost:8001/api/todos?page=1&page_size=5"
curl "http://localhost:8002/api/todos?page=1&page_size=5"
```

Two resources are available on both backends:
- **`/api/items`** — business items (8 rows), filterable.
- **`/api/todos`** — todos (**100,000 rows**), paginated. See [`API.md`](./API.md).

Stop and reset the database completely:

```bash
docker compose down -v        # -v drops the volume so init.sql re-seeds
```

---

## Tests

Both backends have a full pytest suite covering REST **and** GraphQL: health,
filtering, pagination, sorting, stats, CRUD, bulk operations and 404/validation
paths. Tests run against the real Postgres service (so the same dialect as
production) in a dedicated throwaway database, leaving the shared `portal` data
untouched.

Start the database first, then run each suite in its container:

```bash
docker compose up -d db

# FastAPI suite (creates/uses the `fastapi_test` database)
docker compose run --rm --no-deps fastapi \
  sh -c "pip install -q -r requirements-dev.txt && python -m pytest -q"

# Django suite (pytest-django creates the `test_portal` database)
docker compose run --rm --no-deps django \
  sh -c "pip install -q -r requirements-dev.txt && python -m pytest -q"
```

Test-only dependencies live in each app's `requirements-dev.txt` and are **not**
baked into the production image.

---

## Documentation

- [`API.md`](./API.md) — the shared REST + GraphQL contract, with copy-paste
  `curl` and GraphQL examples for **both** servers.
- [`DATABASE.md`](./DATABASE.md) — schema, seed data, and the shared-DB /
  no-conflict design explained.

## Repo layout

```
.
├── docker-compose.yml          # 3 services, shared network
├── .env.example
├── db/
│   └── init.sql                # single source of truth for the schema + seed
├── backend/
│   ├── django_app/             # Django + DRF + strawberry GraphQL
│   │   ├── config/             # settings, urls, wsgi
│   │   ├── items/              # model (managed=False), serializer, views, graphql
│   │   ├── todos/              # todos model, serializer, views, graphql
│   │   ├── conftest.py         # pytest fixtures (creates unmanaged tables)
│   │   └── tests/              # REST + GraphQL test suites
│   └── fastapi_app/            # FastAPI + SQLAlchemy + strawberry GraphQL
│       ├── app/                # database, models, schemas, rest, graphql_schema, main
│       ├── conftest.py         # pytest fixtures (throwaway test DB)
│       └── tests/              # REST + GraphQL test suites
├── API.md
├── DATABASE.md
└── README.md
```

> **Status:** backend only. The React/TypeScript frontend
> (Business Modernization Portal UI) is the next step and will consume this
> exact contract.
