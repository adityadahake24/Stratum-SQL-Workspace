from prometheus_client import Counter, Histogram, Gauge

queries_executed_total = Counter(
    "stratum_queries_executed_total",
    "Total number of queries submitted for execution",
    ["status"],
)

query_duration_seconds = Histogram(
    "stratum_query_duration_seconds",
    "Query execution wall-clock time in seconds",
    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120],
)

undo_operations_total = Counter(
    "stratum_undo_operations_total",
    "Total undo operations executed",
    ["status"],
)

connections_tested_total = Counter(
    "stratum_connections_tested_total",
    "Total connection tests performed",
    ["result"],
)

active_ws_connections = Gauge(
    "stratum_active_ws_connections",
    "Number of currently open WebSocket connections",
)

auth_attempts_total = Counter(
    "stratum_auth_attempts_total",
    "Total authentication attempts",
    ["action", "result"],
)
