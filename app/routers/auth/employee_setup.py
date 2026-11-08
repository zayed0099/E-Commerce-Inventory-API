from typing import Optional

from fastapi import (
	APIRouter, Response, HTTPException, status, Depends, Cookie)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta

# Local Import
from app.database.db import get_db
from app.schemas import (
	TokenResponse, EmployeeVerification, APIResponse)
from app.core.jwt_setup import get_current_user, create_jwt
from app.database import UserDB, AuthDataDB, EmployeeDB
from .cred_auth import auth_router

@auth_router.post(
	"/employee/signup", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def new_employee(
	data: EmployeeVerification, 
	current_user: dict = Depends(stock_manager_required),
	db: AsyncSession = Depends(get_db)):

	user_id = current_user["user_id"]

	address_line = data.address_line
	postal_code = data.postal_code
	city = data.city
	country = data.country
	phone = data.phone
	sec_email = data.sec_email
	sec_phone = data.sec_phone

	db_item = EmployeeDB(
		is_active=False,
		auth_id=user_id,
		address_line=address_line,
		postal_code=postal_code,
		city=city,
		country=country,
		sec_email=sec_email,
		sec_phone=sec_phone,
		phone=phone
	)

	try:
		db.add(db_item)
		await db.commit()

		return APIResponse(
			message="Employee Verification application completed successfully.",
			data=None
		)

	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, 
			detail="Internal Server Error. Please try again later.")