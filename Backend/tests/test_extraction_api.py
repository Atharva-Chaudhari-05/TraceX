import pytest
import os
import sys
from uuid import uuid4
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.auth.models import User, Role
from backend.app.auth.security import create_access_token

client = TestClient(app)

@pytest.fixture
def admin_token(db_session):
    user = db_session.query(User).filter(User.email == "test_admin@tracex.local").first()
    if not user:
        role = db_session.query(Role).filter(Role.name == "Admin").first()
        if not role:
            role = Role(name="Admin")
            db_session.add(role)
            db_session.commit()
            
        user = User(email="test_admin@tracex.local", hashed_password="dummy", is_active=True)
        user.roles.append(role)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
    return create_access_token(data={"sub": user.email})


@pytest.fixture
def viewer_token(db_session):
    user = db_session.query(User).filter(User.email == "test_viewer@tracex.local").first()
    if not user:
        role = db_session.query(Role).filter(Role.name == "Viewer").first()
        if not role:
            role = Role(name="Viewer")
            db_session.add(role)
            db_session.commit()
            
        user = User(email="test_viewer@tracex.local", hashed_password="dummy", is_active=True)
        user.roles.append(role)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
    return create_access_token(data={"sub": user.email})


def test_extraction_trigger_requires_auth():
    response = client.post("/api/v1/extraction/trigger")
    assert response.status_code == 401


def test_extraction_trigger_rbac(viewer_token):
    response = client.post("/api/v1/extraction/trigger", headers={"Authorization": f"Bearer {viewer_token}"})
    assert response.status_code == 403


def test_extraction_trigger_success(admin_token):
    response = client.post("/api/v1/extraction/trigger", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "batch_id" in data
    
    # Check status
    status_response = client.get(f"/api/v1/extraction/status/{data['batch_id']}", headers={"Authorization": f"Bearer {admin_token}"})
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["id"] == data["batch_id"]
    assert status_data["status"] in ["RUNNING", "COMPLETED", "FAILED"]


def test_extraction_trigger_idempotency(admin_token):
    # First trigger
    response1 = client.post("/api/v1/extraction/trigger", headers={"Authorization": f"Bearer {admin_token}"})
    # Since test_extraction_trigger_success already ran, the first trigger here might actually be the duplicate
    # Let's handle both cases gracefully
    data1 = response1.json()
    
    # Second trigger
    response2 = client.post("/api/v1/extraction/trigger", headers={"Authorization": f"Bearer {admin_token}"})
    assert response2.status_code == 200 # We return 200 or 409 depending on logic. Wait, I wrote `return ExtractionTriggerResponse` which is a 200 OK.
    data2 = response2.json()
    
    assert "batch_id" in data2
    assert "already running" in data2["message"] or "already been completed" in data2["message"]
    
    # They should return the same batch ID!
    if "batch_id" in data1 and response1.status_code == 200:
        assert data1["batch_id"] == data2["batch_id"]
