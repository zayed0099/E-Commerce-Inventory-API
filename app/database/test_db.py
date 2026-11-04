import asyncio
from sqlalchemy import text

from db import engine


async def main():
    async with engine.connect() as connection:
        # result = await connection.execute(text("SELECT version()"))
        result = await connection.execute(text("SELECT current_database(), current_schema()"))
        print(result.scalar_one())

asyncio.run(main())