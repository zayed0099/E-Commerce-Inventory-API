from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Optional, Union, List

class ProductAttribute(BaseModel):
	name: str = Field(alias="attribute")
	value: str = Field(alias="attribute_value")

	class Config:
		orm_mode = True

class ProductVariant(BaseModel):
	sku : str
	sku_id: int
	in_stock: bool = Field(alias="variant_in_stock")

	attributes: List[ProductAttribute]
	
	class Config:
		orm_mode = True
	
class SingleProductData(BaseModel):
	catg_id: int
	category: str

	product_id: int
	product_name: str
	short_desc: str
	image_link: str
	current_price: float
	in_stock: bool

	variants: List[ProductVariant]
	
	class Config:
		orm_mode = True