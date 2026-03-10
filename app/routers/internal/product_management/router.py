from fastapi import APIRouter

# Local Import
from app.core.jwt_setup import stock_manager_required
from app.core.config import API_VERSION

product_mgmt_router = APIRouter(
	prefix=f"{API_VERSION}/internal",
	dependencies=[Depends(stock_manager_required)],
	tags=["stock_mgmt(internal)"])