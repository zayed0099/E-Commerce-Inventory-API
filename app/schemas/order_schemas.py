from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional

class NewOrder(BaseModel):
	"""
	Order creation cycle : OrderTracking => OrderItem => OrderSummary
	*ordertracking part
	"""
	pay_method: [str] = "cod"
	payment_status: [str] = "unpaid"
	order_status: [str] = "placed"
	delivery_status: [str] = "processing"

	""" *OrderItem part """
	quantity: [int] = 1
	unit_price_at_order: [float]
	product_id: [int]
	catg_id: [int]

class NewOrderAddress(NewOrder):
	address_line: [str]
	postal_code: [str]
	city: [str]
	country: [str]

	sec_email: [str]
	sec_phone: [str]
