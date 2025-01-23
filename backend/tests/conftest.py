import pytest
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.auth import get_password_hash, create_access_token
from app.models.user import User
from app.models.package import Package
from fastapi.testclient import TestClient
from app.main import app

# Test database URL
DB_USER = os.getenv("TEST_DB_USER", "postgres")
DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "postgres")
DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
DB_NAME = os.getenv("TEST_DB_NAME", "test_bow_db")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def admin_user(db_session):
    """Create an admin user and return with token"""
    # Clean up any existing admin user
    test_admin_email = os.getenv("TEST_ADMIN_EMAIL", "dummy_admin@test.local")
    db_session.query(User).filter(User.email == test_admin_email).delete()
    db_session.commit()
    
    test_admin_password = os.getenv("TEST_ADMIN_PASSWORD", "dummy_password_for_testing")
    user = User(
        email=test_admin_email,
        hashed_password=get_password_hash(test_admin_password),
        is_active=True,
        is_superuser=True,
        client_type="private"  # Set default client type
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "user": user,
        "token": access_token
    }

@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a regular test user"""
    test_user_email = os.getenv("TEST_USER_EMAIL", "test@example.com")
    test_user_password = os.getenv("TEST_USER_PASSWORD", "dummy_password_for_testing")
    user = User(
        email=test_user_email,
        hashed_password=get_password_hash(test_user_password),
        is_active=True,
        client_type="private"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_company_user(db_session):
    """Create a company test user"""
    test_company_email = os.getenv("TEST_COMPANY_EMAIL", "company@example.com")
    test_company_password = os.getenv("TEST_COMPANY_PASSWORD", "dummy_password_for_testing")
    test_company_name = os.getenv("TEST_COMPANY_NAME", "Test Company")
    test_company_vat = os.getenv("TEST_COMPANY_VAT", "DE000000000")
    
    user = User(
        email=test_company_email,
        hashed_password=get_password_hash(test_company_password),
        is_active=True,
        client_type="company",
        company_name=test_company_name,
        vat_number=test_company_vat
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_package(db_session):
    """Create a test package"""
    test_package_name = os.getenv("TEST_PACKAGE_NAME", "Test Package")
    test_package_price = float(os.getenv("TEST_PACKAGE_PRICE", "99.99"))
    test_package_interval = os.getenv("TEST_PACKAGE_INTERVAL", "3 months")
    test_package_trial_days = int(os.getenv("TEST_PACKAGE_TRIAL_DAYS", "30"))
    test_package_max_projects = int(os.getenv("TEST_PACKAGE_MAX_PROJECTS", "10"))
    
    package = Package(
        name=test_package_name,
        description="Test package for automated testing",
        price=test_package_price,
        interval=test_package_interval,
        trial_days=test_package_trial_days,
        max_projects=test_package_max_projects,
        features=["Feature 1", "Feature 2"],
        button_text="Get Test Package",
        is_active=True,
        sort_order=1
    )
    db_session.add(package)
    db_session.commit()
    db_session.refresh(package)
    return package
