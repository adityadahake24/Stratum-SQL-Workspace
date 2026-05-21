# STRATUM — Production-Grade PostgreSQL Workspace
## Complete Agentic Build Prompt

> **Application Name:** Stratum
> **Tagline:** The professional PostgreSQL workspace for teams who take data seriously.
> **Target:** Production-grade, Kubernetes-ready, scalable browser-based SQL workspace.

---

## MANDATORY FIRST STEP — READ THIS BEFORE WRITING ANY CODE

Before writing a single line of code, you must:

1. Create the file `CONTEXT.md` at the monorepo root (template provided at the end of this prompt).
2. Create the file `ARCHITECTURE.md` at the monorepo root (template provided at the end of this prompt).
3. Create `TODO.md` tracking every build phase, feature, and open decision.
4. Update these files continuously. Every major decision, deviation, or completed phase must be logged.

**These files are the source of truth for any future agent session. Any agent reopening this project must read them before doing anything else.**

---

## APPLICATION OVERVIEW

**Stratum** is a browser-based PostgreSQL SQL workspace that prioritizes:

- **Safe SQL execution** with pre-execution analysis
- **Transaction-aware operations** with automatic wrapping
- **Undo capabilities** using generated inverse operations (not open transactions)
- **Query history** with full execution metadata
- **Schema exploration** with lazy-loaded tree navigation
- **Multi-tab SQL editor** powered by Monaco Editor
- **Async query execution** for long-running statements
- **Streaming results** with cursor-based pagination
- **Scalable Kubernetes deployment** via Helm

**MVP scope: PostgreSQL only.**
**Not a hacker-themed playground — a modern professional SaaS-grade workspace.**

---

## NAMING & BRANDING

- Application name: **Stratum**
- All code, configs, Docker images, Helm charts, and namespaces use: `stratum`
- Frontend package name: `@stratum/frontend`
- Backend package name: `@stratum/backend`
- Internal DB schema prefix: `stratum_`
- Kubernetes namespace: `stratum`

---

## DIRECTORY STRUCTURE — MONOREPO

```
stratum/
├── CONTEXT.md                        # Master project context (ALWAYS UPDATE)
├── ARCHITECTURE.md                   # Architecture decisions log
├── TODO.md                           # Build phases and open items
├── README.md                         # Quick start guide
├── docker-compose.yml                # Local dev environment
├── docker-compose.override.yml       # Dev overrides
├── .env.example                      # Example env vars
├── Makefile                          # Dev commands
│
├── apps/
│   ├── frontend/                     # Nuxt 4 application
│   │   ├── app/
│   │   │   ├── assets/
│   │   │   ├── components/
│   │   │   │   ├── common/           # Shared UI atoms (Button, Modal, Badge...)
│   │   │   │   ├── layout/           # AppShell, Navbar, Sidebar, Panels
│   │   │   │   ├── editor/           # SqlEditor, TabBar, RunButton, EditorToolbar
│   │   │   │   ├── explorer/         # DbTree, SchemaNode, TableNode, ColumnNode
│   │   │   │   ├── results/          # ResultTable, ResultMeta, ExportBar, Pagination
│   │   │   │   ├── history/          # HistoryList, HistoryItem, UndoButton
│   │   │   │   ├── connection/       # ConnectionModal, ConnectionCard, TokenConnect
│   │   │   │   ├── auth/             # LoginForm, RegisterForm, SessionGuard
│   │   │   │   └── support/          # SupportModal, SupportButton
│   │   │   ├── composables/
│   │   │   │   ├── useConnection.ts
│   │   │   │   ├── useQueryExecution.ts
│   │   │   │   ├── useQueryHistory.ts
│   │   │   │   ├── useUndo.ts
│   │   │   │   ├── useSchemaExplorer.ts
│   │   │   │   ├── useResultStream.ts
│   │   │   │   └── useTabs.ts
│   │   │   ├── stores/
│   │   │   │   ├── auth.store.ts
│   │   │   │   ├── connection.store.ts
│   │   │   │   ├── editor.store.ts
│   │   │   │   ├── history.store.ts
│   │   │   │   └── ui.store.ts
│   │   │   ├── pages/
│   │   │   │   ├── index.vue           # Redirect to /workspace
│   │   │   │   ├── login.vue
│   │   │   │   ├── register.vue
│   │   │   │   ├── workspace.vue       # Main app layout
│   │   │   │   └── connect/
│   │   │   │       └── [token].vue     # Encrypted token connection
│   │   │   ├── layouts/
│   │   │   │   ├── default.vue
│   │   │   │   └── auth.vue
│   │   │   ├── middleware/
│   │   │   │   └── auth.ts
│   │   │   ├── plugins/
│   │   │   │   └── api.client.ts
│   │   │   └── utils/
│   │   │       ├── format.ts
│   │   │       ├── sql.ts
│   │   │       └── time.ts
│   │   ├── public/
│   │   ├── nuxt.config.ts
│   │   ├── tailwind.config.ts
│   │   ├── components.json            # shadcn-vue config
│   │   ├── package.json
│   │   └── Dockerfile
│   │
│   └── backend/                      # FastAPI application
│       ├── app/
│       │   ├── main.py
│       │   ├── config.py              # Pydantic Settings
│       │   ├── dependencies.py        # FastAPI DI
│       │   │
│       │   ├── api/
│       │   │   └── v1/
│       │   │       ├── router.py
│       │   │       ├── auth.py
│       │   │       ├── connections.py
│       │   │       ├── queries.py
│       │   │       ├── history.py
│       │   │       ├── undo.py
│       │   │       ├── schema.py
│       │   │       ├── support.py
│       │   │       └── ws.py          # WebSocket endpoints
│       │   │
│       │   ├── core/
│       │   │   ├── security.py        # JWT, password hashing
│       │   │   ├── encryption.py      # Credential encryption (Fernet)
│       │   │   ├── middleware.py      # CORS, logging, timing
│       │   │   └── exceptions.py      # Custom exception handlers
│       │   │
│       │   ├── db/
│       │   │   ├── base.py            # SQLAlchemy async engine
│       │   │   ├── session.py         # Async session factory
│       │   │   └── migrations/        # Alembic
│       │   │       ├── env.py
│       │   │       ├── script.py.mako
│       │   │       └── versions/
│       │   │
│       │   ├── models/                # SQLAlchemy ORM models
│       │   │   ├── base.py
│       │   │   ├── user.py
│       │   │   ├── session.py
│       │   │   ├── db_connection.py
│       │   │   ├── query_history.py
│       │   │   ├── query_execution.py
│       │   │   ├── undo_snapshot.py
│       │   │   └── support_request.py
│       │   │
│       │   ├── schemas/               # Pydantic request/response models
│       │   │   ├── auth.py
│       │   │   ├── connection.py
│       │   │   ├── query.py
│       │   │   ├── history.py
│       │   │   ├── undo.py
│       │   │   ├── schema_explorer.py
│       │   │   └── support.py
│       │   │
│       │   ├── services/              # Business logic
│       │   │   ├── auth_service.py
│       │   │   ├── connection_service.py
│       │   │   ├── connection_pool.py  # asyncpg pool manager
│       │   │   ├── query_executor.py   # Core execution engine
│       │   │   ├── sql_analyzer.py     # sqlglot-based analysis
│       │   │   ├── undo_engine.py      # Snapshot + inverse op generator
│       │   │   ├── schema_service.py   # Schema introspection
│       │   │   ├── result_streamer.py  # Cursor-based result pagination
│       │   │   ├── token_service.py    # Encrypted connection tokens
│       │   │   └── cleanup_service.py  # TTL cleanup logic
│       │   │
│       │   ├── workers/
│       │   │   ├── celery_app.py
│       │   │   ├── tasks/
│       │   │   │   ├── query_tasks.py
│       │   │   │   ├── undo_tasks.py
│       │   │   │   └── cleanup_tasks.py
│       │   │   └── beat_schedule.py
│       │   │
│       │   └── websockets/
│       │       ├── manager.py          # WebSocket connection manager
│       │       └── query_stream.py     # Query progress streaming
│       │
│       ├── tests/
│       │   ├── conftest.py
│       │   ├── unit/
│       │   │   ├── test_sql_analyzer.py
│       │   │   ├── test_undo_engine.py
│       │   │   └── test_connection_pool.py
│       │   └── integration/
│       │       ├── test_query_execution.py
│       │       └── test_auth.py
│       │
│       ├── requirements.txt
│       ├── requirements-dev.txt
│       ├── alembic.ini
│       ├── pyproject.toml
│       └── Dockerfile
│
├── deploy/
│   ├── helm/
│   │   └── stratum/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       ├── values.production.yaml
│   │       ├── templates/
│   │       │   ├── _helpers.tpl
│   │       │   ├── namespace.yaml
│   │       │   ├── frontend-deployment.yaml
│   │       │   ├── frontend-service.yaml
│   │       │   ├── backend-deployment.yaml
│   │       │   ├── backend-service.yaml
│   │       │   ├── worker-deployment.yaml
│   │       │   ├── beat-deployment.yaml
│   │       │   ├── ingress.yaml
│   │       │   ├── hpa.yaml
│   │       │   ├── redis.yaml
│   │       │   ├── secrets.yaml
│   │       │   ├── configmap.yaml
│   │       │   └── cronjob-cleanup.yaml
│   │
│   └── docker/
│       ├── frontend.Dockerfile
│       ├── backend.Dockerfile
│       └── worker.Dockerfile
│
├── scripts/
│   ├── dev-up.sh                     # Start local environment
│   ├── db-migrate.sh                 # Run Alembic migrations
│   ├── db-seed.sh                    # Seed dev data
│   └── generate-secret.sh            # Generate encryption keys
│
└── docs/
    ├── api/                          # OpenAPI docs
    ├── deployment.md
    └── local-dev.md
```

