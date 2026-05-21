import asyncio
import uuid
import time
from typing import Dict, Tuple, Optional

import asyncpg
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

MAX_POOLS = 20
IDLE_TIMEOUT_SECONDS = 300  # 5 minutes


class PoolEntry:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.last_used = time.monotonic()

    def touch(self):
        self.last_used = time.monotonic()

    @property
    def is_idle(self) -> bool:
        return (time.monotonic() - self.last_used) > IDLE_TIMEOUT_SECONDS


class ConnectionPoolManager:
    def __init__(self):
        self._pools: Dict[Tuple[str, str], PoolEntry] = {}
        self._lock = asyncio.Lock()

    def _key(self, user_id: uuid.UUID, connection_id: uuid.UUID) -> Tuple[str, str]:
        return (str(user_id), str(connection_id))

    async def get_pool(self, user_id: uuid.UUID, connection_id: uuid.UUID, credentials: dict) -> asyncpg.Pool:
        key = self._key(user_id, connection_id)
        async with self._lock:
            if key in self._pools:
                entry = self._pools[key]
                entry.touch()
                return entry.pool

            if len(self._pools) >= MAX_POOLS:
                await self._evict_oldest()

            pool = await self._create_pool(credentials)
            self._pools[key] = PoolEntry(pool)
            logger.info("pool_created", user_id=str(user_id), connection_id=str(connection_id))
            return pool

    async def _create_pool(self, credentials: dict) -> asyncpg.Pool:
        ssl = None
        if credentials.get("ssl_mode") in ("require", "verify-ca", "verify-full"):
            import ssl as ssl_module
            ssl = ssl_module.create_default_context()

        dsn = (
            f"postgresql://{credentials['user']}:{credentials['password']}"
            f"@{credentials['host']}:{credentials['port']}/{credentials['database']}"
        )
        return await asyncpg.create_pool(
            dsn=dsn,
            min_size=1,
            max_size=5,
            max_inactive_connection_lifetime=300,
            ssl=ssl,
            command_timeout=settings.max_query_runtime_seconds + 10,
        )

    async def release_pool(self, user_id: uuid.UUID, connection_id: uuid.UUID) -> None:
        key = self._key(user_id, connection_id)
        async with self._lock:
            entry = self._pools.pop(key, None)
            if entry:
                await entry.pool.close()
                logger.info("pool_released", user_id=str(user_id), connection_id=str(connection_id))

    async def test_connection(self, credentials: dict) -> Tuple[bool, str, Optional[int]]:
        import time as _time
        try:
            start = _time.perf_counter()
            pool = await self._create_pool(credentials)
            async with pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
            await pool.close()
            latency_ms = int((_time.perf_counter() - start) * 1000)
            return True, version, latency_ms
        except Exception as e:
            return False, str(e), None

    async def cleanup_idle_pools(self) -> int:
        evicted = 0
        async with self._lock:
            idle_keys = [k for k, v in self._pools.items() if v.is_idle]
            for key in idle_keys:
                entry = self._pools.pop(key)
                await entry.pool.close()
                evicted += 1
        if evicted:
            logger.info("pools_evicted", count=evicted)
        return evicted

    async def _evict_oldest(self) -> None:
        if not self._pools:
            return
        oldest_key = min(self._pools.items(), key=lambda x: x[1].last_used)[0]
        entry = self._pools.pop(oldest_key)
        await entry.pool.close()
        logger.warning("pool_evicted_max_reached", key=oldest_key)


pool_manager = ConnectionPoolManager()
