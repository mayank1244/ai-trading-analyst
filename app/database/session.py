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

        # Seed initial default watchlist items if empty
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            from app.database.models import Watchlist
            res = await session.execute(select(Watchlist))
            if not res.scalars().all():
                seeds = [
                    Watchlist(symbol="TATAELXSI", name="TATAELXSI", watchlist_price=3737.0, holding_period="3-5 days", notes="Sample Seed"),
                    Watchlist(symbol="DIVISLAB", name="DIVISLAB", watchlist_price=8378.0, holding_period="3-5 days", notes="Sample Seed"),
                    Watchlist(symbol="TITAN", name="TITAN", watchlist_price=4935.0, holding_period="3-5 days", notes="Sample Seed"),
                    Watchlist(symbol="HCLTECH", name="HCLTECH", watchlist_price=1369.9, holding_period="3-5 days", notes="Sample Seed"),
                    Watchlist(symbol="HINDALCO", name="HINDALCO", watchlist_price=1020.0, holding_period="3-5 days", notes="Sample Seed"),
                    Watchlist(symbol="UPL", name="UPL", watchlist_price=581.9, holding_period="3-5 days", notes="Sample Seed"),
                ]
                session.add_all(seeds)
                await session.commit()
                logger.info("Seeded default Watchlist stocks")
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
