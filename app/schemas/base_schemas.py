from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional, Union

class APIResponse(BaseModel):
	message: Optional[str] = None
	data: Optional[Union[list, dict]] = None

class PaginatedResponse(APIResponse):
	total_pages : int
	page : int
	page_size : int

 