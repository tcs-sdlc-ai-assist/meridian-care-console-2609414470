"""Configure file-backed asynchronous SQLite persistence."""

from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def ensure_database_parent() -> None:
    """Create the configured SQLite parent directory before connecting."""
    prefix = "sqlite+aiosqlite:///"
    if settings.database_url.startswith(prefix):
        database_path = settings.database_url.removeprefix(prefix)
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)


ensure_database_parent()
engine = create_async_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declare the shared SQLAlchemy declarative base."""


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped database session.

    Yields:
        An open asynchronous SQLAlchemy session.
    """
    async with SessionLocal() as session:
        yield session


async def create_tables() -> None:
    """Create the SQLite schema for the demo application."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
