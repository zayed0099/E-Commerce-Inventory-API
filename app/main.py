import uvicorn
from fastapi import FastAPI
#from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
# from app.database.db import init_db
from app.database.db_for_old_pc import init_db
from app.core.logging import admin_logger
from app.routers.product_display_and_order import orders, product_display
from app.routers.auth import cred_auth
from app.routers.internal.product_management import product_mgmt_router
from app.routers.internal import order_packaging

app = FastAPI()
current_datetime = datetime.now()

"""
!!! WARNING !!!
I currently added await before all of my db.add operation, but It needs to be
removed if I shift to real ASYNC SQLALCHEMY. 
Without the await before db.add operation, my db is not completing add operations
ex:  await db.add()
-----------
"""

# Create tables at startup + APScheduler Startup
@app.on_event("startup")
async def on_startup():
	await init_db()
	admin_logger.info(f"Server started at {current_datetime}")
	# start_scheduler(app)

# Router Management 
app.include_router(cred_auth.auth_router)
app.include_router(product_mgmt_router)
app.include_router(product_display.product_display_router)
app.include_router(orders.order_router)
app.include_router(order_packaging.packg_router)

# App Shutdown settings
@app.on_event("shutdown")
def shutdown_event():
	admin_logger.info(f"Server being shutdown at {current_datetime}")

if __name__ == "__main__":
	uvicorn.run(
		"main:app",
		host="0.0.0.0", 
		port=8000,
		log_level="info",
		reload=True
	)