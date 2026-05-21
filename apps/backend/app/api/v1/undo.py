import uuid
import json
import zlib
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import CurrentUser, DBSession
from app.schemas.undo import UndoPreviewResponse, UndoStatusResponse, UndoExecuteResponse
from app.models.query_history import QueryHistory
from app.models.undo_snapshot import UndoSnapshot
from app.core.metrics import undo_operations_total

router = APIRouter()


async def _get_snapshot(history_id: uuid.UUID, user_id: uuid.UUID, session) -> UndoSnapshot:
    h_result = await session.execute(
        select(QueryHistory).where(QueryHistory.id == history_id, QueryHistory.user_id == user_id)
    )
    history = h_result.scalar_one_or_none()
    if not history:
        raise HTTPException(status_code=404, detail="History item not found")
    if not history.has_undo or not history.undo_snapshot_id:
        raise HTTPException(status_code=404, detail="No undo snapshot available")

    s_result = await session.execute(
        select(UndoSnapshot).where(UndoSnapshot.id == history.undo_snapshot_id)
    )
    snapshot = s_result.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Undo snapshot not found")
    return snapshot


@router.get("/{history_id}/preview", response_model=UndoPreviewResponse)
async def preview_undo(history_id: uuid.UUID, current_user: CurrentUser, session: DBSession):
    snapshot = await _get_snapshot(history_id, current_user.id, session)

    now = datetime.now(timezone.utc)
    if snapshot.expires_at < now:
        raise HTTPException(status_code=410, detail="Undo snapshot has expired")

    ttl_seconds = int((snapshot.expires_at - now).total_seconds())
    return UndoPreviewResponse(
        snapshot_id=snapshot.id,
        operation_type=snapshot.operation_type,
        table_name=snapshot.table_name,
        schema_name=snapshot.schema_name,
        row_count=snapshot.row_count or 0,
        inverse_sql=snapshot.inverse_sql or "",
        expires_at=snapshot.expires_at,
        ttl_seconds=ttl_seconds,
        is_consumed=snapshot.is_consumed,
    )


@router.get("/{history_id}/status", response_model=UndoStatusResponse)
async def undo_status(history_id: uuid.UUID, current_user: CurrentUser, session: DBSession):
    h_result = await session.execute(
        select(QueryHistory).where(QueryHistory.id == history_id, QueryHistory.user_id == current_user.id)
    )
    history = h_result.scalar_one_or_none()
    if not history:
        raise HTTPException(status_code=404, detail="History item not found")

    if not history.has_undo or not history.undo_snapshot_id:
        return UndoStatusResponse(has_undo=False, snapshot_id=None, is_consumed=False, expires_at=None, ttl_seconds=None)

    s_result = await session.execute(
        select(UndoSnapshot).where(UndoSnapshot.id == history.undo_snapshot_id)
    )
    snapshot = s_result.scalar_one_or_none()
    if not snapshot:
        return UndoStatusResponse(has_undo=False, snapshot_id=None, is_consumed=False, expires_at=None, ttl_seconds=None)

    now = datetime.now(timezone.utc)
    ttl_seconds = max(0, int((snapshot.expires_at - now).total_seconds()))
    return UndoStatusResponse(
        has_undo=True,
        snapshot_id=snapshot.id,
        is_consumed=snapshot.is_consumed,
        expires_at=snapshot.expires_at,
        ttl_seconds=ttl_seconds,
    )


@router.post("/{history_id}/execute", response_model=UndoExecuteResponse)
async def execute_undo(history_id: uuid.UUID, current_user: CurrentUser, session: DBSession):
    snapshot = await _get_snapshot(history_id, current_user.id, session)

    now = datetime.now(timezone.utc)
    if snapshot.expires_at < now:
        raise HTTPException(status_code=410, detail="Undo snapshot has expired")
    if snapshot.is_consumed:
        raise HTTPException(status_code=409, detail="Undo already executed")
    if not snapshot.inverse_sql:
        raise HTTPException(status_code=422, detail="No inverse SQL available")

    from app.services.connection_service import ConnectionService
    from app.services.connection_pool import pool_manager
    from app.models.query_history import QueryHistory as QH
    from datetime import datetime as dt

    h_result = await session.execute(
        select(QH).where(QH.id == history_id)
    )
    original_history = h_result.scalar_one()

    conn_svc = ConnectionService(session)
    conn = await conn_svc.get_connection(original_history.connection_id, current_user.id)
    credentials = conn_svc.get_decrypted_credentials(conn)
    pool = await pool_manager.get_pool(current_user.id, original_history.connection_id, credentials)

    execution_id = uuid.uuid4()
    try:
        async with pool.acquire() as conn_obj:
            await conn_obj.execute(snapshot.inverse_sql)

        # Mark snapshot consumed
        snapshot.is_consumed = True

        # Update original history undo_executed_at
        original_history.undo_executed_at = dt.now(timezone.utc)

        # Create undo history entry
        undo_history = QH(
            id=execution_id,
            user_id=current_user.id,
            connection_id=original_history.connection_id,
            sql_text=f"-- UNDO of {history_id}\n{snapshot.inverse_sql}",
            query_type="UNDO",
            execution_status="success",
            execution_time_ms=0,
            has_undo=False,
            created_at=dt.now(timezone.utc),
        )
        session.add(undo_history)
        await session.commit()
        undo_operations_total.labels(status="success").inc()

        return UndoExecuteResponse(
            success=True,
            execution_id=execution_id,
            message="Undo executed successfully",
        )
    except Exception as e:
        undo_operations_total.labels(status="error").inc()
        raise HTTPException(status_code=500, detail=f"Undo failed: {e}")
