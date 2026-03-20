from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import mapped_column, DeclarativeBase, declared_attr, Mapped
from sqlalchemy import func, Integer
from typing import Annotated
from datetime import datetime
from app.config.settings import settings


engine = create_async_engine(settings.DATABASE_URL)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


def int_pk() -> Mapped[int]:
    return mapped_column(Integer, primary_key=True)



class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())