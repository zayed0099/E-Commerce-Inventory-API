"""
	order management cycle in this system:
	for "cod"
		user places order > support staff calls the user to ask if 
		he is confirming the order. if is_confirmed=true, then packaging dept
		starts packaging.
		user can deduct any product or product quantity during the confirmation call
		with support staff. but user wont have any order editing option on the website.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, exists, update
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import and_
from typing import List
from datetime import datetime, timedelta
from hashids import Hashids
# Local Import
# from app.database.db import get_db
from app.database.db_for_old_pc import (
	PentiumAsyncSession as AsyncSession,
	SessionLocalSync as SessionLocal, get_db
)
from app.database import (
	Inventory, OrderTracking, OrderItem, OrderSummary, DeliveryDetails, ReserveStock)
from app.core.logging import admin_logger, order_logger
from app.core.jwt_setup import get_current_user
from app.core.config import API_VERSION, TRACKING_ENC_KEY, ALPHABET_ENC
from app.schemas import NewOrder, NewOrderConfirmation, APIResponse
from app.utils.stock_management_for_orders import (
	check_product_availability, release_reserved_stocks)

order_router = APIRouter(
	prefix=f"{API_VERSION}/orders",
	dependencies=[Depends(get_current_user)],
	tags=["orders"])

hashid = Hashids(
		salt=TRACKING_ENC_KEY,
		min_length=8,
		alphabet=ALPHABET_ENC
	)

@order_router.post("/new-order")
async def add_new_order(
	data: NewOrder,
	current_user: dict = Depends(get_current_user), 
	db: AsyncSession = Depends(get_db)):
	
	"""
		this endpoint only takes the order> adds data to OrderTracking, OrderItem and 
		OrderSummary > sends user hashed order tracking key(user_id, OrderTracking.id)
		if user confirms the order,then he can pay in advance or select COD
	"""
	try:
		user_id = current_user["user_id"]
		tracking_id = None

		order_tracking_entry = OrderTracking(
				pay_method = data.pay_method,
				payment_status = data.payment_status,
				user_id=user_id,
				order_status='creating')

		await db.add(order_tracking_entry)
		await db.flush()

		tracking_id = order_tracking_entry.id
		
		if not isinstance(tracking_id, int):
			raise HTTPException(
				status_code=500,
				detail="An error occured with Tracking ID generation.")

		hashed_order_tracking_id = hashid.encode(user_id, tracking_id)
		
		for product in data.items:
			quantity = product.quantity
			product_id = product.product_id
			sku_id = product.sku_id

			is_product_available = await check_product_availability( 
				inventory_db=Inventory,
				reservation_db=ReserveStock,
				db=db,
				quantity=quantity,
				product_id=product_id,
				sku_id=sku_id,
				tracking_id=tracking_id
			)

			# if not is_product_available:
			# 	raise HTTPException(
			# 		status_code=500, 
			# 		detail="Product Out of Stock.")


			order_item_entry = OrderItem(
				tracking_id=tracking_id,
				product_id=product_id,
				sku_id=sku_id,
				catg_id=product.catg_id,
				quantity=quantity,
				unit_price_at_order=product.unit_price_at_order)
		
			await db.add(order_item_entry)

		order_summary_entry = OrderSummary(
				user_id=user_id,
				tracking_id=tracking_id,
				hashed_tracking_id=hashed_order_tracking_id)
		await db.add(order_summary_entry)

		delivery_address_entry = DeliveryDetails(
				address_line=data.address_line,
				postal_code=data.postal_code,
				city=data.city,
				country=data.country,
				sec_email=data.sec_email,
				sec_phone=data.sec_phone,
				tracking_id=tracking_id
			)
		await db.add(delivery_address_entry)

		if tracking_id is not None:
			try:
				tracking_query = (
					update(OrderTracking)
					.where(OrderTracking.id == tracking_id)
					.values(
						order_status = 'placed'
					))
				tracking_update = await db.execute(tracking_query)

			except SQLAlchemyError as ee:
				order_logger.exception(f"Tracking_id: {tracking_id}, status update to 'placed' failed.")
				raise ee
		await db.commit()
		
		return NewOrderConfirmation(tracking_id=hashed_order_tracking_id)

	except (SQLAlchemyError, HTTPException) as er:
		await db.rollback()

		# updating the tracking status
		if tracking_id is not None:
			try:
				sync_session = SessionLocal()
				async with AsyncSession(sync_session) as new_session:
					# async with new_session.begin():
					"""
					[If the code uses Real AsyncSession then un-comment the above part and 
					indent the below code inside it]
					"""
					tracking_query = (
						update(OrderTracking)
						.where(OrderTracking.id == tracking_id)
						.values(order_status = 'cancelled')
					)
					tracking_update = await new_session.execute(tracking_query) 
						 
					release_stocks = await release_reserved_stocks(
						reservation_db=ReserveStock,
						db=new_session,
						tracking_id=tracking_id
					)
					# no commit here.

			except Exception:
				order_logger.exception(
					f"Order Tracking(id:{tracking_id}) status update to 'cancelled' and stock release failed."
				)
		
		order_logger.exception(f"Order failed: {er}")
		raise HTTPException(
			status_code=400, 
			detail="Order Cancelled because of an error.")

@order_router.get("/authenticate")
async def auth_check(
	current_user: dict = Depends(get_current_user), 
	db: AsyncSession = Depends(get_db)):
	
	user_id = current_user["user_id"]

	res = {"user_id" : user_id}
	return APIResponse(message="Authentication successful!", data=res)