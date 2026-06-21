-- =============================================================================
-- Shared database schema for the Business Modernization Portal backend.
--
-- This file is the SINGLE SOURCE OF TRUTH for the `business_items` table.
-- It runs automatically when the Postgres container is first created
-- (mounted into /docker-entrypoint-initdb.d/).
--
-- Both backends connect to THIS schema:
--   * Django  -> ORM model is declared `managed = False` (Django never
--                creates or migrates this table; it only reads/writes it).
--   * FastAPI -> SQLAlchemy maps to the existing table and NEVER calls
--                create_all().
--
-- => No migration conflicts: one schema, two consumers.
-- =============================================================================

-- gen_random_uuid() is available in Postgres 13+ without any extension,
-- but we enable pgcrypto explicitly to be safe across versions.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS business_items (
    id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255)    NOT NULL,
    country     VARCHAR(2)      NOT NULL,         -- AT | DE | US | UA
    status      VARCHAR(20)     NOT NULL,         -- active | inactive | pending
    revenue     NUMERIC(14, 2)  NOT NULL DEFAULT 0,
    owner       VARCHAR(255)    NOT NULL,
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT now()
);

-- Helpful indexes for the filter endpoints (country / status / search).
CREATE INDEX IF NOT EXISTS idx_business_items_country ON business_items (country);
CREATE INDEX IF NOT EXISTS idx_business_items_status  ON business_items (status);
CREATE INDEX IF NOT EXISTS idx_business_items_name    ON business_items (lower(name));

-- -----------------------------------------------------------------------------
-- Seed data (only inserted if the table is empty) so the frontend has
-- something to render immediately when demoing components.
-- -----------------------------------------------------------------------------
INSERT INTO business_items (name, country, status, revenue, owner, updated_at)
SELECT * FROM (VALUES
    ('Vienna Logistics Hub',     'AT', 'active',   1250000.00, 'a.huber',     now() - interval '2 days'),
    ('Berlin Retail Network',    'DE', 'active',   3400000.50, 'm.schmidt',   now() - interval '5 days'),
    ('Munich Data Center',       'DE', 'pending',   890000.00, 'k.weber',     now() - interval '1 day'),
    ('Chicago Distribution',     'US', 'active',   5600000.75, 'j.miller',    now() - interval '8 hours'),
    ('Austin Cloud Services',    'US', 'inactive',  120000.00, 'r.davis',     now() - interval '30 days'),
    ('Kyiv Engineering Office',  'UA', 'active',    760000.00, 'o.kovalenko', now() - interval '3 days'),
    ('Lviv Support Center',      'UA', 'pending',   210000.00, 'i.melnyk',    now() - interval '12 hours'),
    ('Salzburg Tourism Branch',  'AT', 'inactive',   95000.00, 'f.bauer',     now() - interval '60 days')
) AS seed(name, country, status, revenue, owner, updated_at)
WHERE NOT EXISTS (SELECT 1 FROM business_items);


-- =============================================================================
-- TODOS module — large dataset for pagination demos (100,000 rows).
--
-- Same shared-schema rules apply: this table is owned here, Django maps it as
-- `managed = False`, FastAPI maps it via SQLAlchemy without create_all().
-- =============================================================================
CREATE TABLE IF NOT EXISTS todos (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    title       VARCHAR(255) NOT NULL,
    description TEXT         NOT NULL DEFAULT '',
    completed   BOOLEAN      NOT NULL DEFAULT false,
    priority    VARCHAR(10)  NOT NULL DEFAULT 'medium',  -- low | medium | high
    due_date    TIMESTAMPTZ,                             -- nullable
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Indexes that back the filter + ordering used by the paginated endpoints.
CREATE INDEX IF NOT EXISTS idx_todos_completed  ON todos (completed);
CREATE INDEX IF NOT EXISTS idx_todos_priority   ON todos (priority);
CREATE INDEX IF NOT EXISTS idx_todos_title      ON todos (lower(title));
-- Composite index matching the stable pagination order (created_at, id).
CREATE INDEX IF NOT EXISTS idx_todos_created_id ON todos (created_at, id);

-- Generate 100,000 deterministic rows in a single set-based INSERT.
-- (Set-based generation is far faster than row-by-row inserts.)
INSERT INTO todos (title, description, completed, priority, due_date, created_at, updated_at)
SELECT
    'Task #' || g,
    'Auto-generated todo item number ' || g,
    (g % 3 = 0),                                          -- ~33% completed
    (ARRAY['low', 'medium', 'high'])[1 + (g % 3)],        -- rotating priority
    now() + (((g % 120) - 60) || ' days')::interval,      -- due date straddles now (≈half overdue)
    now() - ((g % 365) || ' days')::interval,             -- created_at spread
    now() - ((g % 30) || ' days')::interval               -- updated_at spread
FROM generate_series(1, 100000) AS g
WHERE NOT EXISTS (SELECT 1 FROM todos);
