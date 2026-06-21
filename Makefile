# =============================================================================
# Business Modernization Portal — one-command dev shortcuts.
#
# Just run `make` (or `make up`) from the project root to launch EVERYTHING:
# database + Django + FastAPI + React frontend, with hot reload enabled.
# =============================================================================

# `make` with no target runs `up`.
.DEFAULT_GOAL := up

# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------

## up: Build (if needed) and launch the whole stack in the foreground.
up:
	docker compose up --build

## up-d: Same as `up` but detached (runs in the background).
up-d:
	docker compose up --build -d

## down: Stop and remove the containers (database data is kept).
down:
	docker compose down

## reset: Stop everything AND wipe the database volume (init.sql re-seeds next up).
reset:
	docker compose down -v

## restart: Recreate the containers (e.g. after editing docker-compose.yml).
restart:
	docker compose up -d --force-recreate

# -----------------------------------------------------------------------------
# Inspect
# -----------------------------------------------------------------------------

## ps: Show the status of all services.
ps:
	docker compose ps

## logs: Tail logs for all services, or one: `make logs s=fastapi`.
logs:
	docker compose logs -f $(s)

# -----------------------------------------------------------------------------
# Tests (each suite uses its own throwaway database)
# -----------------------------------------------------------------------------

## test: Run both backend test suites.
test: test-django test-fastapi

## test-django: Run the Django (pytest-django) suite.
test-django:
	docker compose up -d db
	docker compose run --rm --no-deps django sh -c "pip install -q -r requirements-dev.txt && python -m pytest -q"

## test-fastapi: Run the FastAPI (pytest) suite.
test-fastapi:
	docker compose up -d db
	docker compose run --rm --no-deps fastapi sh -c "pip install -q -r requirements-dev.txt && python -m pytest -q"

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------

## help: List the available make targets.
help:
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## //'

.PHONY: up up-d down reset restart ps logs test test-django test-fastapi help
