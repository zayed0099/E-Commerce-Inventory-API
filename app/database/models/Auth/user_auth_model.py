from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint, Boolean
from typing import List, Union
from datetime import datetime
# from app.database.db import Base
from app.database.db_for_old_pc import Base

class AuthDataDB(Base):
	__tablename__ = "user_auth"
	"""
	Plan for Authentication System:
	- everyone will be a user at signup.
	- then internally, customer accounts will be migrated to employee 
		and added to the employee db
	- user account will be disabled and employee account will be activated
	"""
	id: Mapped[int] = mapped_column(primary_key=True)
	
	username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
	email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
	password: Mapped[Union[str, None]] = mapped_column(String(200))

	is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
	is_email_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
	is_oauth_login: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
	is_employee: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

	# relationships
	user_account: Mapped["UserDB"] = relationship(
		back_populates="auth_details", cascade="all, delete-orphan")
	
	employee_account: Mapped["EmployeeDB"] = relationship(
		back_populates="auth_details", cascade="all, delete-orphan")

	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

