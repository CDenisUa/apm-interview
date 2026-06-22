# Business Modernization Portal

A full local stack — **PostgreSQL + Django + FastAPI + React (Vite)** — wired
together with Docker Compose. Two interchangeable backends sit behind **one
shared database** and serve the **same React frontend**.

Both expose an **identical API contract** — the same REST paths, the same
GraphQL schema, and the same JSON shape — so the frontend never has to care
which one is running.

> Why two backends? Running Django *and* FastAPI side by side proves the
> frontend is decoupled from the backend choice: the same REST + GraphQL
> contract is served by both, so endpoints can move between services — or two
> implementations can run in parallel — without touching the UI.

---

## 🚀 Quick start

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
(includes Docker Compose). Nothing else — Python and Node run inside the
containers.

From the project root, **one command launches everything** — database, both
backends, and the frontend:

```bash
make up
```

(equivalent to `docker compose up --build` if you don't have `make`).

That's it. Once it's running:

| App                | URL                                            |
| ------------------ | ---------------------------------------------- |
| **Frontend**       | <http://localhost:5173>                        |
| **Django** API     | <http://localhost:8001> · docs `/api/docs`     |
| **FastAPI** API    | <http://localhost:8002> · docs `/docs`         |
| **PostgreSQL**     | `localhost:5433` (user/pass/db: `portal`)      |

The database seeds itself on first launch (8 business items + 100k todos via
`db/init.sql`), and **hot reload is on** for all three apps — edit code on your
machine and the running containers pick it up automatically.

### Everyday commands

```bash
make up          # build + start the whole stack (foreground, logs visible)
make up-d        # same, but in the background (detached)
make logs        # follow logs (one service: make logs s=fastapi)
make ps          # show service status
make down        # stop & remove containers (database data is kept)
make reset       # stop & WIPE the database (init.sql re-seeds next start)
make test        # run both backend test suites
make help        # list all targets
```

> No `make`? Every target maps to a plain Docker Compose command — see the
> [Makefile](./Makefile). For example `make up` → `docker compose up --build`,
> `make down` → `docker compose down`.

---

## Architecture

```
                         ┌─────────────────────────┐
                         │  React + TypeScript :5173│
                         │   (Vite dev server)      │
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
| Frontend  | **5173**  | —                | —          | Vite dev server (React + TS)     |
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

## Smoke-test the backends

With the stack running (`make up`), both backends answer the same requests:

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

> **Config is optional.** Sensible defaults are baked into `docker-compose.yml`,
> so you don't need a `.env` file. To override (DB credentials, or which backend
> the frontend targets), copy `cp .env.example .env` and edit it.

---

## Tests

Both backends have a full pytest suite covering REST **and** GraphQL: health,
filtering, pagination, sorting, stats, CRUD, bulk operations and 404/validation
paths. Tests run against the real Postgres service (so the same dialect as
production) in a dedicated throwaway database, leaving the shared `portal` data
untouched.

Run both suites with one command:

```bash
make test                 # or: make test-django / make test-fastapi
```

Under the hood that starts the database and runs each suite in its container:

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

## CI / CD

- **CI** ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) — on every push/PR:
  frontend lint + Vitest tests + build, both backend pytest suites (against
  Postgres), and a docker-compose smoke test.
- **CD to Azure** ([`.github/workflows/cd.yml`](.github/workflows/cd.yml)) — on
  `main` after CI passes: builds prod images → **GHCR**, provisions Azure via
  **Bicep** ([`infra/main.bicep`](infra/main.bicep)), applies the schema, and
  publishes the frontend to **Azure Static Web Apps**. Backends run on **Azure
  Container Apps**; the database is a managed Postgres (**Neon**, since Azure
  free-trial blocks managed PostgreSQL); auth is passwordless **GitHub OIDC**.
  Setup steps: [`docs/AZURE_CD.md`](docs/AZURE_CD.md).

---

## Documentation

- [`API.md`](./API.md) — the shared REST + GraphQL contract, with copy-paste
  `curl` and GraphQL examples for **both** servers.
- [`DATABASE.md`](./DATABASE.md) — schema, seed data, and the shared-DB /
  no-conflict design explained.
- [`docs/AZURE_CD.md`](docs/AZURE_CD.md) — Azure deployment runbook (Bicep,
  Container Apps, Static Web Apps, OIDC).

## Repo layout

```
.
├── Makefile                    # one-command shortcuts (make up / down / test …)
├── docker-compose.yml          # 4 services, shared network
├── .env.example
├── db/
│   └── init.sql                # single source of truth for the schema + seed
├── backend/
│   ├── django_app/             # Django + DRF + strawberry GraphQL
│   │   ├── config/             # settings, urls, wsgi
│   │   ├── items/              # model (managed=False), serializer, views, graphql
│   │   ├── todos/              # todos model, serializer, views, graphql
│   │   ├── Dockerfile          # dev image (runserver)
│   │   ├── Dockerfile.prod     # prod image (gunicorn)
│   │   ├── conftest.py         # pytest fixtures (creates unmanaged tables)
│   │   └── tests/              # REST + GraphQL test suites
│   └── fastapi_app/            # FastAPI + SQLAlchemy + strawberry GraphQL
│       ├── app/                # database, models, schemas, rest, graphql_schema, main
│       ├── Dockerfile          # dev image (uvicorn --reload)
│       ├── Dockerfile.prod     # prod image (uvicorn workers)
│       ├── conftest.py         # pytest fixtures (throwaway test DB)
│       └── tests/              # REST + GraphQL test suites
├── frontend/                   # React + TypeScript (Vite) — clean dev starter
│   ├── src/                    # App, consts/api.ts (backend base URL)
│   ├── Dockerfile              # Vite dev server image
│   └── vite.config.ts
├── infra/
│   └── main.bicep              # Azure infra (Container Apps, Postgres, SWA)
├── .github/workflows/          # ci.yml (tests) + cd.yml (Azure deploy)
├── docs/AZURE_CD.md            # Azure deployment runbook
├── API.md
├── DATABASE.md
└── README.md
```

## Frontend

A clean **React 19 + TypeScript** app scaffolded with **Vite** — the starter
boilerplate is stripped out, leaving a minimal page ready to build on. The only
backend coupling lives in [`frontend/src/consts/api.ts`](./frontend/src/consts/api.ts)
(`API_BASE_URL`), which defaults to Django and is overridable via
`VITE_API_BASE_URL`.

Run it inside the stack (`docker compose up`) at <http://localhost:5173>, or
standalone:

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```
