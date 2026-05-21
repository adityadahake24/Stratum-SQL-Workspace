import json
import uuid
from typing import List, Optional

import asyncpg
import structlog

from app.schemas.schema_explorer import SchemaInfo, TableInfo, ColumnInfo, IndexInfo, FKInfo

logger = structlog.get_logger(__name__)


class SchemaService:
    async def list_schemas(self, pool: asyncpg.Pool) -> List[SchemaInfo]:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT schema_name, schema_owner
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                ORDER BY schema_name
            """)
        return [SchemaInfo(name=r["schema_name"], owner=r["schema_owner"]) for r in rows]

    async def list_tables(self, pool: asyncpg.Pool, schema: str) -> List[TableInfo]:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT
                    t.table_name,
                    t.table_type,
                    pg_stat_get_live_tuples(c.oid)::bigint AS row_estimate,
                    obj_description(c.oid) AS comment
                FROM information_schema.tables t
                LEFT JOIN pg_class c ON c.relname = t.table_name
                LEFT JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.table_schema
                WHERE t.table_schema = $1
                ORDER BY t.table_name
            """, schema)
        return [
            TableInfo(
                name=r["table_name"],
                schema=schema,
                table_type=r["table_type"],
                row_estimate=r["row_estimate"],
                comment=r["comment"],
            )
            for r in rows
        ]

    async def list_columns(self, pool: asyncpg.Pool, schema: str, table: str) -> List[ColumnInfo]:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT
                    c.column_name,
                    c.data_type,
                    c.is_nullable = 'YES' AS is_nullable,
                    c.column_default,
                    c.ordinal_position,
                    EXISTS (
                        SELECT 1 FROM information_schema.table_constraints tc
                        JOIN information_schema.constraint_column_usage ccu
                            ON tc.constraint_name = ccu.constraint_name
                        WHERE tc.constraint_type = 'PRIMARY KEY'
                          AND tc.table_schema = c.table_schema
                          AND tc.table_name = c.table_name
                          AND ccu.column_name = c.column_name
                    ) AS is_primary_key
                FROM information_schema.columns c
                WHERE c.table_schema = $1 AND c.table_name = $2
                ORDER BY c.ordinal_position
            """, schema, table)
        return [
            ColumnInfo(
                name=r["column_name"],
                data_type=r["data_type"],
                is_nullable=r["is_nullable"],
                column_default=r["column_default"],
                ordinal_position=r["ordinal_position"],
                is_primary_key=r["is_primary_key"],
            )
            for r in rows
        ]

    async def list_indexes(self, pool: asyncpg.Pool, schema: str, table: str) -> List[IndexInfo]:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT
                    i.relname AS index_name,
                    ix.indisunique AS is_unique,
                    ix.indisprimary AS is_primary,
                    array_agg(a.attname ORDER BY k.n) AS columns
                FROM pg_class t
                JOIN pg_index ix ON ix.indrelid = t.oid
                JOIN pg_class i ON i.oid = ix.indexrelid
                JOIN pg_namespace n ON n.oid = t.relnamespace
                CROSS JOIN unnest(ix.indkey) WITH ORDINALITY AS k(attnum, n)
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum
                WHERE t.relname = $1 AND n.nspname = $2
                GROUP BY i.relname, ix.indisunique, ix.indisprimary
                ORDER BY i.relname
            """, table, schema)
        return [
            IndexInfo(
                name=r["index_name"],
                columns=list(r["columns"]),
                is_unique=r["is_unique"],
                is_primary=r["is_primary"],
            )
            for r in rows
        ]

    async def list_foreign_keys(self, pool: asyncpg.Pool, schema: str, table: str) -> List[FKInfo]:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table,
                    ccu.column_name AS foreign_column
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = $1
                  AND tc.table_name = $2
            """, schema, table)
        return [
            FKInfo(
                constraint_name=r["constraint_name"],
                column_name=r["column_name"],
                foreign_table=r["foreign_table"],
                foreign_column=r["foreign_column"],
            )
            for r in rows
        ]

    async def get_table_row_count_estimate(self, pool: asyncpg.Pool, schema: str, table: str) -> int:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT reltuples::bigint AS estimate
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = $1 AND n.nspname = $2
            """, table, schema)
        return row["estimate"] if row else 0


schema_service = SchemaService()