---

## PHASE 1 BUILD — AUTHENTICATION + CORE WORKSPACE

### Step 1: Monorepo Bootstrap

Initialize the monorepo exactly as structured above.

Create `docker-compose.yml` with services:
- `postgres` — PostgreSQL 16 for internal platform data (port 5432)
- `redis` — Redis 7 (port 6379)
- `backend` — FastAPI with hot reload (port 8000)
- `frontend` — Nuxt dev server (port 3000)
- `worker` — Celery worker
- `beat` — Celery beat scheduler
- `flower` — Celery monitoring (port 5555, dev only)

All services must:
- Use named volumes for persistence
- Reference environment variables from `.env`
- Have health checks defined

Create `.env.example` with:
```
# Platform
SECRET_KEY=change-me-generate-with-scripts/generate-secret.sh
ENCRYPTION_KEY=change-me-32-bytes-fernet-key

# Internal DB
DATABASE_URL=postgresql+asyncpg://stratum:stratum@postgres:5432/stratum

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET=change-me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# App
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development

# Query limits
MAX_QUERY_RUNTIME_SECONDS=60
MAX_RESULT_ROWS=1000
MAX_ROWS_PER_PAGE=100
UNDO_MAX_ROWS_THRESHOLD=100000

# Connection
CONNECTION_TOKEN_EXPIRE_MINUTES=30
```

---

### Step 2: Backend Foundation

#### Tech Stack & Libraries

```
# requirements.txt — EXACT packages to use

# Web framework
fastapi==0.115.0
uvicorn[standard]==0.30.0
gunicorn==22.0.0

# Database - Internal platform
sqlalchemy[asyncio]==2.0.36
asyncpg==0.30.0
alembic==1.13.3

# Database - Connection pool for user DBs
asyncpg==0.30.0

# SQL Analysis
sqlglot==25.0.0

# Task Queue
celery[redis]==5.4.0
redis[asyncio]==5.0.8
flower==2.0.1

# Auth & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
cryptography==43.0.0

# Validation
pydantic==2.9.0
pydantic-settings==2.5.0
email-validator==2.2.0

# HTTP
httpx==0.27.2
python-multipart==0.0.12

# Serialization (fast)
orjson==3.10.7

# Logging
structlog==24.4.0
python-json-logger==2.0.7

# Retry logic
tenacity==9.0.0

# Metrics
prometheus-fastapi-instrumentator==7.0.0

# Error tracking
sentry-sdk[fastapi]==2.14.0

# Date/time
python-dateutil==2.9.0

# Testing
pytest==8.3.0
pytest-asyncio==0.24.0
httpx==0.27.2
factory-boy==3.3.1
faker==30.0.0
```

#### Internal Database Schema

Create Alembic migrations for all tables. Use `stratum_` prefix on all tables.

