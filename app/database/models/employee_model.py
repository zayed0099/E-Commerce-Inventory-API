from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from typing import List
from datetime import datetime
from app.database import Base

class Employee(Base):
	__tablename__ = "employees"
	
	id: Mapped[int] = mapped_column(primary_key=True)

	username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
	email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
	password: Mapped[str | None] = mapped_column(String(100))
	role: Mapped[str] = mapped_column(String(20), default="packaging", nullable=False)

	is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	__table_args__ = (
		CheckConstraint(
			"role IN ('admin', 'stock_manager', 'support', 'packaging')", name='ck_user_role'),
	)