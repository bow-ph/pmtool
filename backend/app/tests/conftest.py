import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.project import Project
import os
from app.core.auth import create_access_token, get_password_hash

# Test database URL
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost/pmtool_test"

# Create test engine
test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    nested = connection.begin_nested()
    
    @event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()
    
    app.dependency_overrides[get_db] = lambda: session
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def test_user(db):
    user = User(
        email="admin@pmtool.test",
        hashed_password=get_password_hash("pmtool"),
        is_active=True,
        subscription_type="trial"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def auth_headers(test_user):
    access_token = create_access_token({"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def test_project(db, test_user):
    project = Project(
        name="Test Project",
        description="Test Description"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
