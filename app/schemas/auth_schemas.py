from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional

class UserLogin(BaseModel):
	# username : str
	email : str
	password : str

class TokenResponse(BaseModel):
	access_token: str
	refresh_token : str
	token_type: str = "Bearer"

class UserCreate(BaseModel):
	email : str
	password : str

