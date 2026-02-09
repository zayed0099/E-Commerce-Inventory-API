"""	
***Explanation on how the product<-> sku <-> inventory works***
	=> every product has a single entry on the products table
	=> products can have multiple sku's based on its attributes
	=> sku's can have multiple entry on the productvariant db.
		that db also takes care of the attrubutes there too.
		
***Architecture explanation:
		=> Tshirt has a entry on products db.
		=> Tshirt has multiple entry on inventory db.
				like : TS-BLU-42, TS-BLU-43, TS-RED-42
		=> now Tshirt will have single/multiple entry on productvariant db
			for its every attribuite. Here, TS-BLU-42 has two.
			for size=42 and color=blue.
			We store the attribuite name too in this productvariant db.
	
	As it stands:
		ProductA has 
			=> single entry on products db
			=> single/multiple entry for its multiple version in inventory
			=> single/multiple entry for its every version in productvariant
"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint, Boolean, Text
from typing import List
from datetime import datetime
from app.database.db import Base

class Products(Base):
	__tablename__ = "products"
	
	id: Mapped[int] = mapped_column(primary_key=True)
	is_archived: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

	product_name: Mapped[str] = mapped_column(String(100), nullable=False)
	short_desc: Mapped[str] = mapped_column(Text(255), nullable=False)
	image_link: Mapped[str] = mapped_column(String(200), nullable=False)
	current_price: Mapped[int] = mapped_column(Integer, nullable=False)
	in_stock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

	catg_id: Mapped[int] = mapped_column(ForeignKey(
		"categories.id"), index=True, nullable=False)

	orders: Mapped[List["OrderItem"]] = relationship(back_populates="product")
	
	category: Mapped["Category"] = relationship(back_populates="products")
	
	items: Mapped[List["Inventory"]] = relationship(
		back_populates="product", cascade="all, delete-orphan")
	
	variants: Mapped[List["ProductVariant"]] = relationship(
		back_populates="parent_product", cascade="all, delete-orphan")

	supplierlink: Mapped["ProductSupplierLink"] = relationship(
		back_populates="product", cascade="all, delete-orphan")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Category(Base):
	__tablename__ = "categories"
	
	id: Mapped[int] = mapped_column(primary_key=True)

	is_archived: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
	
	category: Mapped[str] = mapped_column(String(100), nullable=False)
	normalized_category: Mapped[str] = mapped_column(
		String(100), index=True, nullable=False)

	products: Mapped[List["Products"]] = relationship(back_populates="category")
	orders: Mapped[List["OrderItem"]] = relationship(back_populates="category")
	
	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Inventory(Base):
	__tablename__ = "inventory"
	
	id: Mapped[int] = mapped_column(primary_key=True)
	is_archived: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
	
	sku: Mapped[str] = mapped_column(String(30), nullable=False)

	in_stock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

	"""
	current_stock = products available after deducting from onhold 
	on_hold = products ordered via customer but still not confirmed.
				added to current_stock again if not confirmed after a day
	confirmed_stock = products that were from confirmed orders
	"""
	current_stock: Mapped[int] = mapped_column(default=0, nullable=False)
	on_hold: Mapped[int] = mapped_column(default=0, nullable=False)
	confirmed_stock: Mapped[int] = mapped_column(default=0, nullable=False)

	product_id: Mapped[int] = mapped_column(ForeignKey(
		"products.id", ondelete="CASCADE"), index=True, nullable=False)
	
	product: Mapped["Products"] = relationship(back_populates="items")
	variants: Mapped[List["ProductVariant"]] = relationship(
		back_populates="inventory_item", cascade="all, delete-orphan")
	orders: Mapped[List["OrderItem"]] = relationship(
		back_populates="variant", cascade="all, delete-orphan")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
	
class ProductVariant(Base):
	__tablename__ = "productvariant"
	
	id: Mapped[int] = mapped_column(primary_key=True)

	is_archived: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
	
	sku_id: Mapped[int] = mapped_column(ForeignKey(
		"inventory.id", ondelete="CASCADE"), index=True, nullable=False)
	product_id: Mapped[int] = mapped_column(ForeignKey(
		"products.id", ondelete="CASCADE"), index=True, nullable=False)

	attribute: Mapped[str] = mapped_column(String(20), nullable=False)
	attribute_value: Mapped[str] = mapped_column(String(30), nullable=False)

	parent_product: Mapped["Products"] = relationship(back_populates="variants")
	inventory_item: Mapped["Inventory"] = relationship(back_populates="variants")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
