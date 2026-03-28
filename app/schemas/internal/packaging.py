from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime
from typing import Any, Optional, Union, List, Dict

class SummariazedOrderItemData(BaseModel):
	orderitem_id : int
	quantity : int 
	unit_price_at_order : float
	is_processed : bool 
	is_confirmed : bool
	tracking_id : int

class MultipleOrderedProductSummary(BaseModel):
	page : int
	per_page : int
	total_data : int
	total_page: int

	ordered_products: List[SummariazedOrderItemData]

class DetailedSingleOrderItemData(BaseModel):
	orderitem_id : int
	order_quantity: int
	is_processed: int
	is_confirmed: int
	tracking_id: int

	product_name: str | None = None
	image_link: str | None = None
	current_price: float | None = None
	in_stock: bool | None = None
	category: str | None = None
	sku: str | None = None
	variant_in_stock: bool | None = None
	confirmed_product_stock: int | None = None
	attributes: dict[str, str | int | float] | None

	model_config = ConfigDict(from_attributes=True)