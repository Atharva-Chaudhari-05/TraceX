from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.app.auth.models import User
from backend.app.auth.security import decode_access_token, get_password_hash
from backend.app.core.postgres import get_db
from backend.app.main import app

client = TestClient(app)


def override_get_db(mock_user):
    mock_db = MagicMock()
    mock_db.scalar.return_value = mock_user
    return mock_db


def test_login_success():
    """Test successful login returns a decodable JWT token."""
    mock_user = User(
        email="test@example.com",
        hashed_password=get_password_hash("correct_password"),
        is_active=True,
    )
    app.dependency_overrides[get_db] = lambda: override_get_db(mock_user)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "correct_password"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    decoded = decode_access_token(data["access_token"])
    assert decoded is not None
    assert decoded["sub"] == "test@example.com"

    app.dependency_overrides.pop(get_db, None)


def test_login_for_access_token_success():
    """Test successful login via the OAuth2 Form Data endpoint returns a decodable JWT token."""
    mock_user = User(
        email="test_form@example.com",
        hashed_password=get_password_hash("correct_password"),
        is_active=True,
    )
    app.dependency_overrides[get_db] = lambda: override_get_db(mock_user)

    response = client.post(
        "/api/v1/auth/token",
        data={"username": "test_form@example.com", "password": "correct_password"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verify the JWT can be decoded
    decoded = decode_access_token(data["access_token"])
    assert decoded is not None
    assert decoded["sub"] == "test_form@example.com"

    app.dependency_overrides.pop(get_db, None)


def test_login_unknown_user():
    """Test login fails securely for an unknown user."""
    app.dependency_overrides[get_db] = lambda: override_get_db(None)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@example.com", "password": "any_password"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Incorrect email or password"

    app.dependency_overrides.pop(get_db, None)


def test_login_incorrect_password():
    """Test login fails securely for an incorrect password."""
    mock_user = User(
        email="test@example.com",
        hashed_password=get_password_hash("correct_password"),
        is_active=True,
    )
    app.dependency_overrides[get_db] = lambda: override_get_db(mock_user)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrong_password"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Incorrect email or password"

    app.dependency_overrides.pop(get_db, None)


def test_login_inactive_user():
    """Test login fails if the user account is inactive."""
    mock_user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("correct_password"),
        is_active=False, # User is inactive
    )
    app.dependency_overrides[get_db] = lambda: override_get_db(mock_user)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "correct_password"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "User account is inactive"

    app.dependency_overrides.pop(get_db, None)


def test_login_invalid_request():
    """Test that FastAPI correctly catches validation errors in the request."""
    # Invalid email format and missing password
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email"},
    )

    assert response.status_code == 422
    data = response.json()
    assert "error" in data

    # Test oversized password
    response_large = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "a" * 100},
    )

    assert response_large.status_code == 422
    data_large = response_large.json()
    assert "error" in data_large
