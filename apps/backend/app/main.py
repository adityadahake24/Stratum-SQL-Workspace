import sentry_sdk
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.core.middleware import RequestIDMiddleware, TimingMiddleware
from app.core.exceptions import register_exception_handlers
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api.v1.router import api_router
from app.api.v1.ws import ws_router
from app.db.base import engine
from app.db.session import Base

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("stratum_startup", environment=settings.environment)
    yield
    await engine.dispose()
    logger.info("stratum_shutdown")


if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=0.1,
    )

_DESCRIPTION = """
## Stratum — Professional PostgreSQL Workspace

> The professional PostgreSQL workspace for teams who take data seriously.

Stratum exposes a versioned REST API (`/api/v1/`) alongside a **WebSocket endpoint**
for live, row-by-row query streaming. All REST responses use `application/json`.

---

### Authentication

Authenticated endpoints require a **Bearer JWT** in the `Authorization` header.

| Token | Lifetime | Transport |
|---|---|---|
| Access (JWT HS256) | Configurable (default 15 min prod / 7 days dev) | `Authorization: Bearer <token>` |
| Refresh (opaque) | 7 days | `HttpOnly` cookie on `/api/v1/auth` path |

---

### Rate Limits (per IP)

| Endpoint | Limit |
|---|---|
| `POST /api/v1/auth/register` | 10 / min |
| `POST /api/v1/auth/login` | 20 / min |
| `POST /api/v1/queries/execute` | 30 / min |

Exceeding a limit returns **429 Too Many Requests**.

---

### WebSocket — Query Streaming

After calling `POST /api/v1/queries/execute`, connect to:

```
ws://<host>/ws/query/{execution_id}?token=<access_token>
```

The server pushes `columns`, `rows` (100 per batch), `complete`, `error`, and `cancelled`
messages. Send `{"type":"cancel"}` to stop execution mid-stream.

---

### Useful links

- [Full API Reference](../docs/api.md)
- [Prometheus Metrics](/metrics)
- [Health Check](/health)
"""

app = FastAPI(
    title="Stratum",
    description=_DESCRIPTION,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Stratum",
        "url": "https://github.com/your-org/stratum",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "auth", "description": "Registration, login, token refresh, logout"},
        {"name": "connections", "description": "PostgreSQL connection CRUD, test, and token sharing"},
        {"name": "queries", "description": "SQL execution, status polling, and cancellation"},
        {"name": "schema", "description": "Schema + table introspection (Redis-cached 60 s)"},
        {"name": "history", "description": "Per-user query execution history"},
        {"name": "undo", "description": "Snapshot-based inverse SQL undo for DML statements"},
        {"name": "support", "description": "In-app support requests"},
    ],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)

app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment}
