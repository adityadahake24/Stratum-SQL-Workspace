import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel


class QueryExecuteRequest(BaseModel):
    connection_id: uuid.UUID
    sql: str
    tab_id: Optional[uuid.UUID] = None
    auto_limit: bool = True


class SQLAnalysisResult(BaseModel):
    statement_types: List[str]
    needs_transaction_wrap: bool
    has_existing_transaction: bool
    undo_eligible: bool
    target_tables: List[str]
    is_read_only: bool
    has_dangerous_patterns: bool
    risk_level: str
    warnings: List[str]


class QueryExecuteResponse(BaseModel):
    execution_id: uuid.UUID
    history_id: uuid.UUID
    analysis: SQLAnalysisResult
    status: str


class ExecutionStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    progress_pct: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class ResultPage(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    page: int
    page_size: int
    total_rows: Optional[int]
    has_more: bool
