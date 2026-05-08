from fastapi import (
	APIRouter, Response, HTTPException, status, Depends, Cookie)
from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta

# Local Import
from app.database.db_for_old_pc import (
	PentiumAsyncSession as AsyncSession, get_db)
# from app.database.db import get_db
from app.schemas import (
	TokenResponse, UserCreate, UserLogin, APIResponse)
from app.core.jwt_setup import get_current_user, create_jwt
from app.core.config import API_VERSION
from app.database import UserDB, AuthDataDB, EmployeeDB

# Router Setup
auth_router = APIRouter(
	prefix=f"{API_VERSION}/auth", 
	tags=["auth"])

# Argon2 Password Hasher
ph = PasswordHasher()

@auth_router.post(
	"/signup", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def new_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
	
	result = await db.execute(
		select(AuthDataDB.username, AuthDataDB.email)
		.where(
			(AuthDataDB.username == data.username) |
			(AuthDataDB.email == data.email)
	))
	existing = result.scalars().first()

	if existing.email == data.email:
		raise HTTPException(status_code=400, detail="Invalid Credentials. Try Again.")

	if existing.username == data.username:
		raise HTTPException(status_code=400, detail="Username Taken.")

	unhashed_password = data.password
	pass_len = len(unhashed_password)
	
	if not pass_len >= 8:
		raise HTTPException(status_code=400, detail="Create a stronger password!")

	hashed_password = ph.hash(unhashed_password)

	db_item = AuthDataDB(
			username=data.username,
			password=hashed_password,
			email=data.email)

	try:
		await db.add(db_item)
		await db.commit()
		# await db.refresh(db_item)
		
		return APIResponse(
			message="Account Creation Successful. Head to /login to use account.")
	except SQLAlchemyError as e:
		await db.rollback()
		raise

@auth_router.post("/login/cred", response_model=APIResponse)
async def User_Login(
	data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
	
	result = await db.execute(
		select(
			AuthDataDB.id, 
			AuthDataDB.password, 
			AuthDataDB.is_employee
		)
		.where(AuthDataDB.email == data.email)
	)

	existing = result.first()
	
	if not existing:
		raise HTTPException(status_code=400, detail="Invalid credentials.")
		
	try:
		ph.verify(existing.password, data.password)

		auth_id = existing.id

		if existing.is_employee:
			query = await db.execute(
				select(EmployeeDB.id, EmployeeDB.role)
				.where(EmployeeDB.auth_id == auth_id)
			)						
			emp_role = query.first()
			
			role = emp_role.role

		else:
			query = await db.execute(
				select(UserDB.id)
				.where(UserDB.auth_id == auth_id)
			)						
			user_check = query.first()
			
			role = "customer"

		access_token, refresh_token = await create_jwt(
			auth_id=auth_id, 
			role=role)
		
		"""
		return TokenResponse(
			access_token=access_token,
			refresh_token=refresh_token)
		"""
			
		response.set_cookie(
			key="access_token",
			value=access_token,
			httponly=True,
			secure=True,
			samesite="lax",
			max_age=1800 # 30min in seconds
		)
		response.set_cookie(
			key="refresh_token",
			value=refresh_token,
			httponly=True,
			secure=True,
			samesite="lax",
			max_age=3600 # 60min in seconds
		)

		return APIResponse(
			message="Login Successful!")

	except VerifyMismatchError:
		raise HTTPException(status_code=401, detail="Invalid credentials")

@auth_router.patch("/refresh")
async def refresh(
	response: Response,
	refresh_token: str = Cookie(None)
):
	if not refresh_token:
		raise HTTPException(status_code=401, detail="Refresh token not found.")
	
	payload = decode_jwt(refresh_token)
	
	new_access, new_refresh = await create_jwt(
		auth_id=payload["auth_id"],
		role=payload["role"]
	)
	
	response.set_cookie(
			key="access_token",
			value=new_access,
			httponly=True,
			secure=True,
			samesite="lax",
			max_age=1800 # 30min in seconds
		)

	response.set_cookie(
		key="refresh_token",
		value=new_refresh,
		httponly=True,
		secure=True,
		samesite="lax",
		max_age=3600 # 60min in seconds
	)
	
	return {"message": "Token refresh Successful."}

@auth_router.post("/logout")
async def logout(response: Response):
	response.delete_cookie("access_token")
	response.delete_cookie("refresh_token")
	return {"message": "Logged out"}