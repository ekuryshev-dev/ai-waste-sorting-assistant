
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from waste_analytics.error_handler import (
    WasteAnalyticsError,
    WasteAnalyticsErrorHandler
)


def test_custom_error():
    error = WasteAnalyticsError("Invalid item", 400)

    assert error.message == "Invalid item"
    assert error.status_code == 400
    assert str(error) == "Invalid item"
    #create an error object and verify that it correctly stores the message and status.

def test_application_error_handler():
    app = FastAPI()
    WasteAnalyticsErrorHandler.register(app)

    @app.get("/test-error")
    def trigger_error():
        raise WasteAnalyticsError("Test error", 400)

    with TestClient(app) as client:
        response = client.get("/test-error")

    assert response.status_code == 400
    assert response.json() == {"error": "Test error"}

#testing error of database


def test_database_error_handler():
    app = FastAPI() #Creates a test FastAPI application.
    WasteAnalyticsErrorHandler.register(app) #Connects our WasteAnalyticsErrorHandler.

    @app.get("/test-database-error")
    def trigger_database_error(): #Artificially triggers a SQLAlchemyError.
        raise SQLAlchemyError("Test database failure")

    with TestClient(app) as client:
        response = client.get("/test-database-error")

    assert response.status_code == 500 #Verifies that the server returns an HTTP 500 status code.
    assert response.json() == { #Verifies that the client does not receive internal error details.
        "error": "Database operation failed"
    }
