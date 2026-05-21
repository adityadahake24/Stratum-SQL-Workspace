import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

import structlog

from app.models.db_connection import DbConnection
from app.core.encryption import encrypt, decrypt
from app.core.exceptions import NotFoundError, ForbiddenError
from app.schemas.connection import ConnectionCreate, ConnectionUpdate

logger = structlog.get_logger(__name__)


class ConnectionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_connections(self, user_id: uuid.UUID) -> List[DbConnection]:
        result = await self.session.execute(
            select(DbConnection).where(
                DbConnection.user_id == user_id,
                DbConnection.is_active == True,
            ).order_by(DbConnection.created_at.desc())
        )
        return result.scalars().all()

    async def create_connection(self, user_id: uuid.UUID, data: ConnectionCreate) -> DbConnection:
        conn = DbConnection(
            user_id=user_id,
            name=data.name,
            host=encrypt(data.host),
            port=data.port,
            database=encrypt(data.database),
            username=encrypt(data.username),
            password_encrypted=encrypt(data.password),
            ssl_mode=data.ssl_mode,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(conn)
        await self.session.commit()
        await self.session.refresh(conn)
        logger.info("connection_created", connection_id=str(conn.id), user_id=str(user_id))
        return conn

    async def get_connection(self, connection_id: uuid.UUID, user_id: uuid.UUID) -> DbConnection:
        result = await self.session.execute(
            select(DbConnection).where(DbConnection.id == connection_id)
        )
        conn = result.scalar_one_or_none()
        if not conn:
            raise NotFoundError("Connection")
        if conn.user_id != user_id:
            raise ForbiddenError()
        return conn

    async def update_connection(
        self, connection_id: uuid.UUID, user_id: uuid.UUID, data: ConnectionUpdate
    ) -> DbConnection:
        conn = await self.get_connection(connection_id, user_id)
        if data.name is not None:
            conn.name = data.name
        if data.host is not None:
            conn.host = encrypt(data.host)
        if data.port is not None:
            conn.port = data.port
        if data.database is not None:
            conn.database = encrypt(data.database)
        if data.username is not None:
            conn.username = encrypt(data.username)
        if data.password is not None:
            conn.password_encrypted = encrypt(data.password)
        if data.ssl_mode is not None:
            conn.ssl_mode = data.ssl_mode
        conn.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(conn)
        return conn

    async def delete_connection(self, connection_id: uuid.UUID, user_id: uuid.UUID) -> None:
        conn = await self.get_connection(connection_id, user_id)
        conn.is_active = False
        conn.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        logger.info("connection_deleted", connection_id=str(connection_id))

    def get_decrypted_credentials(self, conn: DbConnection) -> dict:
        """Returns decrypted credentials — NEVER log or serialize this dict."""
        return {
            "host": decrypt(conn.host),
            "port": conn.port,
            "database": decrypt(conn.database),
            "user": decrypt(conn.username),
            "password": decrypt(conn.password_encrypted),
        }

    def to_safe_response(self, conn: DbConnection) -> dict:
        """Returns connection info safe for API response — no credentials."""
        return {
            "id": conn.id,
            "name": conn.name,
            "host": decrypt(conn.host),
            "port": conn.port,
            "database": decrypt(conn.database),
            "ssl_mode": conn.ssl_mode,
            "is_active": conn.is_active,
            "last_used_at": conn.last_used_at,
            "created_at": conn.created_at,
        }
