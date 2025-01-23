import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.package import Package
from app.models.user import User

client = TestClient(app)

@pytest.fixture
def test_package(db_session):
    package = Package(
        name="Test Package",
        description="Test Description",
        price=99.99,
        interval="3 months",
        max_projects=10,
        features=["Feature 1", "Feature 2"],
        button_text="Subscribe Now"
    )
    db_session.add(package)
    db_session.commit()
    return package

def test_list_packages(db_session, test_package):
    """Test listing all active packages"""
    response = client.get("/api/v1/packages")
    assert response.status_code == 200
    packages = response.json()
    assert len(packages) >= 1
    assert packages[0]["name"] == test_package.name
    assert packages[0]["price"] == test_package.price

def test_create_package_unauthorized(db_session):
    """Test that non-admin users cannot create packages"""
    package_data = {
        "name": "New Package",
        "description": "New Description",
        "price": 149.99,
        "interval": "3 months",
        "max_projects": 15,
        "features": ["Feature 1", "Feature 2"],
        "button_text": "Get Started"
    }
    response = client.post("/api/v1/packages", json=package_data)
    assert response.status_code == 403

def test_create_package_authorized(db_session, admin_user):
    """Test package creation by admin"""
    package_data = {
        "name": "New Package",
        "description": "New Description",
        "price": 149.99,
        "interval": "3 months",
        "max_projects": 15,
        "features": ["Feature 1", "Feature 2"],
        "button_text": "Get Started"
    }
    response = client.post(
        "/api/v1/packages",
        json=package_data,
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == package_data["name"]
    assert data["price"] == package_data["price"]

def test_update_package(db_session, admin_user, test_package):
    """Test updating a package"""
    update_data = {
        "price": 199.99,
        "description": "Updated Description"
    }
    response = client.put(
        f"/api/v1/packages/{test_package.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == update_data["price"]
    assert data["description"] == update_data["description"]

def test_delete_package(db_session, admin_user, test_package):
    """Test soft deleting a package"""
    response = client.delete(
        f"/api/v1/packages/{test_package.id}",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    
    # Verify package is not returned in list
    response = client.get("/api/v1/packages")
    packages = response.json()
    assert not any(p["id"] == test_package.id for p in packages)
