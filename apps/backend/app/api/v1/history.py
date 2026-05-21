import uuid
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, func

from app.dependencies import CurrentUser, DBSession
from app.schemas.history import HistoryItemResponse, HistoryListResponse
from app.models.query_history import QueryHistory

router = APIRouter()


@router.get("", response_model=HistoryListResponse)
async def list_history(
    current_user: CurrentUser,
    session: DBSession,
    connection_id: Optional[uuid.UUID] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    offset = (page - 1) * page_size
    q = select(QueryHistory).where(QueryHistory.user_id == current_user.id)
    count_q = select(func.count()).select_from(QueryHistory).where(QueryHistory.user_id == current_user.id)

    if connection_id:
        q = q.where(QueryHistory.connection_id == connection_id)
        count_q = count_q.where(QueryHistory.connection_id == connection_id)

    q = q.order_by(QueryHistory.created_at.desc()).offset(offset).limit(page_size)

    result = await session.execute(q)
    items = result.scalars().all()

    count_result = await session.execute(count_q)
    total = count_result.scalar()

    return HistoryListResponse(
        items=[HistoryItemResponse.model_validate(h) for h in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{history_id}", response_model=HistoryItemResponse)
async def get_history_item(history_id: uuid.UUID, current_user: CurrentUser, session: DBSession):
    result = await session.execute(
        select(QueryHistory).where(
            QueryHistory.id == history_id,
            QueryHistory.user_id == current_user.id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="History item not found")
    return item
