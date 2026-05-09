import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from app.database.db import get_db
from app.core.logging import admin_logger
from app.tasks import inventory_in_stock_manager

def start_scheduler(app: FastAPI):
	scheduler = AsyncIOScheduler()
	
	scheduler.add_job(
		inventory_in_stock_manager,
		CronTrigger(hour=4, minute=30),
		id="inventory_in_stock_manager",
		replace_existing=True
	)

	scheduler.start()
	admin_logger.info("Server started and scheduler initialized.")
