# Stratum — Professional PostgreSQL Workspace

> The professional PostgreSQL workspace for teams who take data seriously.

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.12+ (for secret generation)
- Node.js 20+ (for local frontend dev without Docker)

### 1. Generate secrets

```bash
bash scripts/generate-secret.sh
```

Copy output values into `.env`.

### 2. Start local environment

```bash
make dev-up
```

This starts: PostgreSQL, Redis, FastAPI backend, Nuxt frontend, Celery worker, Celery beat, Flower.

### 3. Apply database migrations

```bash
make db-migrate
```

### 4. Open the app

| Service | URL |
|---------|-----|
| App | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Flower | http://localhost:5555 |

## Architecture

- **Frontend**: Nuxt 4 + Vue 3 + Monaco Editor + Splitpanes
- **Backend**: FastAPI + asyncpg + SQLAlchemy 2 (async)
- **Queue**: Celery + Redis
- **SQL Analysis**: sqlglot (AST-level, no regex)
- **Undo**: Snapshot-based inverse SQL (not open transactions)
- **Auth**: JWT (15min access / 7d refresh HTTP-only cookie)
- **Encryption**: Fernet for DB credentials at rest

## Useful Commands

```bash
make dev-up           # Start all services
make dev-down         # Stop all services
make db-migrate       # Run Alembic migrations
make db-makemigration msg="add_field"  # Create new migration
make test-backend     # Run all backend tests
make generate-secret  # Generate SECRET_KEY
make generate-fernet  # Generate ENCRYPTION_KEY
make backend-shell    # Shell into backend container
```

## Project Structure

See `CONTEXT.md` for full architecture and `TODO.md` for build status.