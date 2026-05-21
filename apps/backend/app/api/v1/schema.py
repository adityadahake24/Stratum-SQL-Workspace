import json
import uuid
from typing import List
from fastapi import APIRouter

from app.dependencies import CurrentUser, DBSession
from app.schemas.schema_explorer import SchemaInfo, TableInfo, ColumnInfo, IndexInfo
from app.services.connection_service import ConnectionService
from app.services.connection_pool import pool_manager
from app.services.schema_service import schema_service
from app.services.token_service import get_redis

router = APIRouter()

SCHEMA_CACHE_TTL = 60


async def _get_pool(connection_id: uuid.UUID, user_id: uuid.UUID, session):
    svc = ConnectionService(session)
    conn = await svc.get_connection(connection_id, user_id)
    credentials = svc.get_decrypted_credentials(conn)
    return await pool_manager.get_pool(user_id, connection_id, credentials)


async def _cached(key: str, fn, ttl: int = SCHEMA_CACHE_TTL):
    redis = await get_redis()
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)
    result = await fn()
    result_dicts = [r.model_dump() for r in result]
    await redis.setex(key, ttl, json.dumps(result_dicts))
    return result_dicts


@router.get("/{connection_id}/schemas", response_model=List[SchemaInfo])
async def list_schemas(connection_id: uuid.UUID, current_user: CurrentUser, session: DBSession):
    pool = await _get_pool(connection_id, current_user.id, session)
    key = f"stratum:schema:{connection_id}:schemas"
    data = await _cached(key, lambda: schema_service.list_schemas(pool))
    return [SchemaInfo(**d) for d in data]


@router.get("/{connection_id}/schemas/{schema_name}/tables", response_model=List[TableInfo])
async def list_tables(connection_id: uuid.UUID, schema_name: str, current_user: CurrentUser, session: DBSession):
    pool = await _get_pool(connection_id, current_user.id, session)
    key = f"stratum:schema:{connection_id}:{schema_name}:tables"
    data = await _cached(key, lambda: schema_service.list_tables(pool, schema_name))
    return [TableInfo(**d) for d in data]


@router.get("/{connection_id}/schemas/{schema_name}/tables/{table_name}/columns", response_model=List[ColumnInfo])
async def list_columns(connection_id: uuid.UUID, schema_name: str, table_name: str, current_user: CurrentUser, session: DBSession):
    pool = await _get_pool(connection_id, current_user.id, session)
    key = f"stratum:schema:{connection_id}:{schema_name}:{table_name}:columns"
    data = await _cached(key, lambda: schema_service.list_columns(pool, schema_name, table_name))
    return [ColumnInfo(**d) for d in data]


@router.get("/{connection_id}/schemas/{schema_name}/tables/{table_name}/indexes", response_model=List[IndexInfo])
async def list_indexes(connection_id: uuid.UUID, schema_name: str, table_name: str, current_user: CurrentUser, session: DBSession):
    pool = await _get_pool(connection_id, current_user.id, session)
    key = f"stratum:schema:{connection_id}:{schema_name}:{table_name}:indexes"
    data = await _cached(key, lambda: schema_service.list_indexes(pool, schema_name, table_name))
    return [IndexInfo(**d) for d in data]
