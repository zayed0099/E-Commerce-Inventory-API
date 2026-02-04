from pydantic import BaseModel, root_validator, Field
from datetime import datetime
from typing import Any, Optional, List
from .base_schemas import APIResponse

class OrderProduct(NewOrder):
	""" *OrderItem part """
	product_id: int
	catg_id: int
	quantity: int
	unit_price_at_order: float

	@root_validator
	def no_null_value(cls, v):
		product_id = v.get("product_id")
		catg_id = v.get("catg_id")
		quantity = v.get("quantity")
		unit_price_at_order = v.get("unit_price_at_order")	

		variables = [product_id, catg_id, quantity, unit_price_at_order]
		
		if any(vr <= 0 for vr in variables):
			raise ValueError("0/Negative Values can't be accepted.")
		
		return v


class NewOrder(BaseModel):
	"""
	Order creation cycle : OrderTracking => OrderItem => OrderSummary
	*ordertracking part
	"""
	pay_method: str = "cod"
	payment_status: str = "unpaid"

	address_line: str
	postal_code: str
	city: str
	country: str
	sec_email: Optional[str] = None
	sec_phone: str
	
	items: List[OrderProduct]

	@root_validator
	def order_validator(cls, v):
		pay_method = v.get("pay_method")
		payment_status = v.get("payment_status")
		items = v.get("items")

		if not items or len(items) == 0:
			raise ValueError("Items can't be empty.")

		if pay_method == "cod" and payment_status != "unpaid"
			raise ValueError("Incorrect payment_status.")

		if pay_method in ["bkash", "gateway"] and payment_status != "paid"
			raise ValueError("Incorrect payment_status.")
		
		return v

class NewOrderConfirmation(APIResponse):
	tracking_id: str
	message: str = "Thanks for ordering. Your order will be delivered to you soon."

