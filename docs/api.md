# Stratum API Reference

> **Stratum** — Professional PostgreSQL workspace for teams who take data seriously.
>
> Base URL (local): `http://localhost:8000`  
> Interactive docs: `http://localhost:8000/docs` (Swagger UI)  
> Alternative docs: `http://localhost:8000/redoc` (ReDoc)

---

## Overview

Stratum exposes a versioned REST API (`/api/v1/`) alongside a WebSocket endpoint for live query streaming. All REST responses use `application/json`. Authenticated endpoints require a `Bearer` JWT in the `Authorization` header.

### Architecture at a glance

```
Browser ──REST──▶ FastAPI /api/v1/...
        ──WS───▶  /ws/query/{execution_id}
                       │
              Celery worker ──asyncpg──▶ User's PostgreSQL
                       │
                   Redis pub/sub
                       │
              WebSocket pushes rows back to browser
```

### Authentication model

| Token | Lifetime | Transport |
|---|---|---|
| Access token (JWT, HS256) | 15 min (prod) / 7 days (dev) | `Authorization: Bearer <token>` header |
| Refresh token (opaque) | 7 days | `HttpOnly` cookie on `/api/v1/auth` path |

---

## Rate Limits

Limits are applied per client IP address via `slowapi`.

| Endpoint | Limit |
|---|---|
| `POST /api/v1/auth/register` | 10 requests / minute |
| `POST /api/v1/auth/login` | 20 requests / minute |
| `POST /api/v1/queries/execute` | 30 requests / minute |

Exceeding a limit returns **429 Too Many Requests**:
```json
{ "detail": "Rate limit exceeded: 30 per 1 minute" }
```

---

## Error Format

All errors follow a consistent envelope:

```json
{
  "detail": "Human-readable error message"
}
```

### Common status codes

| Code | Meaning |
|---|---|
| `400` | Validation error / bad request body |
| `401` | Missing or invalid access token |
| `403` | Action not allowed for this resource |
| `404` | Resource not found (or belongs to another user) |
| `409` | Conflict (duplicate email, undo already consumed) |
| `410` | Gone (undo snapshot expired) |
| `422` | Unprocessable entity (Pydantic validation) |
| `429` | Rate limit exceeded |
| `500` | Internal server error |

---

## Endpoints

### Health

#### `GET /health`

Returns service liveness. No authentication required.

**Response `200`**
```json
{ "status": "ok", "environment": "development" }
```

---

### Auth — `/api/v1/auth`

#### `POST /api/v1/auth/register`

Create a new Stratum account.

**Body**
```json
{
  "email": "you@example.com",
  "password": "StrongPass1!"
}
```

**Response `201`**
```json
{
  "id": "uuid",
  "email": "you@example.com",
  "is_active": true,
  "created_at": "2026-05-21T10:00:00Z"
}
```

---

#### `POST /api/v1/auth/login`

Exchange credentials for an access token. Sets an `HttpOnly` refresh cookie.

**Body**
```json
{
  "email": "you@example.com",
  "password": "StrongPass1!"
}
```

**Response `200`**
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

---

#### `POST /api/v1/auth/refresh`

Use the `refresh_token` cookie to obtain a new access token.

**Response `200`**
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

---

#### `POST /api/v1/auth/logout`

Revoke the refresh token and clear the cookie.

**Response `200`**
```json
{ "message": "Logged out" }
```

---

#### `GET /api/v1/auth/me`

Return the currently authenticated user. Requires Bearer token.

**Response `200`**
```json
{
  "id": "uuid",
  "email": "you@example.com",
  "is_active": true,
  "created_at": "2026-05-21T10:00:00Z"
}
```

---

### Connections — `/api/v1/connections`

Manage PostgreSQL connections. Credentials are encrypted with Fernet before storage; passwords are never returned in responses.

#### `GET /api/v1/connections`

List all connections for the authenticated user.

**Response `200`** — array of connection objects (no `password` field).

---

#### `POST /api/v1/connections`

Create a new connection.

**Body**
```json
{
  "name": "Production DB",
  "host": "db.example.com",
  "port": 5432,
  "database": "myapp",
  "username": "readonly",
  "password": "secret",
  "ssl_mode": "require"
}
```

**Response `201`** — created connection object.

---

#### `GET /api/v1/connections/{id}`

Get a single connection by UUID.

---

#### `PUT /api/v1/connections/{id}`

Update connection metadata. Accepts any subset of the creation fields.

---

#### `DELETE /api/v1/connections/{id}`

Delete a connection. Returns **204 No Content**.

---

#### `POST /api/v1/connections/{id}/test`

Test a saved connection by pinging the database.

**Response `200`**
```json
{
  "success": true,
  "message": "PostgreSQL 16.2",
  "latency_ms": 4.2
}
```

---

#### `POST /api/v1/connections/test-temp`

Test raw credentials without saving. Useful for the connection creation modal.

**Body** — same as `POST /api/v1/connections`.

**Response `200`** — same as `/test` above.

---

#### `POST /api/v1/connections/{id}/token`

Generate a short-lived encrypted share token for this connection.

