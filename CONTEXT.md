# Stratum — Project Context

> This file is the single source of truth for any agent or developer resuming work on Stratum.
> **Read this file completely before writing any code or making any decisions.**
> Update this file after every significant decision, completed phase, or architectural change.

## Current Status

**Phase:** All phases complete — Phase 1, 2, and 3 (production hardening) shipped.
**Last Updated:** 2026-05-21
**What was just completed:** Phase 3 hardening complete + docs/tooling: CI/CD now builds & pushes Docker images to GHCR after tests. .env.example fully annotated with generation instructions. API docs created at docs/api.md with full endpoint reference, WS protocol, rate limits, error codes. FastAPI Swagger UI description updated with auth model, rate limits, WS overview, tags. ARCHITECTURE.md updated (ADR-013 rate limiting, ADR-014 Prometheus, ADR-015 CI/CD; ADR-011 corrected to @vueuse/core).
**What to do next:** Run `make dev-up` to start local dev environment. Run `make db-migrate` to apply migrations. Open http://localhost:3000.

## Application Summary

Stratum is a browser-based PostgreSQL SQL workspace focused on safe SQL execution,
undo operations, query history, and schema exploration.

- Frontend: Nuxt 4 + Vue 3, deployed as static/SSR on Kubernetes
- Backend: FastAPI + asyncpg + Celery, deployed on Kubernetes
- Internal DB: PostgreSQL 16 (platform data only)
- Cache/Queue: Redis 7
- SQL Analysis: sqlglot (no regex)
- Auth: JWT (access 15m, refresh 7d HTTP-only cookie)
- Undo: Snapshot-based inverse operations (NOT open transactions)

## Repository Structure

```
stratum/                               ← repo root
├── CONTEXT.md
├── ARCHITECTURE.md
├── TODO.md
├── README.md
├── docker-compose.yml
├── docker-compose.override.yml
├── .env.example
├── Makefile
├── apps/
│   ├── frontend/                      ← Nuxt 4
│   └── backend/                       ← FastAPI
├── deploy/
│   ├── helm/stratum/
│   └── docker/
├── scripts/
└── docs/
```

## Environment Setup

1. Copy `.env.example` to `.env` and fill values
2. Run: `make dev-up`
3. Run: `make db-migrate`
4. Frontend: http://localhost:3000
5. Backend: http://localhost:8000
6. API Docs: http://localhost:8000/docs
7. Flower: http://localhost:5555

## Completed Work

### Phase 1 — 2026-05-21
- Monorepo directory structure
- docker-compose.yml with all services (postgres, redis, backend, frontend, worker, beat, flower)
- .env.example with all required vars
- Makefile with dev commands
- Backend: FastAPI app shell, config, structlog, CORS, Sentry, middleware
- Backend: SQLAlchemy async engine + session factory
- Backend: All database models (users, sessions, db_connections, query_history, query_executions, undo_snapshots, support_requests)
- Backend: Alembic initial migration
- Backend: Auth service (register, login, refresh, logout, me)
- Backend: Fernet encryption service
- Backend: Connection service + CRUD + test endpoint
- Backend: asyncpg ConnectionPoolManager
- Backend: SQLAnalyzer (sqlglot-based)
- Backend: QueryExecutor + execute_query_task (Celery)
- Backend: WebSocketManager (Redis pub/sub)
- Backend: SchemaService + Redis caching
- Backend: History endpoints
- Backend: UndoEngine (snapshot + inverse SQL)
- Backend: Support endpoint
- Backend: Celery Beat cleanup tasks
- Frontend: Nuxt 4 + Tailwind + shadcn-vue
- Frontend: Theme system (light/dark/system + CSS vars)
- Frontend: Auth pages (login, register) + auth middleware
- Frontend: Pinia stores (auth, connection, editor, history, ui)
- Frontend: App shell workspace layout (splitpanes)
- Frontend: Monaco Editor (pgsql, custom theme)
- Frontend: Tab bar with persistence
- Frontend: DB Explorer tree (lazy-load)
- Frontend: Results table (WebSocket streaming + virtual scroll via useVirtualList)
- Frontend: History panel with undo button
- Frontend: Connection modal
- Frontend: Undo preview modal
- Deploy: Dockerfiles (frontend, backend, worker — Dockerfile.worker)
- Deploy: Helm chart (complete — all deployments, services, ingress, configmap, HPA, CronJobs)
- Tests: Unit (SQLAnalyzer, UndoEngine), Integration (auth, connections), E2E (Playwright auth flow)
- CI/CD: GitHub Actions CI + Docker build+push to GHCR (.github/workflows/ci.yml)
- Docs: Full API reference (docs/api.md) + annotated .env.example

## Open Decisions

