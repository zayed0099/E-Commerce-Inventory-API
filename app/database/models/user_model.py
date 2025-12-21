from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from typing import List
from datetime import datetime
from app.database import Base

class UserDB(Base):
	__tablename__ = "users"
	
	id: Mapped[int] = mapped_column(primary_key=True)

	username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
	email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
	password: Mapped[str | None] = mapped_column(String(100))

	is_oauth_login: Mapped[bool] = mapped_column(default=False, nullable=False)
	is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	# relationships
	orders_summary: Mapped["OrderSummary"] = relationship(
        back_populates="user", cascade="all, delete-orphan")

	track_orders: Mapped["OrderTracking"] = relationship(
        back_populates="user", cascade="all, delete-orphan")
