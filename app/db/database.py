import asyncio
from sqlalchemy.ext.asyncio import AsyncSession , async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import URL
from ..core.config import settings


engine = create_async_engine(settings.DB_URL, echo=True)

SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit= False,
)

Base = declarative_base()




async def get_db():
    async with SessionLocal() as session:
        yield session