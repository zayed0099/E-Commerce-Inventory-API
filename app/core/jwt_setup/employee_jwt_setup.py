from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy import select, exists, and_
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.database.db import SessionLocal

from app.database.db_for_old_pc import (
	PentiumAsyncSession as AsyncSession,
	SessionLocalSync as SessionLocal, get_db
)
from app.database import EmployeeDB
from .jwt_config import security, decode_jwt
from app.core.logging import admin_logger

async def admin_required(cred: HTTPAuthorizationCredentials = Depends(security)):
	return await check_employee_role(cred, "admin")

async def stock_manager_required(cred: HTTPAuthorizationCredentials = Depends(security)):
	return await check_employee_role(cred, "stock_manager")

async def support_role_required(cred: HTTPAuthorizationCredentials = Depends(security)):
	return await check_employee_role(cred, "support")

async def packaging_role_required(cred: HTTPAuthorizationCredentials = Depends(security)):
	return await check_employee_role(cred, "packaging")

async def check_employee_role(cred: HTTPAuthorizationCredentials, role: str):
	sync_session = SessionLocal()
	async with AsyncSession(sync_session) as db:
		token = cred.credentials
		payload = decode_jwt(token)
		
		if not payload:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Could not validate credentials",
				headers={"WWW-Authenticate": "Bearer"},
			)

		auth_id = payload.get("auth_id")
		user_role = payload.get("role")

		if not auth_id:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid JWT payload",
				headers={"WWW-Authenticate": "Bearer"},
			)

		query = await db.execute(
			select(EmployeeDB.id, EmployeeDB.role)
			.where(EmployeeDB.auth_id == auth_id))
		employee = query.first()

		if not employee:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Authentication error.",
				headers={"WWW-Authenticate": "Bearer"},
			)

		emp_role = employee.role
		emp_id = employee.id

		valid_roles = ['admin', role]
		
		if emp_role in valid_roles:
			admin_logger.info(
				f"Employee Login: auth_id : {auth_id}, role : {emp_role}]")
			
			pload = {
				"auth_id" : auth_id,
				"employee_id" : emp_id,
				"role" : emp_role
			}
			return pload

		else:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Authentication error.",
				headers={"WWW-Authenticate": "Bearer"},
			)
			