```python
# models/user.py
class User(Base):
    __tablename__ = "stratum_users"
    id: UUID (PK, default uuid4)
    email: str (unique, indexed)
    hashed_password: str
    is_active: bool (default True)
    is_verified: bool (default False)
    created_at: datetime
    updated_at: datetime

# models/session.py
class UserSession(Base):
    __tablename__ = "stratum_sessions"
    id: UUID (PK)
    user_id: UUID (FK → users)
    token_hash: str (indexed)
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    is_active: bool

# models/db_connection.py
class DbConnection(Base):
    __tablename__ = "stratum_db_connections"
    id: UUID (PK)
    user_id: UUID (FK → users)
    name: str
    host: str (encrypted)
    port: int
    database: str (encrypted)
    username: str (encrypted)
    password_encrypted: str  # Fernet encrypted
    ssl_mode: str (disable/require/verify-ca/verify-full)
    is_active: bool
    last_used_at: datetime
    created_at: datetime
    # NEVER store raw connection strings or passwords unencrypted

# models/query_history.py
class QueryHistory(Base):
    __tablename__ = "stratum_query_history"
    id: UUID (PK)
    user_id: UUID (FK → users)
    connection_id: UUID (FK → db_connections)
    sql_text: str (full query)
    query_type: str  # SELECT / INSERT / UPDATE / DELETE / DDL / MIXED
    execution_status: str  # pending / running / success / error / cancelled
    execution_time_ms: int
    rows_affected: int
    row_count: int
    error_message: str
    has_undo: bool (default False)
    undo_snapshot_id: UUID (nullable)
    undo_executed_at: datetime (nullable)
    created_at: datetime

# models/query_execution.py
class QueryExecution(Base):
    __tablename__ = "stratum_query_executions"
    id: UUID (PK, = celery task id)
    history_id: UUID (FK → query_history)
    user_id: UUID (FK → users)
    status: str  # queued / running / streaming / complete / error / cancelled
    progress_pct: int
    worker_node: str
    started_at: datetime
    completed_at: datetime
    created_at: datetime

# models/undo_snapshot.py
class UndoSnapshot(Base):
    __tablename__ = "stratum_undo_snapshots"
    id: UUID (PK)
    history_id: UUID (FK → query_history)
    user_id: UUID (FK → users)
    operation_type: str  # UPDATE / DELETE / INSERT
    table_name: str
    schema_name: str
    snapshot_data: bytes  # compressed JSON of affected rows
    snapshot_size_bytes: int
    row_count: int
    inverse_sql: str  # pre-generated inverse SQL
    expires_at: datetime  # TTL — 24 hours from creation
    created_at: datetime

# models/support_request.py
class SupportRequest(Base):
    __tablename__ = "stratum_support_requests"
    id: UUID (PK)
    user_id: UUID (nullable FK → users)
    email: str
    message: str
    status: str  # open / in_progress / resolved
    created_at: datetime
```

Add indexes:
- `stratum_query_history`: `(user_id, created_at DESC)`, `(connection_id, created_at DESC)`
- `stratum_undo_snapshots`: `(user_id, expires_at)`, `(history_id)`
- `stratum_sessions`: `(token_hash)`, `(user_id, is_active)`
- `stratum_query_executions`: `(user_id, status)`, `(history_id)`

---

### Step 3: Core Services

#### `services/sql_analyzer.py`

Use **sqlglot** for ALL SQL analysis. Never use regex.

```python
class SQLAnalyzer:
    """
    Analyzes SQL statements before execution.
    Determines: query type, transaction wrapping need,
    undo eligibility, DML targets, estimated impact.
    """
    
    def analyze(self, sql: str) -> SQLAnalysisResult:
        """
        Returns:
        - statement_types: List[str]  # SELECT, INSERT, UPDATE, DELETE, DDL, TCL
        - needs_transaction_wrap: bool
        - has_existing_transaction: bool  # BEGIN/COMMIT detected
        - undo_eligible: bool
        - target_tables: List[str]  # tables being written to
        - is_read_only: bool
        - has_dangerous_patterns: bool  # UPDATE/DELETE without WHERE
        - risk_level: str  # low / medium / high
        - warnings: List[str]
        """
    
    def wrap_in_transaction(self, sql: str) -> str:
        """Wraps SQL in BEGIN/COMMIT if eligible"""
    
    def detect_missing_where(self, sql: str) -> bool:
        """Detect UPDATE or DELETE without WHERE clause"""
    
    def extract_affected_tables(self, sql: str) -> List[TableRef]:
        """Returns schema + table for all write targets"""
```

Transaction wrapping rules:
- Wrap if: query contains INSERT/UPDATE/DELETE and no BEGIN/COMMIT already present
- Do NOT wrap: SELECT-only queries, DDL statements (they auto-commit in PG), queries already in transactions

Risk level rules:
- `high`: UPDATE or DELETE without WHERE clause
- `medium`: UPDATE/DELETE affecting known large tables, DDL statements
- `low`: standard DML with WHERE, INSERT with VALUES

#### `services/connection_pool.py`

```python
class ConnectionPoolManager:
    """
    Manages asyncpg connection pools per user connection.
    
    Pool keyed by: (user_id, connection_id)
    Each pool: min_size=1, max_size=5, max_inactive_connection_lifetime=300s
    
    IMPORTANT:
    - Credentials decrypted in memory only, never logged or serialized
    - Pools released after 5 minutes idle
    - Max 20 concurrent pools per backend instance
    - All external connections through SSL when configured
    """
    
    async def get_pool(self, user_id: UUID, connection_id: UUID) -> asyncpg.Pool
    async def release_pool(self, user_id: UUID, connection_id: UUID)
    async def test_connection(self, credentials: ConnectionCredentials) -> bool
    async def cleanup_idle_pools(self)  # Called by background task
```

#### `services/query_executor.py`

```python
class QueryExecutor:
    """
    Core query execution service.
    
    Execution flow:
    1. Analyze SQL with SQLAnalyzer
    2. Check risk level, surface warnings
    3. If undo-eligible: capture pre-execution snapshot
    4. Apply transaction wrapping if needed
    5. Execute with statement_timeout set
    6. Stream results via cursor (100 rows/page)
    7. Generate undo inverse SQL
    8. Store history + snapshot
    9. Emit WebSocket progress events
    
    NEVER load full result sets into memory.
    Use server-side cursors for all SELECT results.
    """
    
    async def execute(
        self,
        sql: str,
        connection_id: UUID,
        user_id: UUID,
        execution_id: UUID,
        stream_callback: Callable,  # WebSocket emit function
    ) -> QueryExecutionResult
    
    async def cancel(self, execution_id: UUID)
    
    async def fetch_page(
        self,
        execution_id: UUID,
        page: int,
        page_size: int = 100,
    ) -> ResultPage
```

#### `services/undo_engine.py`

```python
class UndoEngine:
    """
    Generates and executes inverse operations.
    
    Strategy per operation type:
    
    UPDATE:
      - Before exec: SELECT affected rows where condition matches
      - Generate: UPDATE t SET col=old_val WHERE pk=val (per row)
      - Store: compressed JSON snapshot of original rows
    
    DELETE:
      - Before exec: SELECT rows to be deleted
      - Generate: INSERT INTO t (cols) VALUES (...) for each row
      - Store: compressed JSON of deleted rows
    
    INSERT:
      - After exec: capture inserted PKs (via RETURNING)
      - Generate: DELETE FROM t WHERE pk IN (...)
      - Store: inserted PK list only
    
    HARD LIMITS (abort undo capture if exceeded):
      - MAX_UNDO_ROWS = 100,000 rows
      - MAX_UNDO_SIZE_MB = 500 MB
      - If exceeded: mark query as has_undo=False, warn user
    
    SNAPSHOT STORAGE:
      - Compress with zlib level 6
      - Store in stratum_undo_snapshots
      - TTL = 24 hours (configurable)
      - Auto-deleted by cleanup worker
    
    UNDO EXECUTION:
      - Retrieve snapshot
      - Validate it hasn't expired
      - Execute inverse SQL in transaction
      - Store undo execution as new history entry
      - Mark original snapshot as consumed
    """
    
    async def capture_pre_snapshot(
        self,
        pool: asyncpg.Pool,
        sql: str,
        analysis: SQLAnalysisResult,
    ) -> UndoSnapshot | None
    
    async def generate_inverse_sql(
        self,
        snapshot: UndoSnapshot,
        original_sql: str,
    ) -> str
    
    async def execute_undo(
        self,
        snapshot_id: UUID,
        user_id: UUID,
        connection_id: UUID,
    ) -> QueryExecutionResult
```

