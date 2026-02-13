from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, func, update, case
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
	
async def check_product_availability( 
		inventory_db,
		db: AsyncSession,
		quantity: int,
		product_id: int,
		sku_id: int
	):
	
	"""
	tried to fix race condition problem i created eralier.
	it used to be
	select query > check none/in_stock=false > update hold + current stock
	now, one update query does all the job.
		it checks if quantity is equal or lower than current stock
		then updates the data > when another req comes it gets latest stock
	"""
	
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

	
