from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, exists
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import and_
from typing import List
from datetime import datetime, timedelta
from hashids import Hashids
# Local Import
from app.database.db_for_old_pc import (
	get_db, PentiumAsyncSession as AsyncSession)
from app.database import (
	OrderTracking, OrderItem, OrderSummary, DeliveryDetails, 
	Products, Category, Inventory, ProductVariant)
from app.core.jwt_setup import packaging_role_required
from app.core.config import API_VERSION
from app.schemas import MultipleOrderedProductSummary
from app.utils import paginated_data_count

packg_router = APIRouter(
	prefix=f"{API_VERSION}/internal/packaging",
	# dependencies=[Depends(packaging_role_required)],
	tags=["packaging(internal)"])

@packg_router.get("/items", response_model=MultipleOrderedProductSummary)
async def manage_all_products(
	page: int = 1, per_page: int = 10,
	# current_user: dict = Depends(packaging_role_required), 
	db: AsyncSession = Depends(get_db)):
	
	total_data, total_page = (
		await paginated_data_count(
			db = db, 
			db_table = OrderItem,
			per_page = per_page,  
			is_archived_check = False
		)
	)

	offset = (page - 1) * per_page
	"""
	Example Output: 
	[
		(1, 3, 35000, False, False, 2), 
		(2, 1, 25000, False, False, 4), 
		(3, 4, 45000, False, False, 4)
	]
	"""
	q = (
		select(
			OrderItem.id,
			OrderItem.quantity, 
			OrderItem.unit_price_at_order,
			OrderItem.is_processed, 
			OrderItem.is_confirmed,
			OrderItem.tracking_id
		)
		.order_by(OrderItem.id)
		.limit(per_page)
		.offset(offset)
	)
	ordered_products = (await db.execute(q)).all()

	if not ordered_products:
		raise HTTPException(status_code=404, detail="No ordered product found.")
	
	# print(ordered_products)

	data_to_send = {
		"page" : page,
		"per_page" : per_page,
		"total_data" : total_data,
		"total_page" : total_page,
		"ordered_products" : []
	}

	for p in ordered_products:
		details = {
			"orderitem_id" : p.id,
			"quantity": p.quantity, 
			"unit_price_at_order" : p.unit_price_at_order,
			"is_processed" : p.is_processed, 
			"is_confirmed" : p.is_confirmed,
			"tracking_id" : p.tracking_id
		}
		data_to_send["ordered_products"].append(details)

	response = MultipleOrderedProductSummary(**data_to_send)
	return response

@packg_router.get("/item/")
async def single_product_status(
	tracking_id: int, verbose: bool = False,
	# current_user: dict = Depends(packaging_role_required), 
	db: AsyncSession = Depends(get_db)):
	
	base_columns = [
		OrderItem.id.label("orderitem_id"),
		OrderItem.quantity.label("order_quantity"),
		OrderItem.is_processed,
		OrderItem.is_confirmed,
		OrderItem.tracking_id
	]

	if verbose:
		extend = [
			Products.product_name, 
			Products.image_link, 
			Products.current_price, 
			Products.in_stock,
			Category.category, 
			Inventory.sku, 
			Inventory.in_stock.label("variant_in_stock"),
			Inventory.confirmed_product_stock,
			ProductVariant.attribute,
			ProductVariant.attribute_value
		]
		base_columns.extend(extend)

		q = (
			select(*base_columns)
			.join(
				Products,
				Products.id == OrderItem.product_id,
				isouter=True
			)
			.join(
				Category,
				Category.id == OrderItem.catg_id,
				isouter=True
			)
			.join(
				Inventory,
				Inventory.id == OrderItem.sku_id,
				isouter=True
			)
			.join(
				ProductVariant,
				ProductVariant.sku_id == OrderItem.sku_id,
				isouter=True
			)
			.where(OrderItem.tracking_id == tracking_id)
		)

		product_info = None

	else:
		q = (
			select(*base_columns)
			.where(OrderItem.tracking_id == tracking_id)
		)

	single_order_item = (await db.execute(q)).all()
	# print(single_order_item)
	
	data_to_send = []

	if verbose:
		