#### `services/schema_service.py`

```python
class SchemaService:
    """
    PostgreSQL schema introspection.
    
    Uses information_schema and pg_catalog.
    All queries read-only, use connection pool.
    Lazy-loaded per tree node expansion.
    
    Caches schema tree in Redis (TTL 60 seconds per connection).
    """
    
    async def list_schemas(self, pool) -> List[SchemaInfo]
    async def list_tables(self, pool, schema: str) -> List[TableInfo]
    async def list_columns(self, pool, schema: str, table: str) -> List[ColumnInfo]
    async def list_indexes(self, pool, schema: str, table: str) -> List[IndexInfo]
    async def list_foreign_keys(self, pool, schema: str, table: str) -> List[FKInfo]
    async def get_table_row_count_estimate(self, pool, schema: str, table: str) -> int
```

---

### Step 4: API Endpoints

All endpoints under `/api/v1/`. Auth required for all except login/register.

#### Authentication — `/api/v1/auth`

```
POST /auth/register         — email + password registration
POST /auth/login            — returns JWT access token + refresh token
POST /auth/refresh          — rotate tokens
POST /auth/logout           — invalidate session
GET  /auth/me               — current user info
```

JWT access token: 15 minutes
Refresh token: 7 days, stored as HTTP-only cookie
Session stored in `stratum_sessions` table for audit trail.

#### Connections — `/api/v1/connections`

```
GET    /connections              — list user's saved connections
POST   /connections              — save new connection (credentials encrypted)
GET    /connections/{id}         — get connection (no raw credentials in response)
PUT    /connections/{id}         — update connection
DELETE /connections/{id}         — remove connection + release pool
POST   /connections/{id}/test    — test connectivity
POST   /connections/tokens       — generate encrypted token for shareable URL
POST   /connections/tokens/{t}   — resolve token → establish connection session
```

**SECURITY RULE**: Connection credentials MUST NEVER appear in response bodies. Return only: id, name, host (masked), port, database, ssl_mode, last_used_at. Passwords are write-only.

#### Queries — `/api/v1/queries`

```
POST /queries/execute           — submit query for execution
GET  /queries/executions/{id}   — poll execution status
POST /queries/executions/{id}/cancel  — cancel running query
GET  /queries/executions/{id}/results — fetch paginated results
WS   /ws/queries/{execution_id} — WebSocket for live progress + streaming
```

Query execution request body:
```json
{
  "connection_id": "uuid",
  "sql": "SELECT * FROM users LIMIT 10",
  "tab_id": "uuid",
  "auto_limit": true
}
```

Query response (initial, before streaming):
```json
{
  "execution_id": "uuid",
  "analysis": {
    "query_type": "SELECT",
    "is_read_only": true,
    "risk_level": "low",
    "warnings": [],
    "undo_eligible": false
  },
  "status": "queued"
}
```

WebSocket messages (server → client):
```json
{"type": "status", "status": "running", "started_at": "..."}
{"type": "row_batch", "rows": [...], "batch_number": 1, "total_so_far": 100}
{"type": "complete", "execution_time_ms": 423, "row_count": 847, "has_undo": true}
{"type": "error", "message": "...", "code": "query_timeout"}
{"type": "cancelled"}
```

#### Schema Explorer — `/api/v1/schema`

```
GET /schema/{connection_id}/schemas
GET /schema/{connection_id}/schemas/{schema}/tables
GET /schema/{connection_id}/schemas/{schema}/tables/{table}/columns
GET /schema/{connection_id}/schemas/{schema}/tables/{table}/indexes
```

All responses cached in Redis with 60-second TTL.

#### History — `/api/v1/history`

```
GET /history?connection_id=&page=&page_size=50   — paginated history
GET /history/{id}                                — single entry with full SQL
GET /history/{id}/results                        — re-fetch results if available
```

#### Undo — `/api/v1/undo`

```
GET  /undo/{history_id}/preview   — show inverse SQL before executing
POST /undo/{history_id}/execute   — execute undo operation
GET  /undo/{history_id}/status    — undo snapshot status + TTL remaining
```

#### Support — `/api/v1/support`

```
POST /support   — submit support request
```

---

### Step 5: Async Worker System

Use **Celery** with Redis as broker and result backend.

#### `workers/tasks/query_tasks.py`

```python
@celery_app.task(
    bind=True,
    max_retries=0,       # Never retry failed queries
    time_limit=70,       # Hard kill at 70s (query limit is 60s)
    soft_time_limit=65,  # Soft signal at 65s
    acks_late=True,      # Only ack after task completes
)
async def execute_query_task(
    self,
    execution_id: str,
    connection_id: str,
    user_id: str,
    sql: str,
):
    """
    1. Update execution status → running
    2. Get connection pool
    3. Run query with statement_timeout = 60s
    4. Stream rows back via WebSocket manager
    5. Capture undo snapshot if eligible
    6. Update history record
    7. Update execution status → complete / error
    """
```

#### `workers/tasks/cleanup_tasks.py`

```python
@celery_app.task
async def cleanup_expired_snapshots():
    """Delete stratum_undo_snapshots where expires_at < NOW()"""

@celery_app.task
async def cleanup_stale_sessions():
    """Deactivate sessions where expires_at < NOW()"""

@celery_app.task
async def cleanup_idle_connection_pools():
    """Release asyncpg pools idle > 5 minutes"""

@celery_app.task
async def cleanup_expired_tokens():
    """Remove expired connection tokens from Redis"""
```

Beat schedule:
```python
beat_schedule = {
    "cleanup-snapshots": {"task": "cleanup_expired_snapshots", "schedule": crontab(minute="*/15")},
    "cleanup-sessions":  {"task": "cleanup_stale_sessions",    "schedule": crontab(hour="*/2")},
    "cleanup-pools":     {"task": "cleanup_idle_connection_pools", "schedule": crontab(minute="*/5")},
    "cleanup-tokens":    {"task": "cleanup_expired_tokens",    "schedule": crontab(minute="*/10")},
}
```

---

### Step 6: WebSocket Manager

