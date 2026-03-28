from fastapi import HTTPException, status, Depends
from sqlalchemy import select, exists
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import and_
from typing import List
from datetime import datetime, timedelta
from hashids import Hashids

# Local Import
# from app.database.db import get_db
from .router_settings import product_mgmt_router
from app.core.jwt_setup.employee_jwt_setup import stock_manager_required
from app.database.db_for_old_pc import (
	get_db, PentiumAsyncSession as AsyncSession)
from app.database import (
	Products, Category, Inventory, Suppliers, Category,
	ProductVariant, SupplierDetails, ProductSupplierLink)
from app.schemas import (
	SupplierEntry, SingleProductDataEntry, ProductVariantEntry, 
	CategoryEntry, APIResponse, ProductEntryResponse, ProductSupplierLinkEntry)
from app.core.logging import admin_logger

root_str_enc = Hashids(
	salt="productentry",
	min_length=4,
	alphabet="QWERTYUOPADFGHJKLMNBVCXZ246789"
)

@product_mgmt_router.post("/product/new", response_model=ProductEntryResponse)
async def add_new_product(
	data: SingleProductDataEntry,
	# current_user: dict = Depends(stock_manager_required), 
	db: AsyncSession = Depends(get_db)):
	
	# user_id = current_user["user_id"]

	product_name = data.product_name
	short_desc = data.short_desc
	image_link = data.image_link
	current_price = data.current_price
	in_stock = data.in_stock
	supplier_id = data.supplier_id
	catg_id = data.catg_id
	
	#  root_str encoding will be done later
	catg_check = await db.scalar(
		select(exists().where(Category.id == catg_id)
	))

	if not catg_check:
		raise HTTPException(
			status_code=400, 
			detail="Category doesn't exists.")

	if supplier_id is not None:
		supp_check = await db.scalar(
			select(exists().where(Suppliers.id == supplier_id)
		))

		if not supp_check:
			raise HTTPException(
				status_code=400, 
				detail="Invalid Supplier ID.")

	try:
		new_product_entry = Products(
				is_entry_complete=False,
				product_name=product_name,
				short_desc=short_desc,
				image_link=image_link,
				current_price=current_price,
				in_stock=in_stock,
				catg_id=catg_id
			)

		await db.add(new_product_entry)
		await db.commit()

		p_id = new_product_entry.id

		# admin_logger.info(
		# 	f"[PRODUCT_ENTRY]-> product_id: {p_id}, user_id: {user_id}")

		return ProductEntryResponse(
			message="Product data entry successful.", product_id=p_id)

	except SQLAlchemyError as er:
		await db.rollback()
		print(er)
				 
		raise HTTPException(
			status_code=400, 
			detail="Product entry failed because of an error.")

@product_mgmt_router.post("/product/add-variant", response_model=APIResponse)
async def add_product_variant(
	data: ProductVariantEntry,
	# current_user: dict = Depends(stock_manager_required), 
	db: AsyncSession = Depends(get_db)):
	
	# user_id = current_user["user_id"]

	# sku will be created in the frontend
	sku = data.sku
	in_stock = data.in_stock
	current_product_stock = data.current_product_stock
	product_id = data.product_id
	attributes = data.attributes

	try:
		new_variant_entry = Inventory(
				sku=sku,
				in_stock=in_stock,
				current_product_stock=current_product_stock,
				product_id = product_id
			)
		await db.add(new_variant_entry)
		await db.flush()

		sku_id = new_variant_entry.id

		for key, value in attributes.items():
			new_attr_entry = ProductVariant(
					sku_id = sku_id,
					product_id = product_id,
					attribute = key,
					attribute_value = value
				)
			await db.add(new_attr_entry)

		await db.commit()

		# admin_logger.info(
		# 	f"[PRODUCT_VARIANT_ENTRY]-> sku_id: {sku_id}, user_id: {user_id}")

		return APIResponse(message="Product Variant entry successful.")


	except SQLAlchemyError as er:
		await db.rollback()
		print(er)
				 
		raise HTTPException(
			status_code=400, 
			detail="Product variant entry failed because of an error.")

@product_mgmt_router.post("/product/supplier/new-record", response_model=APIResponse)
async def add_supplier_for_product(
	data: ProductSupplierLinkEntry,
	# current_user: dict = Depends(stock_manager_required), 
	db: AsyncSession = Depends(get_db)):
	
	# user_id = current_user["user_id"]
	rate = data.rate
	unit_supplied = data.unit_supplied
	delivery_method = data.delivery_method
	status = data.status

	supp_id = data.supp_id
	product_id = data.product_id

	order_placed_at = data.order_placed_at
	delivered_at = data.delivered_at

	new_entry = ProductSupplierLink(
			rate=rate,
			unit_supplied=unit_supplied,
			delivery_method=delivery_method,
			status=status,
			supp_id=supp_id, product_id=product_id,
			order_placed_at=order_placed_at,
			delivered_at=delivered_at
		)

	try:
		await db.add(new_entry)
		await db.commit()

		return APIResponse(message="Supplier and Product Link entry successful.")

	except SQLAlchemyError as e:
		print(e)
		await db.rollback()
		return APIResponse(message="An database error occured.")

@product_mgmt_router.post("/supplier/new", response_model=APIResponse)
async def add_new_supplier(
	data: SupplierEntry,
	# current_user: dict = Depends(stock_manager_required), 
	db: AsyncSession = Depends(get_db)):
	
	# user_id = current_user["user_id"]

	supp_name = data.name
	email = data.email
	phone = data.phone
	is_supplying = data.is_supplying
	supp_type = data.supp_type

	address_line = data.address_line
	postal_code = data.postal_code
	city = data.city
	country = data.country

	sec_email = data.sec_email
	sec_phone = data.sec_phone

	try:
		new_supplier = Suppliers(
				name = supp_name,
				email = email,
				phone = phone,
				is_supplying = is_supplying,
				supp_type = supp_type
			)
		await db.add(new_supplier)
		await db.flush()

		supp_id = new_supplier.id

		supplier_details = SupplierDetails(
				address_line = address_line,
				postal_code = postal_code,
				city = city,
				country = country,
				sec_email = sec_email,
				sec_phone = sec_phone,
				supp_id = supp_id
			)

		await db.add(supplier_details)
		await db.commit()

		# admin_logger.info(
		# 	f"[SUPPLIER_ENTRY]-> supp_id: {supp_id}, user_id: {user_id}")

		return APIResponse(message="Supplier and SupplierDetails entry successful.")

	except SQLAlchemyError as er:
		await db.rollback()
		print(er)
				 
		raise HTTPException(
			status_code=400, 
			detail="Product entry failed because of an error.")

@product_mgmt_router.post("/category/new", response_model=APIResponse)
async def add_new_category(
	data: CategoryEntry,
	# current_user: dict = Depends(stock_manager_required), 
	db: AsyncSession = Depends(get_db)):
	
	category = data.category

	try:
		new_catg = Category(
			category=category, normalized_category= category.strip().lower())
		
		await db.add(new_catg)
		await db.commit()
		return APIResponse(message="Catgeory entry successful.")

	except SQLAlchemyError as e:
		print(e)
		await db.rollback()

		raise HTTPException(
			status_code=400, 
			detail="Category entry failed because of an error.")

