import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UndoPreviewResponse(BaseModel):
    snapshot_id: uuid.UUID
    operation_type: str
    table_name: str
    schema_name: str
    row_count: int
    inverse_sql: str
    expires_at: datetime
    ttl_seconds: int
    is_consumed: bool


class UndoStatusResponse(BaseModel):
    has_undo: bool
    snapshot_id: Optional[uuid.UUID]
    is_consumed: bool
    expires_at: Optional[datetime]
    ttl_seconds: Optional[int]


class UndoExecuteResponse(BaseModel):
    success: bool
    execution_id: uuid.UUID
    message: str
