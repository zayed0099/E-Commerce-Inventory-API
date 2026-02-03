from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import and_
from typing import List
from datetime import datetime, timedelta
from hashids import Hashids
# Local Import
from app.database import (
	get_db, OrderTracking, OrderItem, OrderSummary, DeliveryDetails)
from app.core.jwt_setup import get_current_user
from app.core.config import API_VERSION, TRACKING_ENC_KEY, ALPHABET_ENC
from app.schemas import NewOrderAddress, NewOrderConfirmation

order_router = APIRouter(
	prefix=f"{API_VERSION}/orders",
	dependencies=[Depends(get_current_user)],
	tags=["orders"])

@order_router.post("/new-order")
async def add_new_order(
	current_user: dict = Depends(get_current_user),
	data: NewOrderAddress, db: AsyncSession = Depends(get_db)):
	
	"""order placed and info such as delivery address etc
		then user is given a tracking id(hashed) and if user confirms the order,
		then he can pay in advance or select COD
	"""
	hashid = Hashids(
		salt=TRACKING_ENC_KEY,
		min_length=8,
		alphabet=ALPHABET_ENC
	)

	try:
		order_tracking_entry = OrderTracking(
			pay_method = data.pay_method,
			payment_status = data.payment_status,
			order_status = data.order_status,
			delivery_status = data.delivery_status)

		db.add(order_tracking_id)
		await db.refresh(order_tracking_id)

		user_id = current_user["user_id"]
		tracking_id = order_tracking_id.id
		hashed_order_tracking_id = hashid.encode(user_id, tracking_id)
		
		(
			for product_id, catg_id, unit_price_at_order, quantity 
			in zip(
				data.product_ids, 
				data.catg_ids,
				data.unit_price_at_order,
				data.quantity
			):
				order_item_entry = OrderItem(
					product_id=product_id,
					catg_id=catg_id,
					tracking_id=tracking_id,
					quantity=quantity,
					unit_price_at_order=unit_price_at_order)
			
				db.add(order_item_entry)
				await db.refresh(order_item_entry)
		)

		order_summary_entry = OrderSummary(
					user_id=user_id,
					tracking_id=tracking_id,
					hashed_tracking_id=hashed_order_tracking_id)
		db.add(order_summary_entry)

		delivery_address_entry = DeliveryDetails(
			address_line=data.address_line,
			postal_code=data.postal_code,
			city=data.city,
			country=data.country,
			sec_email=data.sec_email,
			sec_phone=data.sec_phone,
			tracking_id=tracking_id		
			)
		db.add(delivery_address_entry)

		await db.commit()
		return NewOrderConfirmation(tracking_id=hashed_order_tracking_id)

	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, 
			detail="An Database error occured.")

@order_router.patch("/new-order")
async def add_new_order(
	current_user: dict = Depends(get_current_user),
	data: NewOrderAddress, db: AsyncSession = Depends(get_db)):
	pass