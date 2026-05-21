import asyncio
import json
from typing import Dict, Set

import redis.asyncio as aioredis
from fastapi import WebSocket
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

CHANNEL_PREFIX = "stratum:ws:"
CANCEL_PREFIX = "stratum:cancel:"


class WebSocketManager:
    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}

    def _channel(self, execution_id: str) -> str:
        return f"{CHANNEL_PREFIX}{execution_id}"

    async def connect(self, execution_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if execution_id not in self._connections:
            self._connections[execution_id] = set()
        self._connections[execution_id].add(websocket)
        logger.debug("ws_connected", execution_id=execution_id)

    async def disconnect(self, execution_id: str, websocket: WebSocket) -> None:
        if execution_id in self._connections:
            self._connections[execution_id].discard(websocket)
            if not self._connections[execution_id]:
                del self._connections[execution_id]
        logger.debug("ws_disconnected", execution_id=execution_id)

    async def publish(self, execution_id: str, message: dict) -> None:
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        try:
            await redis_client.publish(self._channel(execution_id), json.dumps(message))
        finally:
            await redis_client.aclose()

    async def subscribe_and_forward(self, execution_id: str, websocket: WebSocket) -> None:
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(self._channel(execution_id))
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    try:
                        await websocket.send_text(data)
                        parsed = json.loads(data)
                        if parsed.get("type") in ("complete", "error", "cancelled"):
                            break
                    except Exception:
                        break
        finally:
            await pubsub.unsubscribe(self._channel(execution_id))
            await pubsub.aclose()
            await redis_client.aclose()

    async def signal_cancel(self, execution_id: str) -> None:
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        try:
            await redis_client.setex(f"{CANCEL_PREFIX}{execution_id}", 120, "1")
        finally:
            await redis_client.aclose()

    async def is_cancel_requested(self, execution_id: str) -> bool:
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        try:
            val = await redis_client.get(f"{CANCEL_PREFIX}{execution_id}")
            return val == "1"
        finally:
            await redis_client.aclose()


ws_manager = WebSocketManager()
