import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class HistoryItemResponse(BaseModel):
    id: uuid.UUID
    connection_id: Optional[uuid.UUID]
    sql_text: str
    query_type: str
    execution_status: str
    execution_time_ms: Optional[int]
    rows_affected: Optional[int]
    row_count: Optional[int]
    error_message: Optional[str]
    has_undo: bool
    undo_snapshot_id: Optional[uuid.UUID]
    undo_executed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryListResponse(BaseModel):
    items: list[HistoryItemResponse]
    total: int
    page: int
    page_size: int
