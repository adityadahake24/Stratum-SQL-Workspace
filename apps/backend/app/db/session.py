from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.base import engine, Base

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
