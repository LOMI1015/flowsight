from collections.abc import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.core.settings import settings
engine = create_async_engine(settings.db_url, pool_pre_ping=True)
session_local = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session_local() as session:
        yield session


async def init_database() -> None:
    from app.models import ingestion_models  # noqa: F401

    async with engine.begin() as conn:
        if settings.db_url.startswith('postgresql'):
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {settings.db_schema}'))
        await conn.run_sync(Base.metadata.create_all)
