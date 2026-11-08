from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional

class UserLogin(BaseModel):
	email : str
	password : str

class TokenResponse(BaseModel):
	access_token: str
	refresh_token : str
	token_type: str = "Bearer"

class UserCreate(BaseModel):
	username : str
	email : str
	password : str

class EmployeeVerification(BaseModel):
	
	address_line: str
	postal_code: str
	city: str
	country: str
	phone: str
	sec_email: Optional[str] = None
	sec_phone: str
