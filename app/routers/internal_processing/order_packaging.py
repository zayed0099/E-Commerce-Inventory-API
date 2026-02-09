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
	OrderTracking, OrderItem, OrderSummary, DeliveryDetails)
from app.core.jwt_setup import packaging_role_required
from app.core.config import API_VERSION
from app.schemas import NewOrderAddress, NewOrderConfirmation

packg_router = APIRouter(
	prefix=f"{API_VERSION}/internal",
	dependencies=[Depends(packaging_role_required)],
	tags=["packaging(internal)"])

@packg_router.get("/items")
async def manage_all_products(
	skip: int = 0, limit: int = 10,
	current_user: dict = Depends(get_current_user), 
	db: AsyncSession = Depends(get_db)):
	pass

@packg_router.get("/items/{item_id}")
async def single_product_status(
	item_id: int,
	current_user: dict = Depends(get_current_user), 
	db: AsyncSession = Depends(get_db)):
	pass
