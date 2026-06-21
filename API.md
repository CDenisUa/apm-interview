# API Contract (shared by Django + FastAPI)

Both backends expose the **same** REST paths and the **same** GraphQL schema,
returning the **same** JSON shape. Swap the port to swap the backend:

- Django → `http://localhost:8001`
- FastAPI → `http://localhost:8002`

Every response also carries an `X-Served-By: django|fastapi` header so the
frontend can show which backend answered.

## Resource shape

```jsonc
{
  "id": "0f2c…-uuid",
  "name": "Vienna Logistics Hub",
  "country": "AT",            // AT | DE | US | UA
  "status": "active",         // active | inactive | pending
  "revenue": 1250000.0,       // JSON number, not a string
  "updatedAt": "2026-06-19T10:00:00+00:00",
  "owner": "a.huber"
}
```

---

## REST

| Method   | Path               | Purpose                         | Body                  |
| -------- | ------------------ | ------------------------------- | --------------------- |
| `GET`    | `/api/health`      | Liveness + DB check             | —                     |
| `GET`    | `/api/items`       | List (filterable)               | —                     |
| `GET`    | `/api/items/{id}`  | Single item                     | —                     |
| `POST`   | `/api/items`       | Create (`201`)                  | full item             |
| `PATCH`  | `/api/items/{id}`  | Partial update                  | any subset of fields  |
| `DELETE` | `/api/items/{id}`  | Delete (`204`)                  | —                     |

**Filters** (query params on `GET /api/items`): `country`, `status`, `search`
(case-insensitive match on `name`). They compose:

```
GET /api/items?country=DE&status=active&search=berlin
```

### curl — works against either port

```bash
# List
curl "http://localhost:8001/api/items?country=UA"
curl "http://localhost:8002/api/items?country=UA"

# Create
curl -X POST http://localhost:8002/api/items \
  -H "Content-Type: application/json" \
  -d '{"name":"New Branch","country":"DE","status":"pending","revenue":50000,"owner":"t.test"}'

# Partial update
curl -X PATCH http://localhost:8001/api/items/<id> \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}'

# Delete
curl -X DELETE http://localhost:8002/api/items/<id>
```

