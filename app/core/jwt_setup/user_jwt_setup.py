from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy import select, exists, and_
from .jwt_config import security, decode_jwt

async def get_current_user(cred: HTTPAuthorizationCredentials = Depends(security)):
	token = cred.credentials
	payload = decode_jwt(token)

	if not payload:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
			headers={"WWW-Authenticate": "Bearer"},
		)

	# checking if user has an active api_key
	# if not, then user won't be able to access api even if he has a valid jwt
	# user_id = payload["user_id"]
	# await api_limit_manage(user_id)
		
	return payload