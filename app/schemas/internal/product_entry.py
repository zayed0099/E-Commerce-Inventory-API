from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime
from typing import Any, Optional, Union, List, Dict

class SingleProductDataEntry(BaseModel):
	product_name: str
	short_desc: str
	image_link: str
	current_price: float
	in_stock: bool = True
	supplier_id: int

	catg_id: int

class ProductVariantEntry(BaseModel):
	sku : str
	in_stock: bool
	product_id: int
	current_product_stock: int

	attributes: Dict[str, Union[str, int, float]]

class SupplierEntry(BaseModel):
	name: str
	email: str
	phone: str
	is_supplying: bool = False
	supp_type: str = 'distributor'

	address_line: str
	postal_code: str
	city: str
	country: str

	sec_email: str
	sec_phone: str