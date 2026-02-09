from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import and_
from typing import List
from datetime import datetime, timedelta
from hashids import Hashids
# Local Import
from app.utils import paginated_data_count
from app.database.db import get_db
from app.database import (
	Products, Category, Inventory, ProductVariant)
from app.core.config import API_VERSION
from app.schemas import SingleProductData, MultipleProductData

product_display_router = APIRouter(
	prefix=f"{API_VERSION}/products",
	tags=["product_display"])

@product_display_router.get("/{product_id}", response_model=SingleProductData)
async def single_product_display(
	product_id: int, 
	db: AsyncSession = Depends(get_db)):
	
	q = (
		select(
			Products.id.label("product_id"), 
			Products.product_name, Products.short_desc,
			Products.image_link, Products.current_price, 
			Products.catg_id,
			Products.in_stock.label("product_in_stock"),
			Category.category,
			Inventory.id.label("inventory_sku_id"),
			Inventory.sku,
			Inventory.in_stock.label("variant_in_stock"),
			ProductVariant.attribute,
			ProductVariant.attribute_value
		)
			.join(
				Category,
				Category.id == Products.catg_id,
				isouter=True
			)
			.join(
				Inventory,
				Inventory.product_id == Products.id,
				isouter=True
			)
			.join(
				ProductVariant,
				ProductVariant.sku_id == Inventory.id,
				isouter=True
			)
			.where(
				and_(
					Products.id == product_id,
					Products.is_archived.is_(False)
					)
			)
	)
	product = (await db.execute(q)).all()

	if not product:
		raise HTTPException(status_code=404, detail="Item not found")

	product_dict = None
	variants_map = {}

	for row in product:
		if product_dict is None:
			product_dict = {
				"product_id": row.product_id,
				"product_name": row.product_name,
				"short_desc": row.short_desc,
				"image_link": row.image_link,
				"current_price": row.current_price,
				"in_stock": row.product_in_stock,
				"catg_id": row.catg_id,
				"category": row.category,
				"variants": []
			}

		if row.sku not in variants_map:
			variants_map[row.sku] = {
				"sku": row.sku,
				"sku_id": row.inventory_sku_id,
				"variant_in_stock": row.variant_in_stock,
				"attributes": {}
			}

		if row.attribute is not None:
			variants_map[row.sku]["attributes"][row.attribute] = row.attribute_value

	product_dict["variants"] = list(variants_map.values())

	response = SingleProductData(**product_dict)
	return response

@product_display_router.get("/", response_model=MultipleProductData)
async def multiple_product_display(
	page: int=1, per_page:int=10,
	db: AsyncSession = Depends(get_db)):
	
	total_data, total_page = (
		await paginated_data_count(
			db = db, 
			db_table = Products,
			per_page = per_page,  
			is_archived_check = True
		)
	)
	
	offset = (page - 1) * per_page

	q = (
		select(
			Products.id, 
			Products.product_name, 
			Products.image_link, 
			Products.current_price, 
			Products.catg_id,
			Products.in_stock,
		)
		.where(Products.is_archived.is_(False))
		.order_by(Products.id)
		.limit(per_page)
		.offset(offset)
	)
	products = (await db.execute(q)).all()

	if not products:
		raise HTTPException(status_code=404, detail="Item not found")

	data_to_send = {
		"page" : page,
		"per_page" : per_page,
		"total_data" : total_data,
		"total_page" : total_page,
		"products" : []
	}

	for p in products:
		product_details = {
			"product_id" : p.id,
			"catg_id" : p.catg_id,
			"product_name" : p.product_name,
			"image_link" : p.image_link,
			"current_price" : p.current_price,
			"in_stock" : p.in_stock,
			"url" : f"{API_VERSION}/products/{p.id}" 
		}
		data_to_send["products"].append(product_details)

	response = MultipleProductData(**data_to_send)
	return response
