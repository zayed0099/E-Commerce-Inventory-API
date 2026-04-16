from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, exists, update
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
from app.schemas import (APIResponse,
	MultipleOrderedProductSummary, DetailedSingleOrderItemData)
from app.utils import paginated_data_count

packg_router = APIRouter(
	prefix=f"{API_VERSION}/internal/packaging",
	# dependencies=[Depends(packaging_role_required)],
	tags=["packaging(internal)"])

@packg_router.get("/items", response_model=MultipleOrderedProductSummary)
async def manage_all_orderitem(
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
		(2, 1, 25000, False, False, 4)
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

@packg_router.get("/item/", response_model=DetailedSingleOrderItemData)
async def single_orderitem_data( 
	orderitem_id: int,
	verbose: bool = False,
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
			.where(OrderItem.id == orderitem_id)
		)

		product_info = None

	else:
		q = (
			select(*base_columns)
			.where(OrderItem.id == orderitem_id)
		)

	single_order_item = (await db.execute(q)).all()
	# print(single_order_item)
	
	if not single_order_item:
		raise HTTPException(status_code=404, detail="Item not found")

	orderitem = None

	for data in single_order_item:
		if orderitem is None:
			orderitem = {
				"orderitem_id" : data.orderitem_id,
				"order_quantity" : data.order_quantity,
				"is_processed" : data.is_processed,
				"is_confirmed" : data.is_confirmed,
				"tracking_id" : data.tracking_id,
				"attributes" : {}
			}

		if verbose:
			orderitem.update({
				"product_name" : data.product_name, 
				"image_link" : data.image_link, 
				"current_price" : data.current_price, 
				"in_stock" : data.in_stock,
				"category" : data.category, 
				"sku" : data.sku,
				"variant_in_stock" : data.variant_in_stock,
				"confirmed_product_stock" : data.confirmed_product_stock,
			})

			orderitem["attributes"][data.attribute] = data.attribute_value

	response = DetailedSingleOrderItemData(**orderitem)
	return response

@packg_router.patch("/item/update/")
async def update_processing_status( 
	orderitem_id: int, value: bool = True,
	# current_user: dict = Depends(packaging_role_required), 
	db: AsyncSession = Depends(get_db)):
	
	try:
		q = (
			update(OrderItem)
			.where(
				OrderItem.id == orderitem_id
			)
			.values(is_processed = value)
			.returning(OrderItem)
		)
		result = await db.execute(q)

		updated = result.scalar_one_or_none()

		if not updated:
			raise HTTPException(
				status_code=404,
				detail="Orderitem not found.")

		if value:
			msg_str = "processed"
		else:
			msg_str = "not processed"	
		
		return APIResponse(
			message=f"Orderitem_id: {updated.id}, has been marked {msg_str}.")

	except SQLAlchemyError as e:
		raise