**Response `200`**
```json
{ "token": "<encrypted-base64>", "expires_at": "2026-05-21T11:00:00Z" }
```

---

#### `GET /api/v1/connections/token/{token}`

Resolve a share token back to connection metadata (without password).

---

### Queries — `/api/v1/queries`

#### `POST /api/v1/queries/execute`

Submit a SQL statement for async execution via Celery.

**Body**
```json
{
  "connection_id": "uuid",
  "sql": "SELECT * FROM orders LIMIT 100;"
}
```

**Response `202`**
```json
{
  "execution_id": "uuid",
  "history_id": "uuid",
  "status": "queued",
  "analysis": {
    "statement_types": ["SELECT"],
    "tables": ["orders"],
    "is_read_only": true,
    "has_where_clause": false,
    "is_transaction": false,
    "risk_level": "low"
  }
}
```

After receiving `execution_id`, connect to the WebSocket to stream results in real time.

---

#### `GET /api/v1/queries/executions/{execution_id}`

Poll execution status. Use as a fallback when WebSocket is unavailable.

**Response `200`**
```json
{
  "id": "uuid",
  "status": "complete",
  "progress_pct": 100,
  "started_at": "...",
  "completed_at": "..."
}
```

---

#### `POST /api/v1/queries/executions/{execution_id}/cancel`

Send a cancellation signal. The worker stops streaming and marks the execution `cancelled`.

---

### Schema — `/api/v1/schema`

#### `GET /api/v1/schema/{connection_id}`

List all schemas in the database. Results are Redis-cached for 60 seconds.

#### `GET /api/v1/schema/{connection_id}/{schema}`

List tables and views inside a schema.

#### `GET /api/v1/schema/{connection_id}/{schema}/{table}`

Return column definitions for a table.

---

### History — `/api/v1/history`

#### `GET /api/v1/history`

Paginated query history for the current user.

**Query params:** `connection_id`, `limit` (default 50), `offset`.

#### `GET /api/v1/history/{id}`

Single history entry with execution metadata.

---

### Undo — `/api/v1/undo`

Undo is available for `INSERT`, `UPDATE`, and `DELETE` statements that affected fewer than `UNDO_MAX_ROWS_THRESHOLD` rows. Snapshots expire after 24 hours.

#### `GET /api/v1/undo/{history_id}/preview`

Preview the inverse SQL that will be executed.

**Response `200`**
```json
{
  "history_id": "uuid",
  "operation_type": "UPDATE",
  "table_name": "users",
  "row_count": 3,
  "inverse_sql": "UPDATE users SET name = 'Alice' WHERE id = 1; ...",
  "expires_at": "2026-05-22T10:00:00Z",
  "is_consumed": false
}
```

#### `POST /api/v1/undo/{history_id}/execute`

Execute the inverse SQL. The snapshot is marked consumed and cannot be reused.

**Response `200`**
```json
{
  "success": true,
  "execution_id": "uuid",
  "message": "Undo executed successfully"
}
```

---

### Support — `/api/v1/support`

#### `POST /api/v1/support`

Submit a support request or feedback.

**Body**
```json
{
  "subject": "Query timeout",
  "body": "Long-running queries are timing out after 60 seconds.",
  "category": "bug"
}
```

---

## WebSocket — Query Streaming

Connect after calling `POST /api/v1/queries/execute`.

```
ws://localhost:8000/ws/query/{execution_id}?token=<access_token>
```

### Message types (server → client)

#### `status`
```json
{ "type": "status", "status": "running", "started_at": "..." }
```

#### `columns`
```json
{ "type": "columns", "columns": ["id", "name", "email"] }
```

#### `rows`
```json
{
  "type": "rows",
  "rows": [[1, "Alice", "a@b.com"], [2, "Bob", "b@c.com"]],
  "batch": 1
}
```

#### `complete`
```json
{
  "type": "complete",
  "status": "complete",
  "row_count": 1024,
  "rows_affected": 0,
  "execution_time_ms": 142,
  "has_undo": false
}
```

#### `error`
```json
{ "type": "error", "error": "relation \"foo\" does not exist" }
```

#### `cancelled`
```json
{ "type": "cancelled" }
```

### Message types (client → server)

#### `cancel`
```json
{ "type": "cancel" }
```

---

## Observability

| Endpoint | Description |
|---|---|
| `GET /health` | Liveness check |
| `GET /metrics` | Prometheus metrics (text/plain) |

### Custom Prometheus metrics

| Metric | Type | Labels |
|---|---|---|
| `stratum_queries_executed_total` | Counter | `status` |
| `stratum_query_duration_seconds` | Histogram | — |
| `stratum_undo_operations_total` | Counter | `status` |
| `stratum_connections_tested_total` | Counter | `result` |
| `stratum_active_ws_connections` | Gauge | — |
| `stratum_auth_attempts_total` | Counter | `action`, `result` |

---

## Pagination

List endpoints accept `limit` and `offset` query parameters. Default `limit` is 50.

```
GET /api/v1/history?limit=20&offset=40
```

---

## OpenAPI spec

The full machine-readable OpenAPI 3.1 spec is served at:

```
GET /openapi.json
```
