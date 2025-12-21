from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from typing import List
from datetime import datetime
from app.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    
    is_processed: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Foreign Keys and Relationships
    tracking_id: Mapped[int] = mapped_column(ForeignKey(
        "order_tracking.id", ondelete="CASCADE"))
    
    # product_id
    # catg_id

    tracking: Mapped[List["OrderTracking"]] = relationship(back_populates="items")
    order_summary: Mapped["OrderSummary"] = relationship(back_populates="item")

    __table_args__ = (
        CheckConstraint('quantity >= 1 AND quantity <= 200', name='ck_quantity'),
    )

class OrderTracking(Base):
    __tablename__ = "order_tracking"

    tracking_number: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    
    pay_method: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(15), nullable=False)
    
    order_status: Mapped[str] = mapped_column(String(15), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(15), nullable=False)

    # Foreign Keys and Relationships
    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"))

    items: Mapped["OrderItem"] = relationship(
        back_populates="tracking", cascade="all, delete-orphan")

    orders_summary: Mapped["OrderTrackingLink"] = relationship(
        back_populates="tracking", cascade="all, delete-orphan")
# 
    user: Mapped[List["UserDB"]] = relationship(back_populates="track_order")

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

class OrderSummary(Base):
    __tablename__ = "ordersummary"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    unit_price_at_order: Mapped[int] = mapped_column(nullable=False)
    
    # Foreign Keys and Relationships
    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"))
    orderitem_id: Mapped[int] = mapped_column(ForeignKey(
        "order_items.id", ondelete="CASCADE"))
    tracking_id: Mapped[int] = mapped_column(ForeignKey(
        "order_tracking.id", ondelete="CASCADE"))
    
    item: Mapped["OrderItem"] = relationship(back_populates="order_summary")
    tracking: Mapped[List["OrderTracking"]] = relationship(back_populates="orders_summary")
    user: Mapped[List["UserDB"]] = relationship(back_populates="orders_summary")
