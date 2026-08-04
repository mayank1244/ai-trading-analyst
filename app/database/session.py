"""Async SQLAlchemy engine and session factory."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import settings
from app.database.models import Base
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _build_engine_kwargs() -> dict:
    url: str = settings.DATABASE_URL
    if url.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
            "echo": False,
        }
    return {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "echo": False,
    }


engine = create_async_engine(settings.DATABASE_URL, **_build_engine_kwargs())

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def init_db() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialised successfully")
    except Exception as exc:
        logger.error("Database initialisation failed: {}", exc)
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error("DB session error — rolling back: {}", exc)
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    return AsyncSessionLocal()
