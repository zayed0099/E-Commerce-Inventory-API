"""
My old pc had issue and i was no longer able to use it. i was using 
windows 7 + Pyhton 3.8.3 and it was running async Sqlachemy fine. But it broke and windows isnt
working so i had to shift to antix linux and i am being unable to install async Sqlachemy there.
So i created this file using gemini to atleast test my endpoints, db queries etc. as its hard to
replace so much async/await functions and async db.execute.

Thanks
"""

import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.sql import selectable
from app.core.config import DATABASE_NAME

# --- Setup Paths ---
basedir = os.path.abspath(os.path.dirname(__file__))
# We use standard sqlite (sync) to bypass greenlet/aiosqlite requirements
DATABASE_URL = f"sqlite:///{os.path.join(basedir, DATABASE_NAME)}"

# --- The Sync Engine (Pentium Friendly) ---
engine = create_engine(DATABASE_URL, echo=True)
SessionLocalSync = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# --- The Compatibility Wrapper ---
# This "fakes" the AsyncSession behavior using threads
class PentiumAsyncSession:
    def __init__(self, sync_session):
        self.sync_session = sync_session

    async def execute(self, statement, *args, **kwargs):
        # We run the sync execute in a thread so 'await' works
        return await asyncio.to_thread(self.sync_session.execute, statement, *args, **kwargs)

    async def scalar(self, statement, *args, **kwargs):
        return await asyncio.to_thread(self.sync_session.scalar, statement, *args, **kwargs)

    async def scalars(self, statement, *args, **kwargs):
        return await asyncio.to_thread(self.sync_session.scalars, statement, *args, **kwargs)

    async def get(self, entity, ident, **kwargs):
        return await asyncio.to_thread(self.sync_session.get, entity, ident, **kwargs)

    async def add(self, instance):
        # session.add is usually fast/memory-only, but we thread it for consistency
        return await asyncio.to_thread(self.sync_session.add, instance)

    async def commit(self):
        return await asyncio.to_thread(self.sync_session.commit)

    async def rollback(self):
        return await asyncio.to_thread(self.sync_session.rollback)

    async def close(self):
        return await asyncio.to_thread(self.sync_session.close)

    async def flush(self):
        return await asyncio.to_thread(self.sync_session.flush)

    async def delete(self, instance):
        return await asyncio.to_thread(self.sync_session.delete, instance)

    async def refresh(self, instance):
        return await asyncio.to_thread(self.sync_session.refresh, instance)

    # Context manager support for "async with SessionLocal() as session:"
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

# --- The Dependency (Matches your original signature) ---
async def get_db():
    sync_session = SessionLocalSync()
    # We wrap the sync session in our Pentium-compatible shell
    async with PentiumAsyncSession(sync_session) as session:
        yield session

# --- Init DB (Using Sync Engine) ---
async def init_db():
    import app.database.models
    # No need for run_sync hack here since we have a real sync engine
    await asyncio.to_thread(Base.metadata.create_all, engine)