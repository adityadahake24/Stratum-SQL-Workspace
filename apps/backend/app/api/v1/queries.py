import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import CurrentUser, DBSession
from app.schemas.query import QueryExecuteRequest, QueryExecuteResponse, ExecutionStatusResponse, SQLAnalysisResult as SQLAnalysisSchema
from app.models.query_history import QueryHistory
from app.models.query_execution import QueryExecution
from app.services.sql_analyzer import sql_analyzer
from app.websockets.manager import ws_manager
from app.core.metrics import queries_executed_total

router = APIRouter()


@router.post("/execute", response_model=QueryExecuteResponse, status_code=202)
async def execute_query(body: QueryExecuteRequest, current_user: CurrentUser, session: DBSession):
    from app.workers.tasks.query_tasks import execute_query_task

    analysis = sql_analyzer.analyze(body.sql)
    analysis_schema = SQLAnalysisSchema(**analysis.dict())

    history_id = uuid.uuid4()
    execution_id = uuid.uuid4()

    history = QueryHistory(
        id=history_id,
        user_id=current_user.id,
        connection_id=body.connection_id,
        sql_text=body.sql,
        query_type=analysis.statement_types[0] if analysis.statement_types else "UNKNOWN",
        execution_status="pending",
        created_at=datetime.now(timezone.utc),
    )
    execution = QueryExecution(
        id=execution_id,
        history_id=history_id,
        user_id=current_user.id,
        status="queued",
        created_at=datetime.now(timezone.utc),
    )
    session.add(history)
    session.add(execution)
    await session.commit()

    execute_query_task.delay(
        str(execution_id),
        str(history_id),
        str(body.connection_id),
        str(current_user.id),
        body.sql,
    )
    queries_executed_total.labels(status="queued").inc()

    return QueryExecuteResponse(
        execution_id=execution_id,
        history_id=history_id,
        analysis=analysis_schema,
        status="queued",
    )


@router.get("/executions/{execution_id}", response_model=ExecutionStatusResponse)
async def get_execution_status(execution_id: uuid.UUID, current_user: CurrentUser, session: DBSession):
    result = await session.execute(
        select(QueryExecution).where(
            QueryExecution.id == execution_id,
            QueryExecution.user_id == current_user.id,
        )
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: uuid.UUID, current_user: CurrentUser, session: DBSession):
    result = await session.execute(
        select(QueryExecution).where(
            QueryExecution.id == execution_id,
            QueryExecution.user_id == current_user.id,
        )
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    await ws_manager.signal_cancel(str(execution_id))
    return {"message": "Cancel signal sent"}
