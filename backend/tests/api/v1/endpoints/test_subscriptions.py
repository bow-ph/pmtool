import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.subscription import Subscription
from app.models.user import User
from datetime import datetime, timedelta

client = TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        is_active=True
    )

@pytest.fixture
def mock_subscription():
    return Subscription(
        id=1,
        user_id=1,
        mollie_id="sub_test",
        customer_id="cust_test",
        package_id=1,
        package_type="team",
        project_limit=10,
        status="active",
        amount=119.0,
        interval="3 months",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=90)
    )

def test_get_my_subscription(client, test_user, test_package, test_subscription):
    """Test getting current user's subscription"""
    from app.core.auth import create_access_token
    access_token = create_access_token({"sub": test_user.email})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.get("/api/v1/subscriptions/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_subscription.id
    assert data["status"] == "active"
    assert data["package_id"] == test_package.id

def test_get_my_subscription_not_found(client, test_user):
    """Test getting subscription when none exists"""
    from app.core.auth import create_access_token
    from app.core.database import SessionLocal
    from sqlalchemy import text
    
    # Delete any existing subscriptions for this user
    db = SessionLocal()
    db.execute(text("DELETE FROM test_subscriptions WHERE user_id = :user_id"), {"user_id": test_user.id})
    db.commit()
    
    access_token = create_access_token({"sub": test_user.email})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.get("/api/v1/subscriptions/me", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "No active subscription found"

def test_check_project_limit(client, test_user, test_subscription):
    """Test checking project creation limit"""
    from app.core.auth import create_access_token
    access_token = create_access_token({"sub": test_user.email})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.get("/api/v1/subscriptions/me/project-limit", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["can_create"], bool)
    
    # Only check count and limit if subscription exists and is active
    if data["can_create"] or "current_count" in data:
        assert isinstance(data["current_count"], int)
        assert isinstance(data["limit"], (int, type(None)))

def test_cancel_subscription(client, test_user, test_subscription):
    """Test subscription cancellation"""
    from app.core.auth import create_access_token
    access_token = create_access_token({"sub": test_user.email})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.post("/api/v1/subscriptions/me/cancel", json={"reason": "Test cancellation"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "end_date" in data

def test_cancel_subscription_not_found(client, test_user):
    """Test cancellation when no subscription exists"""
    from app.core.auth import create_access_token
    from app.core.database import SessionLocal
    from sqlalchemy import text
    
    # Delete any existing subscriptions for this user
    db = SessionLocal()
    db.execute(text("DELETE FROM test_subscriptions WHERE user_id = :user_id"), {"user_id": test_user.id})
    db.commit()
    
    access_token = create_access_token({"sub": test_user.email})
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.post("/api/v1/subscriptions/me/cancel", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "No active subscription found"