```python
class WebSocketManager:
    """
    Manages active WebSocket connections per execution_id.
    State stored in Redis so any backend pod can publish.
    
    Redis pub/sub channel: stratum:ws:{execution_id}
    
    Flow:
    - Client connects to WS /ws/queries/{execution_id}
    - Worker publishes progress to Redis channel
    - WS handler subscribes and forwards to client
    - On disconnect: cleanup subscription
    """
    
    async def connect(self, execution_id: str, websocket: WebSocket)
    async def disconnect(self, execution_id: str, websocket: WebSocket)
    async def publish(self, execution_id: str, message: dict)
    async def subscribe_and_forward(self, execution_id: str, websocket: WebSocket)
```

---

## PHASE 1 FRONTEND

### Tech Stack & Libraries

```json
// package.json dependencies
{
  "nuxt": "^4.0.0",
  "vue": "^3.5.0",
  "@nuxtjs/tailwindcss": "^6.12.0",
  "shadcn-nuxt": "^0.10.0",
  "@pinia/nuxt": "^0.7.0",
  "pinia": "^2.2.0",
  "@tanstack/vue-query": "^5.56.0",
  "@vueuse/core": "^11.0.0",
  "@vueuse/nuxt": "^11.0.0",
  "monaco-editor": "^0.52.0",
  "@guolao/vue-monaco-editor": "^1.0.0",
  "vue-virtual-scroller": "^2.0.0-beta.8",
  "splitpanes": "^3.1.0",
  "zod": "^3.23.0",
  "date-fns": "^4.1.0",
  "lucide-vue-next": "^0.441.0",
  "class-variance-authority": "^0.7.0",
  "clsx": "^2.1.0",
  "tailwind-merge": "^2.5.0",
  "radix-vue": "^1.9.0",
  "vue-sonner": "^1.1.0",
  "@formkit/auto-animate": "^0.8.2",
  "rehype-highlight": "^7.0.0",
  "sql-formatter": "^15.3.0"
}
```

### Layout — `workspace.vue`

The workspace is divided into 4 panels using `splitpanes`:

```
┌──────────────────────────────────────────────────────────────┐
│  NAVBAR: Logo | DB picker | Theme | Support | User menu      │
├──────────────┬──────────────────────────┬────────────────────┤
│              │  TAB BAR                 │                    │
│  DB EXPLORER │──────────────────────────│  RIGHT PANEL       │
│              │  MONACO SQL EDITOR       │  (History / Syntax)│
│  Schemas     │                          │                    │
│  └ Tables    │──────────────────────────│                    │
│    └ Columns │  RESULTS TABLE           │                    │
│    └ Indexes │  (virtual scroll, paged) │                    │
│              │                          │                    │
└──────────────┴──────────────────────────┴────────────────────┘
```

Panel sizes (resizable via splitpanes):
- Left: 20% (min 15%, max 35%)
- Center: 55% (min 40%)
- Right: 25% (min 20%, max 35%)

Center panel split vertically:
- Editor: 45% (min 25%)
- Results: 55% (min 30%)

Panel state (sizes) persisted in localStorage.

### Left Panel — Database Explorer

Component: `components/explorer/DbTree.vue`

```
Features:
- Tree structure: Connection → Schema → Tables → Columns/Indexes
- Lazy-load each level on expand (API call per expansion)
- Double-click table → INSERT snippet into current editor tab
- Right-click table → context menu: SELECT TOP 100, Show columns, Show indexes
- Search/filter within current schema
- Loading skeleton per node
- Error state per node with retry
- Connection selector at top of panel
```

### Center Panel — SQL Workspace

#### Tab Bar — `components/editor/TabBar.vue`

```
Features:
- Multiple tabs (max 10)
- Each tab: name (editable), close button, unsaved indicator (dot)
- Add tab button
- Tabs draggable to reorder
- Tab content persisted in Pinia (editor drafts survive page refresh via localStorage)
- Middle-click to close tab
```

#### SQL Editor — `components/editor/SqlEditor.vue`

```
Monaco Editor configuration:
- Language: pgsql (PostgreSQL)
- Theme: stratum-dark / stratum-light (custom tokens)
- Font: JetBrains Mono (loaded from bunny fonts)
- Font size: 14px
- Tab size: 2 spaces
- Word wrap: off
- Minimap: off (too narrow)
- Bracket pair colorization: on
- Format document action: sql-formatter with PostgreSQL dialect

Keyboard shortcuts:
- Ctrl/Cmd + Enter: Execute query
- Ctrl/Cmd + Shift + F: Format SQL
- Ctrl/Cmd + /: Toggle comment
- F5: Execute (same as Ctrl+Enter)

Editor toolbar:
- Run button (play icon) — primary action
- Format button (magic wand)
- Cancel button (appears during execution)
- Statement timeout indicator
- Auto-transaction badge (shows when wrapping will be applied)
```

#### Results Panel — `components/results/ResultTable.vue`

```
Features:
- Virtual scrolling via vue-virtual-scroller (handles 10,000+ rows)
- Column headers with sort indicators (client-side sort for current page)
- Column resizing via drag
- Cell value copy on click
- NULL display as distinct styled pill
- JSON/array values expandable in modal
- Long strings truncated with expand
- Execution metadata bar: rows returned, time, affected rows, undo available
- Pagination controls (page N of M, jump to page)
- "Undo available" button when has_undo=true — opens undo preview modal
- Export button (CSV) — client-side for current page
- Error display with full error message + PG error code
```

### Right Panel — History & Syntax

#### History Tab — `components/history/HistoryList.vue`

```
Features:
- List of executions, newest first
- Each item shows: SQL preview (first 80 chars), time, status badge, execution time
- Status badges: success (green), error (red), running (animated blue), cancelled (gray)
- Click item → load SQL into current editor tab
- Undo button on items with has_undo=true
- Undo badge shows TTL remaining (e.g. "23h 47m")
- Filter by: connection, status, time range
- Infinite scroll pagination
```

#### Syntax Tab — `components/history/SyntaxHelper.vue`

```
Content:
- PostgreSQL quick reference cards
- Common query patterns (SELECT, INSERT, UPDATE, DELETE, CTEs, Window functions)
- Keyboard shortcuts reference
- Click snippet → insert at cursor position in editor
- Searchable
```

### Connection Modal — `components/connection/ConnectionModal.vue`

```
Fields:
- Connection name (label, e.g. "Production DB")
- Host
- Port (default 5432)
- Database name
- Username
- Password (masked, never shown again after save)
- SSL mode selector: disable / require / verify-ca / verify-full
- Test connection button (shows latency or error)
- Save button

After test: shows connection success with PG version string
Error: shows full error message from PG

NEVER expose raw connection string in URL or console.
```

### State Management — Pinia Stores

#### `stores/auth.store.ts`
```typescript
interface AuthStore {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  
  actions:
    login(email, password)
    logout()
    refreshToken()
    fetchMe()
}
```

#### `stores/connection.store.ts`
```typescript
interface ConnectionStore {
  connections: DbConnection[]
  activeConnectionId: UUID | null
  
  actions:
    loadConnections()
    selectConnection(id)
    createConnection(data)
    testConnection(id)
    deleteConnection(id)
}
```