| Decision | Options | Status |
|----------|---------|--------|
| SSE vs WebSocket | SSE simpler, WS bidirectional | Chose WebSocket — needed for cancel signals |
| Undo strategy | Open transactions vs snapshot | Chose snapshot-based inverse SQL |
| Result streaming | Load all vs cursor | Chose cursor (100 rows/batch) |

## Known Issues / Tech Debt

- Playwright E2E tests require a running stack (`make dev-up` + backend seeded) to execute
- No Helm/kubectl deploy workflow yet — CI builds images but Helm upgrade step is manual
- Sentry DSN must be configured in `.env` for production error tracking

## Key Design Decisions

### Undo Strategy
NOT using open transactions. Using snapshot-based inverse SQL generation.
See: `apps/backend/app/services/undo_engine.py`

### Connection Pooling
Each (user_id, connection_id) pair gets its own asyncpg pool.
Pool released after 5 minutes idle. Max 20 pools per backend instance.
See: `apps/backend/app/services/connection_pool.py`

### SQL Analysis
All SQL analysis uses sqlglot. No regex parsing anywhere.
See: `apps/backend/app/services/sql_analyzer.py`

### Result Streaming
Server-side asyncpg cursors. 100 rows per batch streamed via WebSocket.
Never load full result sets into memory.
See: `apps/backend/app/services/query_executor.py`

### Security
- DB credentials encrypted with Fernet before storage
- Encryption key loaded from env, never hardcoded
- Credentials never appear in API responses or logs
- Connection strings never in URLs or localStorage

## API Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/auth/register | Register user |
| POST | /api/v1/auth/login | Get JWT tokens |
| POST | /api/v1/auth/refresh | Rotate tokens |
| POST | /api/v1/auth/logout | Invalidate session |
| GET | /api/v1/auth/me | Current user |
| GET | /api/v1/connections | List connections |
| POST | /api/v1/connections | Create connection |
| GET | /api/v1/connections/{id} | Get connection |
| PUT | /api/v1/connections/{id} | Update connection |
| DELETE | /api/v1/connections/{id} | Delete connection |
| POST | /api/v1/connections/{id}/test | Test connectivity |
| POST | /api/v1/queries/execute | Submit query |
| GET | /api/v1/queries/executions/{id} | Poll status |
| POST | /api/v1/queries/executions/{id}/cancel | Cancel |
| GET | /api/v1/queries/executions/{id}/results | Paginated results |
| WS | /ws/queries/{id} | Stream results |
| GET | /api/v1/schema/{conn_id}/schemas | List schemas |
| GET | /api/v1/schema/{conn_id}/schemas/{s}/tables | List tables |
| GET | /api/v1/schema/{conn_id}/schemas/{s}/tables/{t}/columns | List columns |
| GET | /api/v1/history | Paginated history |
| GET | /api/v1/history/{id} | Single entry |
| GET | /api/v1/undo/{id}/preview | Preview inverse SQL |
| POST | /api/v1/undo/{id}/execute | Execute undo |
| POST | /api/v1/support | Submit support request |

## Database Tables

| Table | Purpose |
|-------|---------|
| stratum_users | User accounts |
| stratum_sessions | Login sessions |
| stratum_db_connections | Encrypted connection configs |
| stratum_query_history | All executed queries |
| stratum_query_executions | Execution lifecycle |
| stratum_undo_snapshots | Temporary undo data (TTL 24h) |
| stratum_support_requests | Support submissions |

## Frontend State

| Store | Purpose | Persisted? |
|-------|---------|-----------|
| auth | JWT, user | localStorage (token only) |
| connection | Active connection | localStorage |
| editor | Tabs, SQL drafts | localStorage |
| history | Query history | Server only |
| ui | Theme, panel sizes | localStorage |

## Infrastructure

- Kubernetes namespace: stratum
- Helm chart: `deploy/helm/stratum/`
- Docker images: `ghcr.io/your-org/stratum/{frontend,backend,worker}`
- Ingress: NGINX with cert-manager

## Environment Variables

| Variable | Description |
|----------|-------------|
| SECRET_KEY | App secret key |
| ENCRYPTION_KEY | Fernet key for credential encryption |
| DATABASE_URL | PostgreSQL connection string (internal) |
| REDIS_URL | Redis connection string |
| JWT_SECRET | JWT signing secret |
| JWT_ALGORITHM | JWT algorithm (HS256) |
| JWT_EXPIRE_MINUTES | JWT access token expiry |
| FRONTEND_URL | Frontend URL for CORS |
| BACKEND_URL | Backend URL |
| ENVIRONMENT | development/production |
| MAX_QUERY_RUNTIME_SECONDS | Max query runtime |
| MAX_RESULT_ROWS | Max result rows |
| MAX_ROWS_PER_PAGE | Max rows per result page |
| UNDO_MAX_ROWS_THRESHOLD | Max rows for undo capture |
| CONNECTION_TOKEN_EXPIRE_MINUTES | Connection token TTL |
