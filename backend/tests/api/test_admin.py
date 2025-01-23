import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User

client = TestClient(app)

def test_get_all_users_unauthorized(db_session):
    """Test that non-admin users cannot access the admin endpoints"""
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 403
    assert "Only administrators" in response.json()["detail"]

def test_filter_users_by_client_type(db_session, admin_user):
    """Test filtering users by client type"""
    # Create test users with different client types
    users = [
        User(email="private@test.com", hashed_password="test", client_type="private"),
        User(email="company@test.com", hashed_password="test", client_type="company",
             company_name="Test Corp", vat_number="DE123456789")
    ]
    for user in users:
        db_session.add(user)
    db_session.commit()

    response = client.get(
        "/api/v1/admin/users?client_type=company",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(user["client_type"] == "company" for user in data)
    assert any(user["company_name"] == "Test Corp" for user in data)

def test_filter_users_by_subscription(db_session, admin_user):
    """Test filtering users by subscription type"""
    users = [
        User(email="trial@test.com", hashed_password="test", subscription_type="trial"),
        User(email="team@test.com", hashed_password="test", subscription_type="team")
    ]
    for user in users:
        db_session.add(user)
    db_session.commit()

    response = client.get(
        "/api/v1/admin/users?subscription_type=team",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(user["subscription_type"] == "team" for user in data)

def test_get_all_users_authorized(db_session, admin_user):
    """Test that admin users can access the user list"""
    # Create some test users
    users = [
        User(
            email=f"test{i}@example.com",
            hashed_password="test",
            is_active=True,
            client_type="private"
        )
        for i in range(3)
    ]
    for user in users:
        db_session.add(user)
    db_session.commit()

    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # At least our test users

def test_get_user_details(db_session, admin_user, test_user):
    """Test getting details of a specific user"""
    response = client.get(
        f"/api/v1/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["client_type"] == test_user.client_type

def test_update_user_status(db_session, admin_user, test_user):
    """Test updating a user's active status"""
    response = client.put(
        f"/api/v1/admin/users/{test_user.id}/status",
        params={"is_active": False},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    
    # Verify the change in database
    updated_user = db_session.query(User).filter(User.id == test_user.id).first()
    assert not updated_user.is_active