#### `stores/editor.store.ts`
```typescript
interface Tab {
  id: UUID
  name: string
  sql: string
  connectionId: UUID | null
  executionId: UUID | null
  isDirty: boolean
}

interface EditorStore {
  tabs: Tab[]
  activeTabId: UUID | null
  
  actions:
    addTab()
    closeTab(id)
    setTabSql(id, sql)
    setActiveTab(id)
    duplicateTab(id)
}

// Persist tabs + SQL to localStorage
// Load on mount
```

#### `stores/history.store.ts`
```typescript
interface HistoryStore {
  items: QueryHistory[]
  page: number
  isLoading: boolean
  
  actions:
    loadHistory(connectionId?)
    loadMore()
    previewUndo(historyId)
    executeUndo(historyId)
}
```

### Theme System

Support: `light`, `dark`, `system`.

Custom Tailwind CSS variables for Stratum theme.

Define in `app/assets/css/main.css`:
```css
:root {
  --stratum-bg-primary: #ffffff;
  --stratum-bg-secondary: #f8f9fa;
  --stratum-bg-tertiary: #f1f3f4;
  --stratum-bg-elevated: #ffffff;
  --stratum-border: #e2e4e7;
  --stratum-text-primary: #1a1c1e;
  --stratum-text-secondary: #6b7280;
  --stratum-text-muted: #9ca3af;
  --stratum-accent: #5B6CF2;
  --stratum-accent-hover: #4857e0;
  --stratum-success: #10b981;
  --stratum-error: #ef4444;
  --stratum-warning: #f59e0b;
}

[data-theme="dark"] {
  --stratum-bg-primary: #0f1117;
  --stratum-bg-secondary: #161b22;
  --stratum-bg-tertiary: #1c2128;
  --stratum-bg-elevated: #1c2128;
  --stratum-border: #30363d;
  --stratum-text-primary: #e6edf3;
  --stratum-text-secondary: #8b949e;
  --stratum-text-muted: #656d76;
  --stratum-accent: #818cf8;
  --stratum-accent-hover: #929bf9;
}
```

Monaco Editor custom theme (stratum-dark/stratum-light) must match these colors.
Define using `monaco.editor.defineTheme`.

---

## PHASE 2 BUILD — UNDO + ASYNC + STREAMING

### Undo Flow (Full Implementation)

```
User clicks Run → Frontend sends POST /api/v1/queries/execute
                ↓
Backend → SQLAnalyzer.analyze(sql)
                ↓
        undo_eligible = True?
                ↓ Yes
UndoEngine.capture_pre_snapshot(pool, sql)
  → SELECT affected rows WHERE condition
  → If row_count > 100k: abort undo, set eligible=False, warn
  → Compress snapshot with zlib
  → Store in stratum_undo_snapshots (expires 24h)
                ↓
Execute wrapped SQL in transaction
                ↓
UndoEngine.generate_inverse_sql(snapshot, original_sql)
  → UPDATE original: generate UPDATE t SET col=val WHERE pk=id per row
  → DELETE original: generate INSERT INTO t VALUES (...) per row
  → INSERT original: generate DELETE FROM t WHERE id IN (...)
                ↓
Store inverse_sql in snapshot record
Set history.has_undo = True
                ↓
Return to frontend with has_undo=True

User clicks Undo:
  → GET /undo/{history_id}/preview — show inverse SQL in modal
  → POST /undo/{history_id}/execute
  → Execute inverse_sql in new transaction
  → Create new query_history record for the undo operation
  → Mark snapshot as consumed (cannot undo twice)
  → Return result
```

### Query Execution Flow (Full Async)

```
POST /queries/execute
  → Create query_history record (status=pending)
  → Create query_execution record (status=queued)
  → Enqueue Celery task: execute_query_task.delay(...)
  → Return {execution_id, status: "queued"}

Frontend immediately opens WebSocket to:
  ws://backend/ws/queries/{execution_id}

Celery worker picks up task:
  → Update status → running
  → Publish to Redis channel: stratum:ws:{execution_id}
  → WS handler forwards to client: {"type": "status", "status": "running"}
  → Execute SQL with asyncpg cursor
  → Iterate cursor in batches of 100 rows:
    → Publish {"type": "row_batch", "rows": [...]}
    → WS forwards to client
    → Frontend appends to virtual scroller
  → Query complete:
    → Publish {"type": "complete", "row_count": N, "execution_time_ms": T, "has_undo": bool}
    → Update query_history + query_execution records
  → Worker releases connection back to pool

If cancel requested:
  → Client sends HTTP POST /queries/executions/{id}/cancel
  → Backend publishes cancel signal to Redis: stratum:cancel:{execution_id}
  → Worker checks cancel flag between row batches
  → Calls conn.cancel() on asyncpg connection
  → Publishes {"type": "cancelled"}
```

---

## KUBERNETES DEPLOYMENT

### Helm Chart Structure

```yaml
# values.yaml
global:
  image:
    registry: ghcr.io
    repository: your-org/stratum
    tag: latest
  env: production

frontend:
  replicaCount: 2
  resources:
    requests: { cpu: 100m, memory: 256Mi }
    limits: { cpu: 500m, memory: 512Mi }

backend:
  replicaCount: 3
  resources:
    requests: { cpu: 200m, memory: 512Mi }
    limits: { cpu: 1000m, memory: 1Gi }

worker:
  replicaCount: 2
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
  resources:
    requests: { cpu: 500m, memory: 1Gi }
    limits: { cpu: 2000m, memory: 4Gi }

beat:
  replicaCount: 1  # ALWAYS 1 — beat must not run as multiple replicas

redis:
  enabled: true
  auth:
    enabled: true
  master:
    persistence:
      enabled: true
      size: 8Gi

postgresql:
  enabled: true
  auth:
    database: stratum
  primary:
    persistence:
      enabled: true
      size: 50Gi

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"  # WebSocket timeout
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
  hosts:
    - host: app.stratum.io
      paths: [/]
  tls:
    - secretName: stratum-tls
      hosts: [app.stratum.io]

secrets:
  secretKey: ""          # Set via helm --set or external secrets
  encryptionKey: ""
  jwtSecret: ""
  databaseUrl: ""
  redisUrl: ""
```

### HPA for Workers

```yaml
# templates/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: stratum-worker
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: stratum-worker
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: External
      external:
        metric:
          name: celery_queue_length
        target:
          type: AverageValue
          averageValue: "5"
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Secrets Management

All secrets via Kubernetes Secrets, referenced as environment variables.

```yaml
# templates/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: stratum-secrets
type: Opaque
stringData:
  SECRET_KEY: {{ .Values.secrets.secretKey }}
  ENCRYPTION_KEY: {{ .Values.secrets.encryptionKey }}
  JWT_SECRET: {{ .Values.secrets.jwtSecret }}
  DATABASE_URL: {{ .Values.secrets.databaseUrl }}
  REDIS_URL: {{ .Values.secrets.redisUrl }}
