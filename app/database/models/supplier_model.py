from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from typing import List
from datetime import datetime
from app.database import Base

class Suppliers(Base):
	__tablename__ = "suppliers"

	id: Mapped[int] = mapped_column(primary_key=True)
	is_archived: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

	name: Mapped[str] = mapped_column(String(100), nullable=False)
	email: Mapped[str] = mapped_column(Text(50), nullable=False)
	phone: Mapped[str] = mapped_column(String(20), nullable=False)

	is_supplying: Mapped[bool] = mapped_column(default=False, nullable=False)
	
	supp_type: Mapped[str] = mapped_column(String(30),
		default='distributor', nullable=False)

	details: Mapped["Suppliers"] = relationship(
		back_populates="supplier", cascade="all, delete-orphan")
	product_link: Mapped[List["Suppliers"]] = relationship(back_populates="productlink")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	__table_args__ = (
		CheckConstraint(
			"supp_type IN ('manufacturer', 'distributor', 'dropshipper', 'white_label')", 
			name='ck_supp_type'),
		)


class SupplierDetails(Base):
	__tablename__ = "supplierdetails"

	id: Mapped[int] = mapped_column(primary_key=True)
	is_archived: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

	address_line: Mapped[str] = mapped_column(String(200), nullable=False)
	postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
	city: Mapped[str] = mapped_column(String(100), nullable=False)
	country: Mapped[str] = mapped_column(String(100), nullable=False)

	sec_email: Mapped[str] = mapped_column(Text(50), nullable=False)
	sec_phone: Mapped[str] = mapped_column(String(20), nullable=False)

	supp_id: Mapped[int] = mapped_column(ForeignKey(
		"suppliers.id", index=True))

	supplier: Mapped["Suppliers"] = relationship(back_populates="details")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ProductSupplierLink(Base):
	__tablename__ = "productsupplierlink"

	id: Mapped[int] = mapped_column(primary_key=True)

	rate: Mapped[int] = mapped_column(default=0, nullable=False)
	unit_supplied: Mapped[int] = mapped_column(default=0, nullable=False)
	delivery_method: Mapped[str] = mapped_column(default='', nullable=False)

	supp_id: Mapped[int] = mapped_column(ForeignKey(
		"suppliers.id", index=True))
	product_id: Mapped[int] = mapped_column(ForeignKey(
		"products.id", index=True))

	product: Mapped["Category"] = relationship(back_populates="supplierlink")
	supplier: Mapped["Suppliers"] = relationship(back_populates="productlink")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	__table_args__ = (
		CheckConstraint(
			"delivery_method IN ('warehouse_delivery', 'own_cost')", 
			name='ck_delivery_method'),
	)