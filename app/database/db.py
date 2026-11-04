from sqlalchemy.ext.asyncio import (
	create_async_engine,
	async_sessionmaker,
	AsyncSession)
from sqlalchemy.orm import DeclarativeBase
# from app.core.config import DATABASE_URL
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", None)


engine = create_async_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = async_sessionmaker(
	engine,
	expire_on_commit=False,
	class_=AsyncSession,
)

class Base(DeclarativeBase):
	pass

async def init_db():
	import app.database.models
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

# Dependency for DB session
async def get_db():
	async with SessionLocal() as session:
		yield session