FastAPI also ships interactive Swagger docs at
[`http://localhost:8002/docs`](http://localhost:8002/docs).

---

## GraphQL

Endpoint: `/graphql` on both servers. Django serves GraphiQL; FastAPI serves
the strawberry GraphiQL — open either in a browser.

### Schema

```graphql
type BusinessItem {
  id: ID!
  name: String!
  country: String!
  status: String!
  revenue: Float!
  updatedAt: String!
  owner: String!
}

input BusinessItemInput {
  name: String!
  country: String!
  status: String!
  revenue: Float!
  owner: String!
}

type Query {
  items(country: String, status: String, search: String): [BusinessItem!]!
  item(id: ID!): BusinessItem
}

type Mutation {
  createItem(input: BusinessItemInput!): BusinessItem!
  updateItem(id: ID!, input: BusinessItemInput!): BusinessItem
  deleteItem(id: ID!): Boolean!
}
```

### Example query (identical on both)

```graphql
query Items($country: String) {
  items(country: $country, status: "active") {
    id
    name
    country
    revenue
    updatedAt
  }
}
```

### Example mutation

```graphql
mutation Create {
  createItem(
    input: {
      name: "GraphQL Branch"
      country: "US"
      status: "active"
      revenue: 99000
      owner: "g.user"
    }
  ) {
    id
    name
    updatedAt
  }
}
```

### curl a GraphQL query

```bash
curl http://localhost:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ items(country:\"DE\") { id name status revenue } }"}'

# Same query, FastAPI:
curl http://localhost:8002/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ items(country:\"DE\") { id name status revenue } }"}'
```

---

## TODOs — paginated module (100,000 rows)

A second resource built specifically to demo **pagination** over a large
dataset. Same rules: identical REST paths and GraphQL schema on both backends.

### Resource shape

```jsonc
{
  "id": "uuid",
  "title": "Task #42",
  "description": "Auto-generated todo item number 42",
  "completed": false,
  "priority": "medium",          // low | medium | high
  "dueDate": "2026-07-01T10:00:00Z",  // nullable
  "createdAt": "2026-05-01T10:00:00Z",
  "updatedAt": "2026-06-01T10:00:00Z"
}
```

### REST

| Method   | Path                          | Purpose                          |
| -------- | ----------------------------- | -------------------------------- |
| `GET`    | `/api/todos`                  | Paginated list (see below)       |
| `GET`    | `/api/todos/stats`            | Counts summary                   |
| `GET`    | `/api/todos/{id}`             | Single todo                      |
| `POST`   | `/api/todos`                  | Create (`201`)                   |
| `PUT`    | `/api/todos/{id}`             | Full replace                     |
| `PATCH`  | `/api/todos/{id}`             | Partial update                   |
| `POST`   | `/api/todos/{id}/toggle`      | Flip `completed`                 |
| `DELETE` | `/api/todos/{id}`             | Delete (`204`)                   |
| `POST`   | `/api/todos/mark-all`         | `{ "completed": bool }` → updated|
| `POST`   | `/api/todos/clear-completed`  | Delete all completed → deleted   |
| `POST`   | `/api/todos/bulk-delete`      | `{ "ids": [...] }` → deleted     |

> `priority` is validated server-side (`low`/`medium`/`high`) — anything else
> returns `400` (Django) / `422` (FastAPI).

**Pagination, filtering & sorting** (query params on `GET /api/todos`):

| Param       | Default     | Notes                                              |
| ----------- | ----------- | -------------------------------------------------- |
| `page`      | `1`         | 1-based                                            |
| `page_size` | `20`        | max `100`                                          |
| `completed` | —           | `true` / `false`                                   |
| `priority`  | —           | `low` / `medium` / `high`                          |
| `search`    | —           | case-insensitive match on `title` **+ `description`** |
| `overdue`   | —           | `true` → not completed & `due_date` in the past    |
| `sort_by`   | `createdAt` | `createdAt`/`updatedAt`/`dueDate`/`title`/`priority`|
| `order`     | `asc`       | `asc` / `desc`                                     |

> `sort_by=priority` uses **semantic** order (high → medium → low), not
> alphabetical. Results always carry an `id` tiebreaker so pagination is stable.

The `GET /api/todos/stats` response:

```jsonc
{
  "total": 100000,
  "active": 66667,
  "completed": 33333,
  "overdue": 1234,
  "byPriority": { "low": 33334, "medium": 33333, "high": 33333 }
}
```

The list response is a **paginated envelope** (identical on both backends):

```jsonc
{
  "items": [ /* Todo[] */ ],
  "total": 100000,
  "page": 1,
  "pageSize": 20,
  "totalPages": 5000
}
```

```bash
# Page 2, 50 per page, only high-priority unfinished todos
curl "http://localhost:8001/api/todos?page=2&page_size=50&priority=high&completed=false"
curl "http://localhost:8002/api/todos?page=2&page_size=50&priority=high&completed=false"
```

> Ordering is stable (`created_at`, then `id`) so paging over 100k rows never
> skips or repeats items.

### GraphQL

```graphql
type Todo {
  id: ID!
  title: String!
  description: String!
  completed: Boolean!
  priority: String!
  dueDate: String
  createdAt: String!
  updatedAt: String!
}

type TodoPage {
  items: [Todo!]!
  total: Int!
  page: Int!
  pageSize: Int!
  totalPages: Int!
}

type TodoStats {
  total: Int!
  active: Int!
  completed: Int!
  overdue: Int!
  byPriority: PriorityCounts!
}

type Query {
  todos(
    page: Int, pageSize: Int,
    completed: Boolean, priority: String, search: String, overdue: Boolean,
    sortBy: String, order: String
  ): TodoPage!
  todo(id: ID!): Todo
  todoStats: TodoStats!
}

type Mutation {
  createTodo(input: TodoInput!): Todo!
  updateTodo(id: ID!, input: TodoInput!): Todo
  toggleTodo(id: ID!): Todo
  deleteTodo(id: ID!): Boolean!
  markAll(completed: Boolean): Int!
  clearCompleted: Int!
  bulkDeleteTodos(ids: [ID!]!): Int!
}
```

```graphql
query Page {
  todos(page: 1, pageSize: 5, priority: "high") {
    total
    totalPages
    page
    items { id title completed priority dueDate }
  }
}
```

```bash
curl http://localhost:8002/graphql -H "Content-Type: application/json" \
  -d '{"query":"{ todos(page:1,pageSize:3){ total totalPages items{ title priority } } }"}'
```

---

## Using this from the frontend

The contract is stable across backends, so the frontend can flip via an env
variable:

```ts
// shared/config/env.ts
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL // e.g. http://localhost:8001
```

That's the whole point of keeping the contract identical: the React API layer
(`getBusinessItems`, `createBusinessItem`, …) stays unchanged whether it talks
to Django or FastAPI, REST or GraphQL.

### Design rationale

The frontend depends on a typed API contract, not on a specific backend. REST
and GraphQL are kept identical across Django and FastAPI, so the React API layer
is the only place that knows the base URL. That decoupling is what makes a
modernization safe — endpoints can move between services, or two implementations
can run in parallel, without touching the UI.
