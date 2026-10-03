from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


# SQLite драйвер
DATABASE_URL = "sqlite+aiosqlite:///./fraud_check.db"

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    DATABASE_URL,
    echo=False, 
    future=True,
    connect_args={"check_same_thread": False},
)

# фаб. асинхрон сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def init_db() -> None:
    from models import FraudCheckLog #noqa: 401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
            """
            Открывает сессию на время обработки запроса и гарантированно закрывает её.
            """
            async with AsyncSessionLocal() as session: 
                try:
                    yield session
                except Exception:
                    await session.rollback()
                    raise

