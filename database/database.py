from collections.abc import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine 
from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
class Base(DeclarativeBase):
  pass

engine = create_async_engine(
  DATABASE_URL,
  echo = False,
  pool_pre_ping = True
)
SessionLocal = async_sessionmaker(
  bind=engine,
  class_=AsyncSession,
  expire_on_commit=False,
)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
  async with SessionLocal() as session:
    yield session