```

Future: integrate with HashiCorp Vault or Kubernetes External Secrets Operator.

---

## SECURITY REQUIREMENTS — NON-NEGOTIABLE

1. **NEVER log SQL query parameters that could contain sensitive data**
2. **NEVER include connection credentials in API responses**
3. **NEVER store passwords in plaintext** — Fernet encryption for DB credentials, bcrypt for user passwords
4. **NEVER put connection strings in URLs, browser history, or localStorage**
5. **ALWAYS validate and sanitize query inputs even though sqlglot analyzes them**
6. **ALWAYS enforce statement_timeout on every query execution**
7. **ALWAYS enforce row limits** — reject result fetches beyond MAX_RESULT_ROWS
8. **Rate limit all API endpoints** — auth endpoints especially (10 req/min per IP)
9. **CORS configured strictly** — only allow FRONTEND_URL origin
10. **JWT tokens must be short-lived** — 15 min access, 7 day refresh (HTTP-only cookie)
11. **Connection tokens must be short-lived** — 30 minutes max, single-use preferred
12. **Undo snapshots must expire** — 24 hour TTL, hard-deleted by cleanup worker
13. **Input validation on all endpoints** via Pydantic with strict mode
14. **SQL injection is NOT a concern for user's own DB** (they're sending queries to their own DB) but platform SQL (schema introspection, undo capture) must use parameterized queries only

---

## OBSERVABILITY

### Logging

Use `structlog` for all backend logging.

Every log entry must include:
- `request_id` (UUID, set in middleware)
- `user_id` (when authenticated)
- `execution_id` (for query logs)
- `duration_ms` (for timed operations)
- `environment`

Log levels:
- `DEBUG`: Query analysis results, pool operations
- `INFO`: Query execution start/complete, undo operations, connections
- `WARNING`: Large queries approaching limits, slow queries > 5s, undo capture skipped
- `ERROR`: Execution failures, pool exhaustion, encryption errors
- `CRITICAL`: Security events, authentication failures (repeated)

**NEVER log**: SQL parameters that could contain sensitive data, raw passwords, decrypted credentials.

### Metrics (Prometheus)

Expose `/metrics` endpoint via `prometheus-fastapi-instrumentator`.

Track:
- `stratum_queries_total` (by type, status)
- `stratum_query_duration_seconds` (histogram)
- `stratum_active_connections_total` (gauge)
- `stratum_undo_snapshots_total` (counter)
- `stratum_undo_snapshot_size_bytes` (histogram)
- `stratum_worker_queue_length` (gauge)

### Sentry

Configure Sentry DSN via environment variable.
Capture: unhandled exceptions, slow queries > 10s, worker task failures.

---

## CONTEXT MAINTENANCE SYSTEM

**THIS IS MANDATORY.** Create and maintain these files throughout the entire build.

---

## Template: `CONTEXT.md`

```markdown
# Stratum — Project Context

> This file is the single source of truth for any agent or developer resuming work on Stratum.
> **Read this file completely before writing any code or making any decisions.**
> Update this file after every significant decision, completed phase, or architectural change.

## Current Status

**Phase:** [e.g. Phase 1 — Backend Foundation]
**Last Updated:** [DATE]
**What was just completed:** [SHORT DESCRIPTION]
**What to do next:** [SHORT DESCRIPTION]

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

[Paste current top-level directory tree]

## Environment Setup

1. Copy .env.example to .env and fill values
2. Run: make dev-up
3. Run: make db-migrate
4. Frontend: http://localhost:3000
5. Backend: http://localhost:8000
6. API Docs: http://localhost:8000/docs
7. Flower: http://localhost:5555

## Completed Work

### Phase 1 — [DATE]
- [List of completed items]

## Open Decisions

| Decision | Options | Status |
|----------|---------|--------|
| [e.g. SSE vs WebSocket] | SSE simpler, WS bidirectional | Chose WebSocket |

## Known Issues / Tech Debt

- [List any known issues with their location and severity]

## Key Design Decisions

### Undo Strategy
NOT using open transactions. Using snapshot-based inverse SQL generation.
See: apps/backend/app/services/undo_engine.py

### Connection Pooling
Each (user_id, connection_id) pair gets its own asyncpg pool.
Pool released after 5 minutes idle. Max 20 pools per backend instance.
See: apps/backend/app/services/connection_pool.py

### SQL Analysis
All SQL analysis uses sqlglot. No regex parsing anywhere.
See: apps/backend/app/services/sql_analyzer.py

### Result Streaming
Server-side asyncpg cursors. 100 rows per batch streamed via WebSocket.
Never load full result sets into memory.
See: apps/backend/app/services/result_streamer.py

### Security
- DB credentials encrypted with Fernet before storage
- Encryption key loaded from env, never hardcoded
- Credentials never appear in API responses or logs
- Connection strings never in URLs or localStorage

## API Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/auth/login | Get JWT tokens |
| GET | /api/v1/connections | List connections |
| POST | /api/v1/queries/execute | Submit query |
| WS | /ws/queries/{id} | Stream results |
| POST | /api/v1/undo/{id}/execute | Execute undo |
[... continue for all endpoints]

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
- Helm chart: deploy/helm/stratum/
- Docker images: ghcr.io/your-org/stratum/{frontend,backend,worker}
- Ingress: NGINX with cert-manager

## Environment Variables

[List all required env vars with descriptions, no values]
```

---

## Template: `ARCHITECTURE.md`

```markdown
# Stratum — Architecture Decisions Record

## ADR-001: SQL Analysis Library
**Decision:** Use sqlglot, never regex
**Reason:** Regex cannot reliably parse SQL. sqlglot provides AST-level analysis.
**Date:** [DATE]
**Status:** Accepted

## ADR-002: Undo Strategy
**Decision:** Snapshot-based inverse SQL generation
**Reason:** Long-running open transactions cause lock contention and don't survive
backend restarts. Inverse SQL is safe, auditable, and TTL-manageable.
**Date:** [DATE]
**Status:** Accepted

## ADR-003: Result Streaming
**Decision:** WebSocket with asyncpg server-side cursors
**Reason:** SSE is unidirectional; WebSocket allows cancel signals.
Cursors prevent loading millions of rows into memory.
**Date:** [DATE]
**Status:** Accepted

## ADR-004: Connection Pool Strategy
**Decision:** Per (user_id, connection_id) asyncpg pools
**Reason:** Shared global pool risks cross-user query interference.
Per-user pools isolated, TTL-released, max 5 connections each.
**Date:** [DATE]
**Status:** Accepted

## ADR-005: Credential Storage
**Decision:** Fernet symmetric encryption, key from environment
**Reason:** Must store credentials for reconnection without asking user each time.
Fernet is authenticated encryption, safe for database storage.
**Date:** [DATE]
**Status:** Accepted

