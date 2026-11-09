import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
#from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from app.database.db import init_db
from app.core.logging import admin_logger
from app.routers.product_display_and_order import orders, product_display
from app.routers.auth.cred_auth import auth_router
from app.routers.auth import employee_setup
from app.routers.internal.product_management import product_mgmt_router
from app.routers.internal import order_packaging, admin
from app.core.logging import register_exception_handlers
# from app.core.scheduler import start_scheduler

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
	# startup
	start_time = datetime.now()
	await init_db()
	admin_logger.info(f"Server started at {start_time}")

	yield

	# shutdown
	end_time = datetime.now()
	admin_logger.info(f"Server being shutdown at {end_time}")

app = FastAPI(lifespan=lifespan)

# Global Exception Handler
register_exception_handlers(app)

# Router Management 
app.include_router(auth_router)
app.include_router(product_mgmt_router)
app.include_router(product_display.product_display_router)
app.include_router(orders.order_router)
app.include_router(order_packaging.packg_router)
app.include_router(admin.admin_router)
	
if __name__ == "__main__":
	uvicorn.run(
		"main:app",
		host="0.0.0.0", 
		port=8000,
		log_level="info",
		reload=True
	)