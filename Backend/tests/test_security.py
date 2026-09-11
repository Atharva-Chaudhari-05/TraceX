from datetime import timedelta

from backend.app.auth.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    """Test that passwords hash securely and verify correctly."""
    password = "supersecretpassword123!"
    hashed = get_password_hash(password)
    
    # Hashes should not equal plaintext
    assert hashed != password
    # Hashes should verify the correct password
    assert verify_password(password, hashed) is True
    # Hashes should fail on incorrect passwords
    assert verify_password("wrongpassword", hashed) is False
    # Malformed hashes should fail safely
    assert verify_password(password, "malformedhash") is False


def test_create_and_decode_access_token():
    """Test successful creation and decoding of a JWT access token."""
    data = {"sub": "user@example.com", "role": "Investigator"}
    token = create_access_token(data=data)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == data["sub"]
    assert decoded["role"] == data["role"]
    assert "exp" in decoded


def test_invalid_jwt():
    """Test that completely invalid tokens are rejected safely."""
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.payload"
    decoded = decode_access_token(invalid_token)
    assert decoded is None


def test_expired_jwt():
    """Test that expired tokens are rejected safely."""
    data = {"sub": "user@example.com"}
    # Create a token that expires immediately (-1 second)
    token = create_access_token(data=data, expires_delta=timedelta(seconds=-1))
    
    decoded = decode_access_token(token)
    assert decoded is None
