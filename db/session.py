from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

##############################################
# BLOCK FOR COMMON INTERACTION WITH DATABASE #
##############################################

Base = declarative_base()

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# create async engine for interaction with database
engine = create_async_engine(DATABASE_URL, future=True, echo=True)


# create session for the interaction with database
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session