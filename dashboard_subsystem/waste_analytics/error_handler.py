
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class WasteAnalyticsError(Exception):

    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class WasteAnalyticsErrorHandler:

    @staticmethod
    async def handle_application_error(
        request: Request, #The incoming request object. FastAPI passes it automatically.
        exc: WasteAnalyticsError #The object of the error that occurred.
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message}
        )

    @staticmethod
    async def handle_database_error( #This method handles errors that occur when interacting with the database via SQLModel/SQLAlchemy.
        request: Request,
        exc: SQLAlchemyError
    ):
        logging.error("Database error: %s", type(exc).__name__) #Writes error information to the server log.

        return JSONResponse(
            status_code=500,
            content={"error": "Database operation failed"}
        )

    @staticmethod
    def register(app: FastAPI):
        app.add_exception_handler(
            WasteAnalyticsError,
            WasteAnalyticsErrorHandler.handle_application_error
        )

        app.add_exception_handler(
            SQLAlchemyError,
            WasteAnalyticsErrorHandler.handle_database_error
        )
