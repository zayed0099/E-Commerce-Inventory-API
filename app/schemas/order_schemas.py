from pydantic import BaseModel, model_validator, Field
from datetime import datetime
from typing import Any, Optional, List
from .base_schemas import APIResponse

class OrderProduct(BaseModel):
	""" *OrderItem part """
	product_id: int
	catg_id: int
	sku_id: int
	quantity: int
	unit_price_at_order: float

	@model_validator(mode="after")
	def no_null_value(self):
		variables = [
			self.product_id,
			self.catg_id,
			self.quantity,
			self.unit_price_at_order
		]

		if any(vr <= 0 for vr in variables):
			raise ValueError("0/Negative Values can't be accepted.")
		
		return self
		
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

	@model_validator(mode="after")
	def order_validator(self):
		pay_method = self.pay_method
		payment_status = self.payment_status
		items = self.items

		if not items or len(items) == 0:
			raise ValueError("Items can't be empty.")

		if pay_method == "cod" and payment_status != "unpaid":
			raise ValueError("Incorrect payment_status.")

		if pay_method in ["bkash", "gateway"] and payment_status != "paid":
			raise ValueError("Incorrect payment_status.")
		
		return self

class NewOrderConfirmation(APIResponse):
	tracking_id: str
	message: str = "Thanks for ordering. Your order will be delivered to you soon."

