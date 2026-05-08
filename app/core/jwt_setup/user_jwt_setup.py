from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy import select, exists, and_
from .jwt_config import security, decode_jwt
from app.database import UserDB
from app.database.db_for_old_pc import (
	PentiumAsyncSession as AsyncSession,
	SessionLocalSync as SessionLocal, get_db
)

async def get_current_user(cred: HTTPAuthorizationCredentials = Depends(security)):
	token = cred.credentials
	payload = decode_jwt(token)

	if not payload:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
			headers={"WWW-Authenticate": "Bearer"},
		)

	role = payload.get("role")
	auth_id = payload.get("auth_id")

	if role != "customer":
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid credentials",
			headers={"WWW-Authenticate": "Bearer"},
		)

	sync_session = SessionLocal()
	async with AsyncSession(sync_session) as db:
		query = await db.execute(
			select(UserDB.id)
			.where(UserDB.auth_id == auth_id)
		)
		user = query.first()
		
		user_id = user.id
	
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid credentials",
			headers={"WWW-Authenticate": "Bearer"},
		)

	pload = {
		"auth_id" : auth_id,
		"user_id" : user_id,
		"role" : role
	}		

	return pload

	# checking if user has an active api_key
	# if not, then user won't be able to access api even if he has a valid jwt
	# user_id = payload["user_id"]
	# await api_limit_manage(user_id)
		
	# return payload