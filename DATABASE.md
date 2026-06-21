# Shared Database

One PostgreSQL instance, one table, **two backends** reading and writing it.

## Connection

| Setting  | Value (default)                                        |
| -------- | ------------------------------------------------------ |
| Host     | `localhost` (from host) / `db` (inside compose network)|
| Port     | `5433` from host → `5432` inside the compose network    |
| Database | `portal`                                               |
| User     | `portal`                                               |
| Password | `portal`                                               |

```bash
# Connect with psql from the host (note host port 5433)
psql postgresql://portal:portal@localhost:5433/portal
```

Connection strings used by the services:

```
Django   DATABASE_URL=postgresql://portal:portal@db:5432/portal
FastAPI  DATABASE_URL=postgresql+psycopg://portal:portal@db:5432/portal
```

(The only difference is the SQLAlchemy `+psycopg` driver suffix.)

## Schema: `business_items`

Defined once in [`db/init.sql`](./db/init.sql). This is the **single source of
truth** — neither backend generates it.

| Column       | Type            | Notes                                   |
| ------------ | --------------- | --------------------------------------- |
| `id`         | `UUID` PK       | default `gen_random_uuid()`             |
| `name`       | `VARCHAR(255)`  | not null                                |
| `country`    | `VARCHAR(2)`    | `AT` \| `DE` \| `US` \| `UA`            |
| `status`     | `VARCHAR(20)`   | `active` \| `inactive` \| `pending`     |
| `revenue`    | `NUMERIC(14,2)` | default `0`                             |
| `owner`      | `VARCHAR(255)`  | not null                                |
| `updated_at` | `TIMESTAMPTZ`   | default `now()`                         |

Indexes on `country`, `status`, and `lower(name)` back the filter endpoints.

This maps directly to the frontend `BusinessItem` type:

```ts
export type BusinessItem = {
  id: string;
  name: string;
  country: CountryCode;          // "AT" | "DE" | "US" | "UA"
  status: BusinessItemStatus;    // "active" | "inactive" | "pending"
  revenue: number;
  updatedAt: string;             // ISO string
  owner: string;
};
```

> Note the column `updated_at` is exposed in the API as `updatedAt` (camelCase)
> by **both** backends, so the JSON matches the TS type exactly.

## Table: `todos` (large dataset)

A second shared table built to demo **pagination** against a big dataset.
Same ownership rules (`init.sql` owns it, Django `managed = False`, FastAPI no
`create_all()`).

| Column        | Type            | Notes                               |
| ------------- | --------------- | ----------------------------------- |
| `id`          | `UUID` PK       | default `gen_random_uuid()`         |
| `title`       | `VARCHAR(255)`  | not null                            |
| `description` | `TEXT`          | default `''`                        |
| `completed`   | `BOOLEAN`       | default `false`                     |
| `priority`    | `VARCHAR(10)`   | `low` \| `medium` \| `high`         |
| `due_date`    | `TIMESTAMPTZ`   | nullable                            |
| `created_at`  | `TIMESTAMPTZ`   | default `now()`                     |
| `updated_at`  | `TIMESTAMPTZ`   | default `now()`                     |

Indexes: `completed`, `priority`, `lower(title)`, and a composite
`(created_at, id)` matching the stable pagination order.

## Seed data

- `business_items`: 8 sample rows across all four countries / three statuses.
- `todos`: **100,000 rows** generated in a single set-based `INSERT` using
  `generate_series(1, 100000)` (far faster than row-by-row). Priorities and
  completion rotate deterministically so filters return varied results.

Both seeds are guarded by `WHERE NOT EXISTS (...)`, so they only run on an
empty table.

## Why this design has no conflicts

The risk with two ORMs on one table is **schema ownership**: if both try to
create or migrate it, they fight. This setup removes that risk:

| Concern                | Resolution                                                        |
| ---------------------- | ----------------------------------------------------------------- |
| Who creates the table? | `db/init.sql`, once, on first container init.                     |
| Django migrations      | Model is `managed = False` → Django never touches the schema.     |
| FastAPI / SQLAlchemy   | Never calls `create_all()` → maps onto the existing table only.   |
| Duplicate primary keys | UUIDs generated independently; collisions are practically zero.   |
| `updated_at` drift     | Each backend sets `updated_at = now()` on write — consistent.     |
| Concurrent writes      | Postgres handles transactions/locking; no app-level coordination. |

## Resetting

The schema + seed only run on a **fresh** volume:

```bash
docker compose down -v     # drop the db_data volume
docker compose up --build  # init.sql runs again
```

## Design rationale

The database schema is the single source of truth in an init script, not inside
either ORM. Django maps it as an unmanaged model and FastAPI maps it with
SQLAlchemy without `create_all`. That way two services can share one data layer
without competing migrations — the kind of decoupling that lets you modernize
and replace apps incrementally, sometimes running old and new side by side
against the same data.
