from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import mapped_column, DeclarativeBase, declared_attr, Mapped
from sqlalchemy import func
from typing import Annotated
from datetime import datetime
from app.config.config import setting

engine = create_async_engine(setting.DATABASE_URL)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


int_pk = mapped_column(primary_key=True)
create_at = Annotated[datetime, mapped_column(server_default=func.now())]
update_at = Annotated[datetime, mapped_column(server_default=func.now(), server_onupdate=func.now())]



class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())