from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manager import ws_manager
import structlog

logger = structlog.get_logger(__name__)

ws_router = APIRouter()


@ws_router.websocket("/ws/queries/{execution_id}")
async def query_websocket(execution_id: str, websocket: WebSocket):
    await ws_manager.connect(execution_id, websocket)
    try:
        await ws_manager.subscribe_and_forward(execution_id, websocket)
    except WebSocketDisconnect:
        logger.debug("ws_client_disconnected", execution_id=execution_id)
    finally:
        await ws_manager.disconnect(execution_id, websocket)
