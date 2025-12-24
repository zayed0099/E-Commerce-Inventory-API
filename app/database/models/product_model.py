from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from typing import List
from datetime import datetime
from app.database import Base

class Products(Base):
	__tablename__ = "products"
	
	id: Mapped[int] = mapped_column(primary_key=True)
	
	is_archived: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

	product_name: Mapped[str] = mapped_column(String(100), nullable=False)
	short_desc: Mapped[str] = mapped_column(Text(255), nullable=False)
	image_link: Mapped[str] = mapped_column(String(200), nullable=False)
	current_price: Mapped[int] = mapped_column(Integer(100), nullable=False)
	in_stock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

	catg_id: Mapped[int] = mapped_column(ForeignKey(
		"categories.id", index=True))

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

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Inventory(Base):
	__tablename__ = "inventory"
	
	id: Mapped[int] = mapped_column(primary_key=True)

	is_archived: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
	
	sku: Mapped[str] = mapped_column(String(30), nullable=False)

	current_stock: Mapped[int] = mapped_column(default=0, nullable=False)
	on_hold: Mapped[int] = mapped_column(default=0, nullable=False)
	confirmed_stock: Mapped[int] = mapped_column(default=0, nullable=False)

	product_id: Mapped[int] = mapped_column(ForeignKey(
		"products.id", ondelete="CASCADE", index=True))
	
	product: Mapped["Products"] = relationship(back_populates="items")
	variants: Mapped[List["ProductVariant"]] = relationship(
		back_populates="inventory_item", cascade="all, delete-orphan")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
	
class ProductVariant(Base):
	__tablename__ = "productvariant"
	
	id: Mapped[int] = mapped_column(primary_key=True)

	is_archived: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
	
	sku_id: Mapped[int] = mapped_column(ForeignKey(
		"inventory.id", ondelete="CASCADE", index=True))
	product_id: Mapped[int] = mapped_column(ForeignKey(
		"products.id", ondelete="CASCADE", index=True))

	attribute: Mapped[str] = mapped_column(String(20), nullable=False)
	attribute_value: Mapped[str] = mapped_column(String(30), nullable=False)

	parent_product: Mapped["Products"] = relationship(back_populates="variants")
	inventory_item: Mapped["Inventory"] = relationship(back_populates="variants")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)