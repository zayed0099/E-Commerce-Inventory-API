from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional, List
from .base_schemas import APIResponse

class NewOrder(BaseModel):
	"""
	Order creation cycle : OrderTracking => OrderItem => OrderSummary
	*ordertracking part
	"""
	pay_method:str = "cod"
	payment_status: str = "unpaid"
	order_status: str = "placed"
	delivery_status: str = "processing"

	""" *OrderItem part """
	quantitys: List[int]
	unit_price_at_order: List[float]
	product_ids: List[int]
	catg_ids: List[int]

class NewOrderAddress(NewOrder):
	address_line: str
	postal_code: str
	city: str
	country: str

	sec_email: Optional[str] = None
	sec_phone: str

class NewOrderConfirmation(APIResponse):
	tracking_id: str
	message: str = "Thanks for ordering. Your order will be delivered to you soon."

