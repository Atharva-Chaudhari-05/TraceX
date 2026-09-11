from unittest.mock import MagicMock

from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta, timezone

from backend.app.auth.dependencies import get_current_user, require_role
from backend.app.auth.models import User, Role
from backend.app.core.config import settings
from backend.app.core.postgres import get_db
from backend.app.main import app

client = TestClient(app)

# --- Test Router for RBAC ---
mock_router = APIRouter()

@mock_router.get("/test/admin-only")
def admin_only_endpoint(user: User = Depends(require_role(["Admin"]))):
    return {"message": "Success"}

@mock_router.get("/test/investigator-only")
def investigator_only_endpoint(user: User = Depends(require_role(["Investigator"]))):
    return {"message": "Success"}

@mock_router.get("/test/analyst-only")
def analyst_only_endpoint(user: User = Depends(require_role(["Analyst"]))):
    return {"message": "Success"}

@mock_router.get("/test/multiple-roles")
def multiple_roles_endpoint(user: User = Depends(require_role(["Admin", "Investigator"]))):
    return {"message": "Success"}

@mock_router.get("/test/current-user")
def current_user_endpoint(user: User = Depends(get_current_user)):
    return {"message": "Success", "email": user.email}

app.include_router(mock_router)


# --- Helper functions ---
def create_test_token(email: str, expires_delta: timedelta = timedelta(minutes=15)):
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def override_get_db(mock_user):
    mock_db = MagicMock()
    mock_db.scalar.return_value = mock_user
    return mock_db

def mock_user_with_roles(email: str, roles: list[str], is_active: bool = True):
    user = User(email=email, is_active=is_active)
    user.roles = [Role(name=r) for r in roles]
    return user


# --- Tests for get_current_user ---

def test_missing_token():
    response = client.get("/test/current-user")
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Not authenticated"

def test_invalid_token():
    response = client.get("/test/current-user", headers={"Authorization": "Bearer invalid_token_here"})
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Could not validate credentials"

def test_expired_token():
    expired_token = create_test_token("test@example.com", expires_delta=timedelta(minutes=-15))
    response = client.get("/test/current-user", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Could not validate credentials"

def test_nonexistent_user():
    app.dependency_overrides[get_db] = lambda: override_get_db(None)
    token = create_test_token("nonexistent@example.com")
    
    response = client.get("/test/current-user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Could not validate credentials"
    app.dependency_overrides.pop(get_db, None)

def test_inactive_user():
    user = mock_user_with_roles("inactive@example.com", ["Admin"], is_active=False)
    app.dependency_overrides[get_db] = lambda: override_get_db(user)
    token = create_test_token("inactive@example.com")
    
    response = client.get("/test/current-user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "User account is inactive"
    app.dependency_overrides.pop(get_db, None)

def test_valid_token_resolves_user():
    user = mock_user_with_roles("active@example.com", ["Admin"])
    app.dependency_overrides[get_db] = lambda: override_get_db(user)
    token = create_test_token("active@example.com")
    
    response = client.get("/test/current-user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "active@example.com"
    app.dependency_overrides.pop(get_db, None)


# --- Tests for require_role ---

def test_admin_allowed_on_admin_endpoint():
    user = mock_user_with_roles("admin@example.com", ["Admin"])
    app.dependency_overrides[get_db] = lambda: override_get_db(user)
    token = create_test_token("admin@example.com")
    
    response = client.get("/test/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    app.dependency_overrides.pop(get_db, None)

def test_admin_rejected_on_investigator_endpoint():
    user = mock_user_with_roles("admin@example.com", ["Admin"])
    app.dependency_overrides[get_db] = lambda: override_get_db(user)
    token = create_test_token("admin@example.com")
    
    response = client.get("/test/investigator-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["error"]["message"] == "Not enough permissions"
    app.dependency_overrides.pop(get_db, None)

def test_investigator_allowed_on_investigator_endpoint():
    user = mock_user_with_roles("inv@example.com", ["Investigator"])
    app.dependency_overrides[get_db] = lambda: override_get_db(user)
    token = create_test_token("inv@example.com")
    
    response = client.get("/test/investigator-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    app.dependency_overrides.pop(get_db, None)

def test_analyst_allowed_on_analyst_endpoint():
    user = mock_user_with_roles("ana@example.com", ["Analyst"])
    app.dependency_overrides[get_db] = lambda: override_get_db(user)
    token = create_test_token("ana@example.com")
    
    response = client.get("/test/analyst-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    app.dependency_overrides.pop(get_db, None)

def test_multiple_roles_endpoint_allowed():
    user = mock_user_with_roles("inv@example.com", ["Investigator"])
    app.dependency_overrides[get_db] = lambda: override_get_db(user)
    token = create_test_token("inv@example.com")
    
    # Should allow Investigator
    response = client.get("/test/multiple-roles", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    app.dependency_overrides.pop(get_db, None)

def test_multiple_roles_endpoint_rejected():
    user = mock_user_with_roles("ana@example.com", ["Analyst"])
    app.dependency_overrides[get_db] = lambda: override_get_db(user)
    token = create_test_token("ana@example.com")
    
    # Analyst not allowed on Admin+Investigator endpoint
    response = client.get("/test/multiple-roles", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    app.dependency_overrides.pop(get_db, None)
