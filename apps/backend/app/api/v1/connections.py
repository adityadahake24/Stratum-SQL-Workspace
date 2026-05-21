import uuid
from typing import List
from fastapi import APIRouter

from app.dependencies import CurrentUser, DBSession
from app.schemas.connection import (
    ConnectionCreate, ConnectionUpdate, ConnectionResponse,
    ConnectionTestResponse, ConnectionTokenRequest, ConnectionTokenResponse,
)
from app.services.connection_service import ConnectionService
from app.services.connection_pool import pool_manager
from app.services.token_service import TokenService, get_redis

router = APIRouter()


def _to_response(svc: ConnectionService, conn) -> ConnectionResponse:
    safe = svc.to_safe_response(conn)
    return ConnectionResponse(**safe)


@router.get("", response_model=List[ConnectionResponse])
async def list_connections(current_user: CurrentUser, session: DBSession):
    svc = ConnectionService(session)
    conns = await svc.list_connections(current_user.id)
    return [_to_response(svc, c) for c in conns]


@router.post("", response_model=ConnectionResponse, status_code=201)
async def create_connection(body: ConnectionCreate, current_user: CurrentUser, session: DBSession):
    svc = ConnectionService(session)
    conn = await svc.create_connection(current_user.id, body)
    return _to_response(svc, conn)


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(connection_id: uuid.UUID, current_user: CurrentUser, session: DBSession):
    svc = ConnectionService(session)
    conn = await svc.get_connection(connection_id, current_user.id)
    return _to_response(svc, conn)


@router.put("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(connection_id: uuid.UUID, body: ConnectionUpdate, current_user: CurrentUser, session: DBSession):
    svc = ConnectionService(session)
    conn = await svc.update_connection(connection_id, current_user.id, body)
    return _to_response(svc, conn)


@router.delete("/{connection_id}", status_code=204)
async def delete_connection(connection_id: uuid.UUID, current_user: CurrentUser, session: DBSession):
    svc = ConnectionService(session)
    await svc.delete_connection(connection_id, current_user.id)
    await pool_manager.release_pool(current_user.id, connection_id)


@router.post("/test-temp", response_model=ConnectionTestResponse)
async def test_temp_connection(body: ConnectionCreate, current_user: CurrentUser):
    """Test raw credentials without saving the connection."""
    credentials = {
        "host": body.host,
        "port": body.port,
        "database": body.database,
        "username": body.username,
        "password": body.password or "",
        "ssl_mode": body.ssl_mode,
    }
    success, message, latency_ms = await pool_manager.test_connection(credentials)
    return ConnectionTestResponse(
        success=success,
        message=message if not success else "Connection successful",
        latency_ms=latency_ms,
        pg_version=message if success else None,
    )


@router.post("/{connection_id}/test", response_model=ConnectionTestResponse)
async def test_connection(connection_id: uuid.UUID, current_user: CurrentUser, session: DBSession):
    svc = ConnectionService(session)
    conn = await svc.get_connection(connection_id, current_user.id)
    credentials = svc.get_decrypted_credentials(conn)
    success, message, latency_ms = await pool_manager.test_connection(credentials)
    pg_version = message if success else None
    return ConnectionTestResponse(
        success=success,
        message=message if not success else "Connection successful",
        latency_ms=latency_ms,
        pg_version=pg_version,
    )


@router.post("/tokens", response_model=ConnectionTokenResponse)
async def create_connection_token(body: ConnectionTokenRequest, current_user: CurrentUser, session: DBSession):
    svc = ConnectionService(session)
    await svc.get_connection(body.connection_id, current_user.id)
    redis = await get_redis()
    token_svc = TokenService(redis)
    token, expires_at = await token_svc.create_token(body.connection_id, current_user.id)
    return ConnectionTokenResponse(token=token, expires_at=expires_at)


@router.post("/tokens/{token}", response_model=ConnectionResponse)
async def resolve_connection_token(token: str, current_user: CurrentUser, session: DBSession):
    redis = await get_redis()
    token_svc = TokenService(redis)
    payload = await token_svc.resolve_token(token)
    if not payload:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Token")
    svc = ConnectionService(session)
    conn = await svc.get_connection(uuid.UUID(payload["connection_id"]), uuid.UUID(payload["user_id"]))
    return _to_response(svc, conn)
