from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint, Boolean
from typing import List, Union
from datetime import datetime
from app.database.db import Base

class UserDB(Base):
	__tablename__ = "users"
	
	id: Mapped[int] = mapped_column(primary_key=True)

	username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
	email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
	password: Mapped[Union[str, None]] = mapped_column(String(150))

	is_oauth_login: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
	is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	# relationships
	orders_summary: Mapped[List["OrderSummary"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")

	track_orders: Mapped[List["OrderTracking"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")
