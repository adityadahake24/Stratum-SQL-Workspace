import json
import uuid
from datetime import datetime, timezone, timedelta

import redis.asyncio as redis
import structlog

from app.config import settings
from app.core.encryption import encrypt, decrypt

logger = structlog.get_logger(__name__)

TOKEN_PREFIX = "stratum:conn_token:"


class TokenService:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def create_token(self, connection_id: uuid.UUID, user_id: uuid.UUID) -> tuple[str, datetime]:
        token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.connection_token_expire_minutes)
        payload = json.dumps({
            "connection_id": str(connection_id),
            "user_id": str(user_id),
            "expires_at": expires_at.isoformat(),
        })
        encrypted = encrypt(payload)
        ttl_seconds = settings.connection_token_expire_minutes * 60
        await self.redis.setex(f"{TOKEN_PREFIX}{token}", ttl_seconds, encrypted)
        logger.info("connection_token_created", connection_id=str(connection_id))
        return token, expires_at

    async def resolve_token(self, token: str) -> dict | None:
        encrypted = await self.redis.get(f"{TOKEN_PREFIX}{token}")
        if not encrypted:
            return None
        payload = json.loads(decrypt(encrypted if isinstance(encrypted, str) else encrypted.decode()))
        expires_at = datetime.fromisoformat(payload["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            await self.redis.delete(f"{TOKEN_PREFIX}{token}")
            return None
        return payload

    async def revoke_token(self, token: str) -> None:
        await self.redis.delete(f"{TOKEN_PREFIX}{token}")


_redis_client = None


async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client
