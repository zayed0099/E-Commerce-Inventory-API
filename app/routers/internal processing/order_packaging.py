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
from app.core.jwt_setup import packaging_role_required
from app.core.config import API_VERSION, TRACKING_ENC_KEY, ALPHABET_ENC
from app.schemas import NewOrderAddress, NewOrderConfirmation