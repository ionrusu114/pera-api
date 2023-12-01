from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from pera_fastapi.settings import settings
DATABASE_URL = 'mysql+aiomysql://{}:{}@{}:3306/{}'.format(settings.mysql_user,settings.mysql_password,settings.mysql_host,settings.mysql_database)
from pera_fastapi.models.models import Base, User

# class Base(DeclarativeBase):
#     pass


# class User(SQLAlchemyBaseUserTableUUID, Base):
#     pass


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)