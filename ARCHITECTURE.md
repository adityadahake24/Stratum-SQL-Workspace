# Stratum — Architecture Decisions Record

## ADR-001: SQL Analysis Library
**Decision:** Use sqlglot, never regex
**Reason:** Regex cannot reliably parse SQL. sqlglot provides AST-level analysis enabling accurate statement type detection, table extraction, and WHERE clause detection.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-002: Undo Strategy
**Decision:** Snapshot-based inverse SQL generation
**Reason:** Long-running open transactions cause lock contention and don't survive backend restarts. Inverse SQL is safe, auditable, TTL-manageable, and doesn't block other operations.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-003: Result Streaming
**Decision:** WebSocket with asyncpg server-side cursors
**Reason:** SSE is unidirectional; WebSocket allows cancel signals. Cursors prevent loading millions of rows into memory. Batches of 100 rows keep memory bounded.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-004: Connection Pool Strategy
**Decision:** Per (user_id, connection_id) asyncpg pools
**Reason:** Shared global pool risks cross-user query interference. Per-user pools are isolated, TTL-released, and max 5 connections each.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-005: Credential Storage
**Decision:** Fernet symmetric encryption, key from environment
**Reason:** Must store credentials for reconnection without asking user each time. Fernet is authenticated encryption, safe for database storage. Key never hardcoded.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-006: Async Task Queue
**Decision:** Celery with Redis broker
**Reason:** Query execution can exceed request timeout limits. Celery enables async execution with progress streaming via Redis pub/sub. Beat scheduler handles cleanup.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-007: WebSocket State Distribution
**Decision:** Redis pub/sub for WebSocket message routing
**Reason:** Multiple backend pods need to publish query progress. Redis channels (stratum:ws:{execution_id}) allow any pod to publish, any pod to forward to the connected client.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-008: Schema Cache
**Decision:** Redis TTL cache (60 seconds) for schema introspection
**Reason:** Schema queries hit pg_catalog which can be slow. 60-second TTL provides fresh enough data while avoiding per-request overhead.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-009: Frontend Framework
**Decision:** Nuxt 4 + Vue 3 + Pinia + TanStack Query
**Reason:** SSR capability for production, file-based routing, Pinia for reactive store with localStorage persistence, TanStack Query for server state caching.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-010: SQL Editor
**Decision:** Monaco Editor (VSCode engine) with pgsql language
**Reason:** Best-in-class SQL editing experience with syntax highlighting, autocomplete, and keyboard shortcut support. @guolao/vue-monaco-editor for Vue integration.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-011: Result Virtualization
**Decision:** @vueuse/core useVirtualList for result table
**Reason:** Result sets can contain thousands of rows. Virtual scrolling renders only visible rows, keeping DOM performance bounded regardless of result size. Implemented via useVirtualList composable (30px fixed row height, 20-row overscan).
**Date:** 2026-05-21
**Status:** Accepted

## ADR-012: Resizable Panels
**Decision:** splitpanes for workspace layout
**Reason:** Lightweight, Vue-native panel splitter. Supports nested panels (vertical + horizontal split in center column).
**Date:** 2026-05-21
**Status:** Accepted

## ADR-013: Rate Limiting
**Decision:** slowapi (limits library) with IP-based key function
**Reason:** Protects auth and query endpoints from brute force and abuse without requiring Redis (in-memory store sufficient for single-instance; swap to Redis store for multi-replica).
**Date:** 2026-05-21
**Status:** Accepted

## ADR-014: Prometheus Metrics
**Decision:** prometheus_fastapi_instrumentator + custom prometheus_client counters/histograms in app/core/metrics.py
**Reason:** instrumentator auto-instruments all HTTP routes. Custom counters (queries_executed, undo_operations, query_duration_seconds, auth_attempts) give business-level visibility beyond HTTP metrics.
**Date:** 2026-05-21
**Status:** Accepted

## ADR-015: CI/CD Pipeline
**Decision:** GitHub Actions — two jobs (ci: lint+test, build-and-push: Docker images to GHCR)
**Reason:** GHCR is free for public repos and integrates natively with GitHub Actions GITHUB_TOKEN. Build job is gated on CI success and only runs on push (not PRs). Three separate image scopes (backend, worker, frontend) with GHA layer cache per scope.
**Date:** 2026-05-21
**Status:** Accepted
