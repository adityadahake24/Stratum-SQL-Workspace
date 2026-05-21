import uuid
import json
import time
from datetime import datetime, timezone
from typing import Callable, Optional, List, Any

import asyncpg
import structlog

from app.config import settings
from app.services.sql_analyzer import sql_analyzer, SQLAnalysisResult
from app.services.undo_engine import undo_engine

logger = structlog.get_logger(__name__)

ROW_BATCH_SIZE = 100


class QueryExecutor:
    async def execute(
        self,
        pool: asyncpg.Pool,
        sql: str,
        analysis: SQLAnalysisResult,
        execution_id: str,
        publish_fn: Callable,
    ) -> dict:
        start_time = time.perf_counter()
        result = {
            "status": "error",
            "row_count": 0,
            "rows_affected": 0,
            "execution_time_ms": 0,
            "columns": [],
            "error": None,
            "has_undo": False,
            "undo_snapshot": None,
        }

        try:
            async with pool.acquire() as conn:
                await conn.execute(f"SET statement_timeout = '{settings.max_query_runtime_seconds * 1000}'")

                pre_snapshot = None
                if analysis.undo_eligible and analysis.statement_types[0] in ("UPDATE", "DELETE"):
                    pre_snapshot = await undo_engine.capture_pre_snapshot(pool, sql, analysis)

                exec_sql = sql
                if analysis.needs_transaction_wrap:
                    exec_sql = f"BEGIN;\n{sql.strip().rstrip(';')};\nCOMMIT;"

                if analysis.is_read_only:
                    # Use server-side cursor for streaming
                    rows_collected = []
                    columns = []
                    batch_number = 0

                    async with conn.transaction():
                        cursor = await conn.cursor(sql)
                        batch = await cursor.fetch(ROW_BATCH_SIZE)
                        if batch:
                            columns = list(batch[0].keys())
                        while batch:
                            batch_number += 1
                            row_data = [list(r.values()) for r in batch]
                            rows_collected.extend(row_data)
                            await publish_fn({
                                "type": "row_batch",
                                "columns": columns,
                                "rows": row_data,
                                "batch_number": batch_number,
                                "total_so_far": len(rows_collected),
                            })
                            if len(rows_collected) >= settings.max_result_rows:
                                await publish_fn({"type": "warning", "message": f"Result truncated at {settings.max_result_rows} rows"})
                                break
                            batch = await cursor.fetch(ROW_BATCH_SIZE)

                    result["columns"] = columns
                    result["row_count"] = len(rows_collected)
                    result["rows_affected"] = 0

                else:
                    # DML / DDL — execute and capture affected rows
                    stmt_result = await conn.execute(exec_sql)
                    rows_affected = self._parse_rows_affected(stmt_result)

                    # Handle INSERT undo via RETURNING if needed
                    if analysis.undo_eligible and analysis.statement_types[0] == "INSERT":
                        pre_snapshot = await self._capture_insert_snapshot(
                            conn, sql, analysis, pool
                        )

                    result["rows_affected"] = rows_affected
                    result["row_count"] = rows_affected

                    if pre_snapshot and pre_snapshot.get("rows") is not None:
                        result["has_undo"] = True
                        result["undo_snapshot"] = pre_snapshot

                elapsed_ms = int((time.perf_counter() - start_time) * 1000)
                result["status"] = "complete"
                result["execution_time_ms"] = elapsed_ms

                await publish_fn({
                    "type": "complete",
                    "execution_time_ms": elapsed_ms,
                    "row_count": result["row_count"],
                    "rows_affected": result["rows_affected"],
                    "has_undo": result["has_undo"],
                    "columns": result["columns"],
                })

        except asyncpg.QueryCanceledError:
            result["status"] = "cancelled"
            result["error"] = "Query was cancelled"
            await publish_fn({"type": "cancelled"})
        except asyncpg.PostgresError as e:
            result["status"] = "error"
            result["error"] = str(e)
            await publish_fn({"type": "error", "message": str(e), "code": e.sqlstate if hasattr(e, "sqlstate") else "pg_error"})
        except Exception as e:
            logger.error("query_executor_error", error=str(e), execution_id=execution_id)
            result["status"] = "error"
            result["error"] = str(e)
            await publish_fn({"type": "error", "message": "Internal execution error", "code": "internal_error"})

        result["execution_time_ms"] = int((time.perf_counter() - start_time) * 1000)
        return result

    def _parse_rows_affected(self, result_str: str) -> int:
        try:
            parts = result_str.split()
            return int(parts[-1]) if parts else 0
        except (ValueError, IndexError):
            return 0

    async def _capture_insert_snapshot(self, conn, sql: str, analysis: SQLAnalysisResult, pool) -> Optional[dict]:
        table_ref = analysis.target_tables[0] if analysis.target_tables else None
        if not table_ref:
            return None
        schema_name = "public"
        table_name = table_ref
        if "." in table_ref:
            schema_name, table_name = table_ref.split(".", 1)
        return {
            "operation_type": "INSERT",
            "table_name": table_name,
            "schema_name": schema_name,
            "rows": [],  # INSERT undo uses RETURNING-captured PKs
        }


query_executor = QueryExecutor()
