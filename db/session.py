"""
session.py

This module provides utilities for interacting with the database asynchronously.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DB_HOST
from config import DB_NAME
from config import DB_PASS
from config import DB_PORT
from config import DB_USER


Base = declarative_base()
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator for getting a database session.

    Yields:
        AsyncSession: An asynchronous database session.
    """
    async with async_session_maker() as session:
        yield session
