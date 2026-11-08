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
	TokenResponse, UserCreate, UserLogin, APIResponse)
from app.core.jwt_setup import admin_required
from app.core.jwt_setup import get_current_user, create_jwt
from app.core.config import API_VERSION
from app.database import UserDB, AuthDataDB, EmployeeDB

admin_router = APIRouter(
	prefix=f"{API_VERSION}/internal/admin",
	dependencies=[Depends(admin_required)],
	tags=["admin(internal)"])


@admin_router.get(
	"/employees/new_applications", status_code=status.HTTP_200_OK, response_model=APIResponse)
async def approve_employee_application(db: AsyncSession = Depends(get_db)):

	try:
		query = await db.execute(
			select(
				EmployeeDB.id,
				EmployeeDB.role,
				EmployeeDB.first_name,
				EmployeeDB.last_name
				).where(EmployeeDB.is_active == False)
		)
		employees = query.scalars().all()

		if not employees:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Employees not found."
			)

		employees_for_verification = []
		
		for employee in employees:
			employee_data = {
				"id": employee.id,
				"role": employee.role,
				"first_name": employee.first_name,
				"last_name": employee.last_name
			}
			employees_for_verification.append(employee_data)

		return APIResponse(
			message="Employees retrieved successfully.",
			data=employees_for_verification
		)
		
	except SQLAlchemyError as e:
		raise HTTPException(
			status_code=500, 
			detail="Internal Server Error. Please try again later.")

@admin_router.get(
	"/employees/{employee_id}", status_code=status.HTTP_200_OK, response_model=APIResponse)
async def individual_employee_details(employee_id: int, db: AsyncSession = Depends(get_db)):

	try:
		query = await db.execute(
			select(EmployeeDB).where(EmployeeDB.id == employee_id)
		)
		employee = query.scalar_one_or_none()

		if not employee:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Employee not found."
			)

		employee_data = {
			"id": employee.id,
			"role": employee.role,
			"first_name": employee.first_name,
			"last_name": employee.last_name,
			"address_line": employee.address_line,
			"postal_code": employee.postal_code,
			"city": employee.city,
			"country": employee.country,
			"sec_email": employee.sec_email,
			"sec_phone": employee.sec_phone,
			"is_active": employee.is_active
		}

		return APIResponse(
			message="Employee retrieved successfully.",
			data=employee_data
		)
		
	except SQLAlchemyError as e:
		raise HTTPException(
			status_code=500, 
			detail="Internal Server Error. Please try again later.")

@admin_router.patch(
	"/employees/{employee_id}/approve", status_code=status.HTTP_200_OK, response_model=APIResponse)
async def approve_employee(employee_id: int, db: AsyncSession = Depends(get_db)):

	try:
		query = await db.execute(
			select(EmployeeDB).where(EmployeeDB.id == employee_id)
		)
		employee = query.scalar_one_or_none()

		if not employee:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Employee not found."
			)

		employee.is_active = True
		await db.commit()

		return APIResponse(
			message="Employee approved successfully.",
			data=None
		)

	except SQLAlchemyError as e:
		await db.rollback()
		raise HTTPException(
			status_code=500,
			detail="Internal Server Error. Please try again later.")