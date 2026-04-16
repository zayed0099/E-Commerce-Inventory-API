from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .logging_setup import error_logger

def register_exception_handlers(app):
	@app.exception_handler(SQLAlchemyError)
	async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
		error_logger.error(
			f"Method: {request.method} | Path: {request.url} | Error: {str(exc)}",
			exc_info=True
		)

		return JSONResponse(
			status_code=500,
			content={"detail": "Database error occurred"}
		)

	@app.exception_handler(Exception)
	async def global_exception_handler(request: Request, exc: Exception):
		error_logger.error(
			f"Method: {request.method} | Path: {request.url} | Error: {str(exc)}",
			exc_info=True)

		return JSONResponse(
			status_code=500,
			content={"detail": "Internal server error"}
		)