from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint, Boolean
from typing import List, Union
from datetime import datetime
from app.database.db import Base

class EmployeeDB(Base):
	__tablename__ = "employees"
	
	id: Mapped[int] = mapped_column(primary_key=True)

	is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
	role: Mapped[str] = mapped_column(String(20), default="packaging", nullable=False)

	first_name: Mapped[str] = mapped_column(String(20), nullable=False)
	last_name: Mapped[str] = mapped_column(String(20), nullable=False)
	
	address_line: Mapped[str] = mapped_column(String(200), nullable=False)
	postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
	city: Mapped[str] = mapped_column(String(100), nullable=False)
	country: Mapped[str] = mapped_column(String(100), nullable=False)

	phone: Mapped[str] = mapped_column(String(20), nullable=False)
	
	sec_email: Mapped[str] = mapped_column(String(50), nullable=True)
	sec_phone: Mapped[str] = mapped_column(String(20), nullable=False)

	# relationships
	auth_id: Mapped[int] = mapped_column(ForeignKey(
		"user_auth.id", ondelete="CASCADE"), index=True, unique=True, nullable=False)

	auth_details: Mapped["AuthDataDB"] = relationship(back_populates="employee_account")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	__table_args__ = (
		CheckConstraint(
			"role IN ('admin', 'stock_manager', 'support', 'packaging')", 
			name='ck_user_role'),
		)