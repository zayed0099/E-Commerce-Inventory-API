from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint, Boolean
from typing import List, Union
from datetime import datetime
# from app.database.db import Base
from app.database.db_for_old_pc import Base

class EmployeeDB(Base):
	__tablename__ = "employees"
	
	id: Mapped[int] = mapped_column(primary_key=True)

	is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
	role: Mapped[str] = mapped_column(String(20), default="packaging", nullable=False)

	first_name: Mapped[str] = mapped_column(String(20), nullable=False)
	last_name: Mapped[str] = mapped_column(String(20), nullable=False)
	phone_number: Mapped[str] = mapped_column(String(20), nullable=False)

	# relationships
	auth_id: Mapped[int] = mapped_column(ForeignKey(
		"user_auth.id", ondelete="CASCADE"), index=True, unique=True, nullable=True)

	auth_details: Mapped["AuthDataDB"] = relationship(back_populates="employee_account")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	__table_args__ = (
		CheckConstraint(
			"role IN ('admin', 'stock_manager', 'support', 'packaging')", 
			name='ck_user_role'),
		)