[Add new ADRs as decisions are made]
```

---

## Template: `TODO.md`

```markdown
# Stratum — Build TODO

## Phase 1 — Core (Target: [DATE])

### Infrastructure
- [ ] Monorepo directory structure
- [ ] docker-compose.yml with all services
- [ ] .env.example
- [ ] Makefile with dev commands
- [ ] Backend Dockerfile
- [ ] Frontend Dockerfile

### Backend — Foundation
- [ ] FastAPI app setup with structlog, CORS, Sentry
- [ ] SQLAlchemy async engine + session
- [ ] All database models
- [ ] Alembic initial migration
- [ ] Pydantic settings from env

### Backend — Auth
- [ ] User model + registration endpoint
- [ ] Login endpoint + JWT generation
- [ ] Refresh token (HTTP-only cookie)
- [ ] Auth middleware/dependency
- [ ] Session tracking

### Backend — Connections
- [ ] DbConnection model
- [ ] Fernet encryption service
- [ ] Connection CRUD endpoints
- [ ] Connection test endpoint
- [ ] asyncpg pool manager

### Backend — SQL Engine
- [ ] SQLAnalyzer with sqlglot
- [ ] Transaction wrapping logic
- [ ] Risk level detection
- [ ] Missing WHERE clause detection

### Backend — Query Execution
- [ ] Celery setup with Redis
- [ ] QueryExecutor service
- [ ] execute_query_task Celery task
- [ ] WebSocket manager with Redis pub/sub
- [ ] WS endpoint /ws/queries/{id}
- [ ] Cancel endpoint + signal mechanism
- [ ] Result pagination endpoint

### Backend — Schema Explorer
- [ ] SchemaService (list schemas/tables/columns/indexes)
- [ ] Redis caching for schema responses
- [ ] Schema endpoints

### Backend — History
- [ ] QueryHistory CRUD
- [ ] History list endpoint (paginated)
- [ ] History detail endpoint

### Backend — Support
- [ ] SupportRequest model
- [ ] Support submission endpoint

### Frontend — Foundation
- [ ] Nuxt 4 project setup
- [ ] TailwindCSS + shadcn-vue
- [ ] Pinia stores
- [ ] TanStack Vue Query setup
- [ ] Theme system (light/dark/system)
- [ ] CSS variables

### Frontend — Auth Pages
- [ ] Login page
- [ ] Register page
- [ ] Auth middleware
- [ ] Auth store with JWT handling

### Frontend — Layout
- [ ] App shell with splitpanes
- [ ] Navbar component
- [ ] Resizable panels

### Frontend — Editor
- [ ] Monaco Editor component (pgsql syntax)
- [ ] Tab bar with persistence
- [ ] Run button + keyboard shortcut
- [ ] Format SQL button
- [ ] Auto-transaction badge

### Frontend — Explorer
- [ ] DB tree component
- [ ] Lazy-load schema nodes
- [ ] Table right-click context menu

### Frontend — Results
- [ ] Virtual scroll results table
- [ ] WebSocket connection for streaming
- [ ] Row batch append
- [ ] Execution metadata bar
- [ ] Error display

### Frontend — History
- [ ] History list component
- [ ] Load SQL into editor from history
- [ ] Undo button per item

### Frontend — Connection
- [ ] Connection modal
- [ ] Test connection flow
- [ ] Connection selector in navbar

## Phase 2 — Undo + Async (Target: [DATE])

- [ ] UndoEngine service (snapshot capture)
- [ ] Inverse SQL generation (UPDATE/DELETE/INSERT)
- [ ] Undo snapshot storage with TTL
- [ ] Undo preview endpoint
- [ ] Undo execute endpoint
- [ ] Undo button in results panel
- [ ] Undo preview modal in frontend
- [ ] Large query undo threshold enforcement
- [ ] Cleanup worker tasks (Celery Beat)

## Phase 3 — Production Hardening (Target: [DATE])

- [ ] Helm chart (all templates)
- [ ] HPA for workers
- [ ] Kubernetes CronJobs for cleanup
- [ ] Prometheus metrics
- [ ] Encrypted connection token sharing
- [ ] Rate limiting (via Redis)
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline (GitHub Actions)
```

---

## BUILD ORDER — EXECUTE IN SEQUENCE

Follow this exact sequence. Do not skip ahead.

1. Create `CONTEXT.md`, `ARCHITECTURE.md`, `TODO.md` at repo root
2. Create full directory structure (all folders, empty `__init__.py` / `.gitkeep` files)
3. Create `docker-compose.yml` + `.env.example` + `Makefile`
4. Backend: FastAPI app shell + config + logging + middleware
5. Backend: SQLAlchemy models + Alembic migration
6. Backend: Auth service + endpoints
7. Backend: Encryption service + Connection service + endpoints
8. Backend: SQLAnalyzer with sqlglot
9. Backend: ConnectionPoolManager with asyncpg
10. Backend: QueryExecutor (sync first, test it works)
11. Backend: Celery setup + execute_query_task
12. Backend: WebSocket manager + Redis pub/sub
13. Backend: SchemaService + endpoints
14. Backend: History + Support endpoints
15. Backend: UndoEngine (snapshot capture + inverse SQL generation)
16. Frontend: Nuxt 4 + Tailwind + shadcn-vue setup
17. Frontend: Auth pages + store
18. Frontend: App shell layout with splitpanes
19. Frontend: Monaco Editor component
20. Frontend: Tab bar + editor store
21. Frontend: DB Explorer tree
22. Frontend: Results table with virtual scroller
23. Frontend: WebSocket integration for query streaming
24. Frontend: History panel
25. Frontend: Connection modal
26. Frontend: Undo preview modal + undo flow
27. Deploy: Docker images
28. Deploy: Helm chart
29. Deploy: Kubernetes manifests
30. Tests: Unit tests for SQL analyzer, undo engine, connection pool
31. Tests: Integration tests for query execution

After each step: update `TODO.md` (mark done), update `CONTEXT.md` (current status).

---

## CRITICAL DO-NOTS

Never do any of the following, regardless of how it might seem simpler:

- ❌ Use regex to parse SQL — use sqlglot
- ❌ Load full query result sets into memory — use cursor pagination
- ❌ Store credentials in plaintext — use Fernet encryption
- ❌ Put connection URLs in browser URLs or localStorage
- ❌ Use long-running open transactions for undo — use snapshot-based inverse SQL
- ❌ Use browser localStorage for query history — server-side only
- ❌ Expose raw passwords in API responses at any point
- ❌ Ignore statement timeouts — always set them
- ❌ Build multi-database support — PostgreSQL only for MVP
- ❌ Run Celery Beat with more than 1 replica — it must be singleton
- ❌ Skip updating CONTEXT.md after completing a phase
- ❌ Hacker-themed UI (green-on-black, terminal aesthetics) — SaaS professional only

---

*End of Stratum Build Prompt — Version 1.0*
*Application: Stratum — The Professional PostgreSQL Workspace*
```
