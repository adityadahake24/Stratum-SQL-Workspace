import asyncio
import uuid
import json
import zlib
from datetime import datetime, timezone, timedelta

import structlog

from app.workers.celery_app import celery_app
from app.config import settings
from app.core.metrics import queries_executed_total, query_duration_seconds

logger = structlog.get_logger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    bind=True,
    name="app.workers.tasks.query_tasks.execute_query_task",
    max_retries=0,
    time_limit=70,
    soft_time_limit=65,
    acks_late=True,
)
def execute_query_task(self, execution_id: str, history_id: str, connection_id: str, user_id: str, sql: str):
    return _run_async(_execute_query_async(execution_id, history_id, connection_id, user_id, sql))


async def _execute_query_async(execution_id: str, history_id: str, connection_id: str, user_id: str, sql: str):
    from app.db.session import async_session_factory
    from app.models.query_execution import QueryExecution
    from app.models.query_history import QueryHistory
    from app.models.undo_snapshot import UndoSnapshot
    from app.services.connection_service import ConnectionService
    from app.services.connection_pool import pool_manager
    from app.services.sql_analyzer import sql_analyzer
    from app.services.query_executor import query_executor
    from app.services.undo_engine import undo_engine
    from app.websockets.manager import ws_manager
    from sqlalchemy import select

    async with async_session_factory() as session:
        # Update execution status → running
        result = await session.execute(
            select(QueryExecution).where(QueryExecution.id == uuid.UUID(execution_id))
        )
        execution = result.scalar_one_or_none()
        if execution:
            execution.status = "running"
            execution.started_at = datetime.now(timezone.utc)
            execution.worker_node = "celery"
            await session.commit()

        # Get connection + pool
        conn_service = ConnectionService(session)
        conn = await conn_service.get_connection(uuid.UUID(connection_id), uuid.UUID(user_id))
        credentials = conn_service.get_decrypted_credentials(conn)
        pool = await pool_manager.get_pool(uuid.UUID(user_id), uuid.UUID(connection_id), credentials)

        analysis = sql_analyzer.analyze(sql)

        # Publish function via Redis pub/sub
        async def publish(msg: dict):
            await ws_manager.publish(execution_id, msg)

        await publish({"type": "status", "status": "running", "started_at": datetime.now(timezone.utc).isoformat()})

        exec_result = await query_executor.execute(pool, sql, analysis, execution_id, publish)

        # Store undo snapshot if eligible
        has_undo = False
        if exec_result.get("undo_snapshot") and exec_result["undo_snapshot"].get("rows") is not None:
            snap_data = exec_result["undo_snapshot"]
            rows = snap_data.get("rows", [])
            operation_type = snap_data["operation_type"]
            table_name = snap_data["table_name"]
            schema_name = snap_data["schema_name"]

            pk_col = await undo_engine.get_pk_column(pool, schema_name, table_name)
            inverse_sql = await undo_engine.generate_inverse_sql(
                operation_type, table_name, schema_name, rows, pk_column=pk_col
            )

            snapshot = UndoSnapshot(
                id=uuid.uuid4(),
                history_id=uuid.UUID(history_id),
                user_id=uuid.UUID(user_id),
                operation_type=operation_type,
                table_name=table_name,
                schema_name=schema_name,
                snapshot_data=zlib.compress(json.dumps(rows, default=str).encode(), level=6) if rows else None,
                snapshot_size_bytes=len(json.dumps(rows, default=str).encode()) if rows else 0,
                row_count=len(rows),
                inverse_sql=inverse_sql,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
                created_at=datetime.now(timezone.utc),
            )
            session.add(snapshot)
            await session.flush()
            has_undo = True

            # Update history
            h_result = await session.execute(
                select(QueryHistory).where(QueryHistory.id == uuid.UUID(history_id))
            )
            history = h_result.scalar_one_or_none()
            if history:
                history.has_undo = True
                history.undo_snapshot_id = snapshot.id

        # Update history record
        h_result = await session.execute(
            select(QueryHistory).where(QueryHistory.id == uuid.UUID(history_id))
        )
        history = h_result.scalar_one_or_none()
        if history:
            history.execution_status = exec_result["status"]
            history.execution_time_ms = exec_result.get("execution_time_ms")
            history.row_count = exec_result.get("row_count")
            history.rows_affected = exec_result.get("rows_affected")
            history.error_message = exec_result.get("error")
            history.has_undo = has_undo

        # Update execution record
        if execution:
            execution.status = exec_result["status"]
            execution.completed_at = datetime.now(timezone.utc)
            execution.progress_pct = 100

        await session.commit()

        duration_s = (exec_result.get("execution_time_ms") or 0) / 1000.0
        queries_executed_total.labels(status=exec_result["status"]).inc()
        query_duration_seconds.observe(duration_s)

        logger.info(
            "query_task_complete",
            execution_id=execution_id,
            status=exec_result["status"],
            execution_time_ms=exec_result.get("execution_time_ms"),
        )
        return exec_result
