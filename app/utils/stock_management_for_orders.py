# from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_for_old_pc import PentiumAsyncSession as AsyncSession

from sqlalchemy import select, exists, func, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
	
async def check_product_availability( 
		inventory_db,
		reservation_db,
		db: AsyncSession,
		quantity: int,
		product_id: int,
		sku_id: int,
		tracking_id: int
	):

	try:
		update_query = (
			update(inventory_db)
			.where(
				inventory_db.is_archived.is_(False),
				inventory_db.id == sku_id,
				inventory_db.product_id == product_id,
				inventory_db.in_stock.is_(True),
				inventory_db.current_product_stock >= quantity
			)
			.values(
				current_product_stock = inventory_db.current_product_stock - quantity,
				product_stock_on_hold = inventory_db.product_stock_on_hold + quantity
			)
		)

		result = await db.execute(update_query)
		
		ten_min_time = int((datetime.utcnow() + timedelta(minutes=10)).timestamp())
		reservation_entry = reservation_db(
				status="pending",
				quantity=quantity,
				expires_at=ten_min_time,
				tracking_id=tracking_id,
				sku_id=sku_id
			)

		db.add(reservation_entry)

		await db.commit()

		if result.rowcount == 0:
			raise HTTPException(
				status_code=400,
				detail="An error occured with product stock")
		
		elif result.rowcount == 1:
			return True

	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")

async def release_reserved_stocks(
		reservation_db,
		db: AsyncSession,
		tracking_id: int
	):

	try:
		stmt = (
			select(reservation_db)
			.where(reservation_db.tracking_id == tracking_id)
			.options(joinedload(reservation_db.inventory_item)) 
		)
		reserved_stocks = await (db.execute(stmt)).scalars().all()

		for data in reserved_stocks:
			data.inventory_item.current_product_stock += data.quantity
			data.inventory_item.product_stock_on_hold -= data.quantity
			data.status = "cancelled"
			
			order_logger.info(
				f"{data.quantity} products[order tracking id : {tracking_id}] have been released from hold.")

		return True

	except SQLAlchemyError as e:
		await db.rollback()
		order_logger.info(
			f"An error occured while releasing stock for failed order[tracking_id: {tracking_id}]")
