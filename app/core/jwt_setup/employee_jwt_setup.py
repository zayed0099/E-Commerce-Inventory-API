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
	async with SessionLocal() as db:
		token = cred.credentials
		payload = decode_jwt(token)
		
		user_id = payload["user_id"]

		if not payload:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Could not validate credentials",
				headers={"WWW-Authenticate": "Bearer"},
			)

		if not user_id:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid JWT payload",
				headers={"WWW-Authenticate": "Bearer"},
			)

		query = await db.execute(
			select(exists().where(
				and_(
					EmployeeDB.id == user_id,
					EmployeeDB.role.in_(["admin", role])
				)
			))
		)
		record_exists = query.scalar()

		if record_exists:
			admin_logger.info(
				f"Userid : {user_id}, role : {role}] logged in.")
			return payload
		else:
			admin_logger.info(
				f"Invalid Login attempt! User : {user_id}.")
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Authentication error.",
				headers={"WWW-Authenticate": "Bearer"},
			)