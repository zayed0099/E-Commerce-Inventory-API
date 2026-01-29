import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy import select, exists, and_
from app.core.config import JWT_ALGORITHM, JWT_SECRET

security = HTTPBearer()

def decode_jwt(token: str) -> Optional[dict]:
	try:
		decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
		user_id = decoded_token.get("user_id", None)

		if user_id is None:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid token payload",
				headers={"WWW-Authenticate": "Bearer"},
			)
		return decoded_token
		
	except jwt.ExpiredSignatureError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token has expired",
			headers={"WWW-Authenticate": "Bearer"},
		)
	except jwt.InvalidTokenError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token",
			headers={"WWW-Authenticate": "Bearer"},
		)

async def create_jwt(user_id, role):
	access_token = jwt.encode(
		payload={
			"role": role, 
			"user_id" : user_id,
			"type" : "access",
			"iat": int(datetime.utcnow().timestamp()),
			"exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp())
		}, 
		key=JWT_SECRET, 
		algorithm=JWT_ALGORITHM
	)
		
	refresh_token = jwt.encode(
		payload={
			"role": role, 
			"user_id" : user_id,
			"type" : "refresh",
			"iat": int(datetime.utcnow().timestamp()),
			"exp": int((datetime.utcnow() + timedelta(minutes=120)).timestamp())
		}, 
		key=JWT_SECRET, 
		algorithm=JWT_ALGORITHM
	)

	return access_token, refresh_token