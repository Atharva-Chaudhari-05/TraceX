import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.main import app

client = TestClient(app)

error_router = APIRouter()

class DummyModel(BaseModel):
    value: int

@error_router.get("/test/error/http")
def throw_http_error():
    raise StarletteHTTPException(status_code=404, detail="Resource not found here")

@error_router.post("/test/error/validation")
def throw_validation_error(model: DummyModel):
    return {"value": model.value}

@error_router.get("/test/error/unexpected")
def throw_unexpected_error():
    raise ValueError("This is an internal database or logic exception")

app.include_router(error_router)


def test_http_exception_formatting():
    response = client.get("/test/error/http")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert data["error"]["message"] == "Resource not found here"
    assert "request_id" in data["error"]

def test_validation_error_formatting():
    response = client.post("/test/error/validation", json={"value": "not-an-int"})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in data["error"]

import asyncio

def test_unexpected_exception_formatting():
    from backend.app.core.errors import global_exception_handler
    from fastapi import Request
    
    async def run_handler():
        request = Request({"type": "http", "headers": []})
        return await global_exception_handler(request, ValueError("This is an internal database or logic exception"))
        
    response = asyncio.run(run_handler())
    
    assert response.status_code == 500
    import json
    data = json.loads(response.body)
    assert "error" in data
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert data["error"]["message"] == "An unexpected server error occurred."
    assert "request_id" in data["error"]
    # Ensure stack trace/original message is NOT exposed
    assert "database or logic exception" not in str(data)

def test_request_id_generation():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]

def test_supplied_request_id():
    custom_id = "custom-client-id-123"
    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id

def test_invalid_request_id():
    custom_id = "invalid id with spaces and very long " * 10
    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    # Should generate a new UUID since the supplied one is invalid
    assert response.headers["X-Request-ID"] != custom_id
    assert len(response.headers["X-Request-ID"]) > 0

def test_authentication_401_formatting():
    # Attempting to access protected RBAC endpoint without token
    response = client.get("/test/admin-only")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "UNAUTHORIZED"
    assert data["error"]["message"] == "Not authenticated"
    assert "request_id" in data["error"]
