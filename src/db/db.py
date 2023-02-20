from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.core.config import app_settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(app_settings.database_dsn, echo=True, future=True)
async_session = async_sessionmaker(
    engine, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
