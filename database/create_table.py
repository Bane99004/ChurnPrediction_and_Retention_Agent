import asyncio
from database.database import engine, Base
from database.database_models import Customer, AgentInteractions
async def create_table():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_table())