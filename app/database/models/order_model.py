""" 
***How the order-management cycle works***
A entry for a new order is created on OrderTracking.
	=> We use the pk from OrderTracking + users user_id and create a 8 char hash.
	=> then send it to user as order tracking number.
then we use pk from OrderTracking and create entry on OrderItem for products 
of that order. If a order has 2 products then we get 2 entry on OrderItem for that order.

we use the OrderItem id + OrderTracking id + user_id and add entry on OrderSummary.
(Still not sure if the OrderSummary is really necessary)

A single order can have: 
- Only One Entry on OrderTracking
- One/Multiple Entry on OrderItem
- One/Multiple Entry on OrderSummary
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint, Boolean, Text
from typing import List, Union
from datetime import datetime
from app.database.db import Base

"""
this is mainly for internal processing of orders
orders are processed in packaging using this model
"""
class OrderItem(Base):
	__tablename__ = "order_items"

	id: Mapped[int] = mapped_column(primary_key=True)

	quantity: Mapped[int] = mapped_column(nullable=False)
	unit_price_at_order: Mapped[int] = mapped_column(nullable=False)
	
	is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
	is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
	
	# Foreign Keys and Relationships
	tracking_id: Mapped[int] = mapped_column(ForeignKey(
		"order_tracking.id", ondelete="CASCADE"), index=True, nullable=False)
	
	product_id: Mapped[int] = mapped_column(ForeignKey(
		"products.id", ondelete="CASCADE"), index=True, nullable=False)
	
	catg_id: Mapped[int] = mapped_column(ForeignKey(
		"categories.id", ondelete="CASCADE"), index=True, nullable=False)

	sku_id: Mapped[int] = mapped_column(ForeignKey(
		"inventory.id", ondelete="CASCADE"), index=True, nullable=True)

	tracking: Mapped["OrderTracking"] = relationship(back_populates="items")
	product: Mapped["Products"] = relationship(back_populates="orders")
	category: Mapped["Category"] = relationship(back_populates="orders")
	variant: Mapped["Inventory"] = relationship(back_populates="orders")
	
	__table_args__ = (
		CheckConstraint('quantity >= 1 AND quantity <= 200', name='ck_quantity'),
	)

"""
main db table to record and process orders.
orders are taken using this table and fk'd in other two models
"""
class OrderTracking(Base):
	__tablename__ = "order_tracking"

	id: Mapped[int] = mapped_column(primary_key=True)

	"""
	planning to send the "id" of this table to user and hash it
	Later will decode the code and get tracking id + user_id.
	"""
	pay_method: Mapped[str] = mapped_column(String(20), nullable=False)
	payment_status: Mapped[str] = mapped_column(String(15), nullable=False)
	
	order_status: Mapped[str] = mapped_column(
		String(15), default="placed", nullable=False)
	delivery_status: Mapped[str] = mapped_column(
		String(15), default="processing", nullable=False)

	# Foreign Keys and Relationships
	user_id: Mapped[int] = mapped_column(ForeignKey(
		"users.id", ondelete="CASCADE"), index=True, nullable=False)

	items: Mapped[List["OrderItem"]] = relationship(
		back_populates="tracking", cascade="all, delete-orphan")

	orders_summary: Mapped[List["OrderSummary"]] = relationship(
		back_populates="tracking", cascade="all, delete-orphan")

	deliverydetails: Mapped["DeliveryDetails"] = relationship(
		back_populates="track_order", cascade="all, delete-orphan")
	
	user: Mapped["UserDB"] = relationship(back_populates="track_orders")

	__table_args__ = (
		CheckConstraint(
			"pay_method IN ('cod', 'bkash', 'gateway')", name='ck_pay_method'),
		CheckConstraint(
			"payment_status IN ('paid', 'unpaid')", name='ck_pay_status'),
		CheckConstraint(
			"order_status IN ('placed', 'confirmed', 'cancelled')", 
			name='ck_order_status'),
		CheckConstraint(
			"delivery_status IN ('delivered', 'on_way', 'processing')", 
			name='ck_delivery_status'),
	)

"""This is to keep all the hashed order id from users"""
class OrderSummary(Base):
	__tablename__ = "ordersummary"

	id: Mapped[int] = mapped_column(primary_key=True)
	
	# Foreign Keys and Relationships
	user_id: Mapped[int] = mapped_column(ForeignKey(
		"users.id", ondelete="CASCADE"), index=True, nullable=False)
	tracking_id: Mapped[int] = mapped_column(ForeignKey(
		"order_tracking.id", ondelete="CASCADE"), index=True, nullable=False)
	
	hashed_tracking_id: Mapped[str] = mapped_column(String(20), nullable=False)
	

	tracking: Mapped["OrderTracking"] = relationship(back_populates="orders_summary")
	user: Mapped["UserDB"] = relationship(back_populates="orders_summary")


"""
Table to keep all delivery details of orders
a one<->one relatinonship with tracking table
"""
class DeliveryDetails(Base):
	__tablename__ = "deliverydetails"

	id: Mapped[int] = mapped_column(primary_key=True)
	
	address_line: Mapped[str] = mapped_column(String(200), nullable=False)
	postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
	city: Mapped[str] = mapped_column(String(100), nullable=False)
	country: Mapped[str] = mapped_column(String(100), nullable=False)

	sec_email: Mapped[str] = mapped_column(Text(50), nullable=False)
	sec_phone: Mapped[str] = mapped_column(String(20), nullable=False)

	tracking_id: Mapped[int] = mapped_column(ForeignKey(
		"order_tracking.id", ondelete="CASCADE"), index=True, nullable=False)

	track_order: Mapped["OrderTracking"] = relationship(back_populates="deliverydetails")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)