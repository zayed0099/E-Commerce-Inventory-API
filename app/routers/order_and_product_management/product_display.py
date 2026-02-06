from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import and_
from typing import List
from datetime import datetime, timedelta
from hashids import Hashids
# Local Import
from app.database.db import get_db
from app.database import (
	Products, Category, Inventory, ProductVariant)
from app.core.jwt_setup import get_current_user
from app.core.config import API_VERSION
from app.schemas import SingleProductData

product_display_router = APIRouter(
	prefix=f"{API_VERSION}/products",
	dependencies=[Depends(get_current_user)],
	tags=["product_display"])

@product_display_router.get("/{product_id}", response_model=SingleProductData)
async def single_product_display(
	product_id: int,
	# current_user: dict = Depends(get_current_user), 
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
					Products.is_archived == False
				)
			)
		)
	)
	product = await (db.execute(q)).all()

	if not product:
		raise HTTPException(status_code=404, detail="Item not found")

	product_dict = None
	variants_map = []

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
				"in_stock": row.variant_in_stock,
				"attributes": []
			}

		if row.attribute is not None:
			variants_map[row.sku]["attributes"].append({
				"attribute": row.attribute,
				"attribute_value": row.attribute_value
			})

	product_dict["variants"] = list(variants_map.values())

	response = SingleProductData(**product_dict)
	return response
