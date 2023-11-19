"""This module contains the database configuration and connection setup for the application.

It defines the database engine, sessionmaker, and AsyncSession for the application to connect to the MySQL database.
It also provides an async context manager function to get a database session for performing database operations.
"""
import dataclasses
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pera_fastapi.settings import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    f"mysql+aiomysql://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:3306/{settings.mysql_database}"
)

SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

from contextlib import asynccontextmanager

async def get_db() -> AsyncSession:
    """Get an AsyncSession object to perform database operations.

    Returns:
        AsyncSession: An AsyncSession object to perform database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
