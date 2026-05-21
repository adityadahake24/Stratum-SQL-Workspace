import json
import uuid
import zlib
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

import asyncpg
import structlog

from app.config import settings
from app.services.sql_analyzer import SQLAnalysisResult
from app.schemas.undo import UndoPreviewResponse

logger = structlog.get_logger(__name__)

UNDO_TTL_HOURS = 24
MAX_UNDO_SIZE_MB = 500


class UndoEngine:
    async def capture_pre_snapshot(
        self,
        pool: asyncpg.Pool,
        sql: str,
        analysis: SQLAnalysisResult,
    ) -> Optional[Dict]:
        if not analysis.undo_eligible or not analysis.target_tables:
            return None

        operation_type = analysis.statement_types[0]  # single DML type guaranteed
        table_ref = analysis.target_tables[0]

        schema_name = "public"
        table_name = table_ref
        if "." in table_ref:
            schema_name, table_name = table_ref.split(".", 1)

        try:
            if operation_type == "INSERT":
                # For INSERT, we capture PKs after execution via RETURNING
                # Return metadata only — actual snapshot done post-execution
                return {
                    "operation_type": "INSERT",
                    "table_name": table_name,
                    "schema_name": schema_name,
                    "rows": None,  # filled after execution
                }

            # For UPDATE and DELETE, capture affected rows before execution
            pre_select = self._build_pre_select(sql, operation_type, schema_name, table_name)
            if not pre_select:
                return None

            async with pool.acquire() as conn:
                rows = await conn.fetch(f"SELECT * FROM {schema_name}.{table_name} WHERE ctid IN (SELECT ctid FROM ({pre_select}) sub)")

                if len(rows) > settings.undo_max_rows_threshold:
                    logger.warning(
                        "undo_threshold_exceeded",
                        row_count=len(rows),
                        threshold=settings.undo_max_rows_threshold,
                    )
                    return None

                row_dicts = [dict(r) for r in rows]

                # Serialize + check size
                serialized = json.dumps(row_dicts, default=str).encode()
                if len(serialized) > MAX_UNDO_SIZE_MB * 1024 * 1024:
                    logger.warning("undo_size_exceeded", size_bytes=len(serialized))
                    return None

                compressed = zlib.compress(serialized, level=6)
                return {
                    "operation_type": operation_type,
                    "table_name": table_name,
                    "schema_name": schema_name,
                    "rows": row_dicts,
                    "snapshot_data": compressed,
                    "snapshot_size_bytes": len(compressed),
                    "row_count": len(row_dicts),
                }

        except Exception as e:
            logger.error("undo_snapshot_failed", error=str(e))
            return None

    def _build_pre_select(self, sql: str, operation_type: str, schema: str, table: str) -> Optional[str]:
        """Build a SELECT that identifies rows that would be affected."""
        sql_stripped = sql.strip().rstrip(";")
        if operation_type == "UPDATE":
            # Extract WHERE clause from UPDATE
            upper = sql_stripped.upper()
            where_idx = upper.find(" WHERE ")
            if where_idx >= 0:
                where_clause = sql_stripped[where_idx:]
                return f"SELECT ctid FROM {schema}.{table}{where_clause}"
            else:
                # No WHERE — all rows (risky but valid)
                return f"SELECT ctid FROM {schema}.{table}"
        elif operation_type == "DELETE":
            upper = sql_stripped.upper()
            where_idx = upper.find(" WHERE ")
            if where_idx >= 0:
                where_clause = sql_stripped[where_idx:]
                return f"SELECT ctid FROM {schema}.{table}{where_clause}"
            else:
                return f"SELECT ctid FROM {schema}.{table}"
        return None

    async def generate_inverse_sql(
        self,
        operation_type: str,
        table_name: str,
        schema_name: str,
        rows: List[Dict[str, Any]],
        inserted_pks: Optional[List] = None,
        pk_column: str = "id",
    ) -> str:
        if not rows and not inserted_pks:
            return ""

        if operation_type == "UPDATE":
            statements = []
            for row in rows:
                pk_val = row.get(pk_column)
                if pk_val is None:
                    continue
                set_parts = []
                for col, val in row.items():
                    if col == pk_column:
                        continue
                    if val is None:
                        set_parts.append(f"{col} = NULL")
                    elif isinstance(val, str):
                        escaped = val.replace("'", "''")
                        set_parts.append(f"{col} = '{escaped}'")
                    elif isinstance(val, bool):
                        set_parts.append(f"{col} = {str(val).upper()}")
                    else:
                        set_parts.append(f"{col} = {val}")
                if set_parts:
                    stmt = f"UPDATE {schema_name}.{table_name} SET {', '.join(set_parts)} WHERE {pk_column} = '{pk_val}';"
                    statements.append(stmt)
            return "\n".join(statements)

        elif operation_type == "DELETE":
            if not rows:
                return ""
            columns = list(rows[0].keys())
            col_list = ", ".join(columns)
            value_rows = []
            for row in rows:
                vals = []
                for col in columns:
                    v = row[col]
                    if v is None:
                        vals.append("NULL")
                    elif isinstance(v, str):
                        escaped = v.replace("'", "''")
                        vals.append(f"'{escaped}'")
                    elif isinstance(v, bool):
                        vals.append(str(v).upper())
                    else:
                        vals.append(str(v))
                value_rows.append(f"({', '.join(vals)})")
            return f"INSERT INTO {schema_name}.{table_name} ({col_list}) VALUES\n" + ",\n".join(value_rows) + ";"

        elif operation_type == "INSERT":
            if not inserted_pks:
                return ""
            pk_list = ", ".join(f"'{pk}'" for pk in inserted_pks)
            return f"DELETE FROM {schema_name}.{table_name} WHERE {pk_column} IN ({pk_list});"

        return ""

    async def get_pk_column(self, pool: asyncpg.Pool, schema: str, table: str) -> str:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
                  AND tc.table_schema = $1
                  AND tc.table_name = $2
                LIMIT 1
            """, schema, table)
        return row["column_name"] if row else "id"


undo_engine = UndoEngine()
