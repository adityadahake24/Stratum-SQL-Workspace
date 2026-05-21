# Stratum — Build TODO

## Phase 1 — Core (Completed: 2026-05-21)

### Infrastructure
- [x] Monorepo directory structure
- [x] docker-compose.yml with all services
- [x] .env.example
- [x] Makefile with dev commands
- [x] Backend Dockerfile
- [x] Frontend Dockerfile
- [x] Worker Dockerfile (Dockerfile.worker)

### Backend — Foundation
- [x] FastAPI app setup with structlog, CORS, Sentry
- [x] SQLAlchemy async engine + session
- [x] All database models
- [x] Alembic initial migration
- [x] Pydantic settings from env

### Backend — Auth
- [x] User model + registration endpoint
- [x] Login endpoint + JWT generation
- [x] Refresh token (HTTP-only cookie)
- [x] Auth middleware/dependency
- [x] Session tracking

### Backend — Connections
- [x] DbConnection model
- [x] Fernet encryption service
- [x] Connection CRUD endpoints
- [x] Connection test endpoint
- [x] asyncpg pool manager

### Backend — SQL Engine
- [x] SQLAnalyzer with sqlglot
- [x] Transaction wrapping logic
- [x] Risk level detection
- [x] Missing WHERE clause detection

### Backend — Query Execution
- [x] Celery setup with Redis
- [x] QueryExecutor service
- [x] execute_query_task Celery task
- [x] WebSocket manager with Redis pub/sub
- [x] WS endpoint /ws/queries/{id}
- [x] Cancel endpoint + signal mechanism
- [x] Result pagination endpoint

### Backend — Schema Explorer
- [x] SchemaService (list schemas/tables/columns/indexes)
- [x] Redis caching for schema responses
- [x] Schema endpoints

### Backend — History
- [x] QueryHistory CRUD
- [x] History list endpoint (paginated)
- [x] History detail endpoint

### Backend — Support
- [x] SupportRequest model
- [x] Support submission endpoint

### Frontend — Foundation
- [x] Nuxt 4 project setup
- [x] TailwindCSS + shadcn-vue
- [x] Pinia stores
- [x] TanStack Vue Query setup (app/plugins/vue-query.ts)
- [x] Theme system (light/dark/system)
- [x] CSS variables

### Frontend — Auth Pages
- [x] Login page
- [x] Register page
- [x] Auth middleware
- [x] Auth store with JWT handling

### Frontend — Layout
- [x] App shell with splitpanes
- [x] Navbar component
- [x] Resizable panels

### Frontend — Editor
- [x] Monaco Editor component (pgsql syntax)
- [x] Tab bar with persistence
- [x] Run button + keyboard shortcut
- [x] Format SQL button
- [x] Auto-transaction badge

### Frontend — Explorer
- [x] DB tree component
- [x] Lazy-load schema nodes
- [x] Table right-click context menu

### Frontend — Results
- [x] Virtual scroll results table (useVirtualList from @vueuse/core)
- [x] WebSocket connection for streaming
- [x] Row batch append
- [x] Execution metadata bar
- [x] Error display

### Frontend — History
- [x] History list component
- [x] Load SQL into editor from history
- [x] Undo button per item

### Frontend — Connection
- [x] Connection modal
- [x] Test connection flow
- [x] Connection selector in navbar

## Phase 2 — Undo + Async (Target: 2026-05-21)

- [x] UndoEngine service (snapshot capture)
- [x] Inverse SQL generation (UPDATE/DELETE/INSERT)
- [x] Undo snapshot storage with TTL
- [x] Undo preview endpoint
- [x] Undo execute endpoint
- [x] Undo button in results panel
- [x] Undo preview modal in frontend
- [x] Large query undo threshold enforcement
- [x] Cleanup worker tasks (Celery Beat)

## Phase 3 — Production Hardening (Target: TBD)

- [x] Helm chart (all templates) — backend + frontend + worker deployments, services, ingress, configmap, HPA, CronJobs
- [x] HPA for workers
- [x] Kubernetes CronJobs for cleanup (deploy/helm/stratum/templates/cronjobs.yaml)
- [x] Prometheus metrics (app/core/metrics.py — queries, undo, duration, auth, connections, WS)
- [x] Encrypted connection token sharing
- [x] Rate limiting (slowapi — auth login/register + query execute)
- [x] Unit tests — SQLAnalyzer + UndoEngine
- [x] Integration tests — auth + connections (tests/integration/)
- [x] E2E tests — Playwright auth flows (tests/e2e/)
- [x] CI/CD pipeline (GitHub Actions — CI + Docker build+push to GHCR)
- [x] .env.example annotated with generation instructions per variable
- [x] API docs (docs/api.md — full endpoint reference, WS protocol, rate limits, error codes)
- [x] FastAPI Swagger UI description (auth model, rate limits, WS overview, openapi_tags)
- [x] ARCHITECTURE.md updated (ADR-013 rate limiting, ADR-014 Prometheus, ADR-015 CI/CD; ADR-011 corrected)

