import asyncio
from datetime import datetime, timezone

import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.workers.tasks.cleanup_tasks.cleanup_expired_snapshots")
def cleanup_expired_snapshots():
    return _run_async(_cleanup_expired_snapshots())


@celery_app.task(name="app.workers.tasks.cleanup_tasks.cleanup_stale_sessions")
def cleanup_stale_sessions():
    return _run_async(_cleanup_stale_sessions())


@celery_app.task(name="app.workers.tasks.cleanup_tasks.cleanup_idle_connection_pools")
def cleanup_idle_connection_pools():
    return _run_async(_cleanup_idle_connection_pools())


@celery_app.task(name="app.workers.tasks.cleanup_tasks.cleanup_expired_tokens")
def cleanup_expired_tokens():
    logger.info("cleanup_expired_tokens_skipped", reason="tokens have built-in Redis TTL")
    return {"deleted": 0}


async def _cleanup_expired_snapshots():
    from app.db.session import async_session_factory
    from app.models.undo_snapshot import UndoSnapshot
    from sqlalchemy import delete

    async with async_session_factory() as session:
        result = await session.execute(
            delete(UndoSnapshot).where(UndoSnapshot.expires_at < datetime.now(timezone.utc))
        )
        await session.commit()
        count = result.rowcount
        logger.info("cleanup_snapshots_done", deleted=count)
        return {"deleted": count}


async def _cleanup_stale_sessions():
    from app.db.session import async_session_factory
    from app.models.session import UserSession
    from sqlalchemy import update

    async with async_session_factory() as session:
        result = await session.execute(
            update(UserSession)
            .where(UserSession.expires_at < datetime.now(timezone.utc), UserSession.is_active == True)
            .values(is_active=False)
        )
        await session.commit()
        count = result.rowcount
        logger.info("cleanup_sessions_done", deactivated=count)
        return {"deactivated": count}


async def _cleanup_idle_connection_pools():
    from app.services.connection_pool import pool_manager
    evicted = await pool_manager.cleanup_idle_pools()
    return {"evicted": evicted}
