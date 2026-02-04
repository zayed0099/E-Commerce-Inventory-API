import uvicorn
from fastapi import FastAPI
#from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from app.database.db import init_db
from app.core.logging import admin_logger
from app.routers.order_and_product_management import orders 

app = FastAPI()
current_datetime = datetime.now()

# Create tables at startup + APScheduler Startup
@app.on_event("startup")
async def on_startup():
	await init_db()
	admin_logger.info(f"Server started at {current_datetime}")
	# start_scheduler(app)

# Router Management
app.include_router(orders.order_router)

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