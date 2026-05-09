from sqlalchemy import select, exists, update
from datetime import datetime, date
from app.database import Inventory
from app.core.logging import admin_logger
from app.database.db_for_old_pc import (
	PentiumAsyncSession as AsyncSession,
	SessionLocalSync as SessionLocal, get_db
)

async def inventory_in_stock_manager():
	sync_session = SessionLocal()
	async with AsyncSession(sync_session) as new_session:

		update_query = (
			update(Inventory)
			.where(
				Inventory.is_archived.is_(False),
				Inventory.in_stock.is_(True),
				Inventory.current_product_stock == 0
			)
			.values(
				in_stock = False
			)
		)
		result = await new_session.execute(update_query)

		changed = result.rowcount

		admin_logger.info(f"{changed} products marked out of stock in Inventory.")