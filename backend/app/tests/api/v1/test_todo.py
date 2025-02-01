import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.services.pdf_analysis_service import PDFAnalysisService
from app.services.caldav_service import CalDAVService
from app.core.auth import create_access_token
from app.core.config import settings
from app.core.database import SessionLocal
from unittest.mock import MagicMock, patch
from datetime import timedelta

@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_test_database():
    from app.core.database import Base, engine, SessionLocal
    from app.models.user import User
    from app.core.auth import get_password_hash
    from sqlalchemy.exc import IntegrityError
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == "admin@pmtool.test").first()
        if not existing_user:
            test_user = User(
                email="admin@pmtool.test",
                hashed_password=get_password_hash("pmtool"),
                is_active=True,
                subscription_type="trial"
            )
            db.add(test_user)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
        yield
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_client():
    access_token = create_access_token(
        data={"sub": "admin@pmtool.test"},
        expires_delta=timedelta(minutes=30)
    )
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {access_token}"}
    return client

@pytest.fixture
def mock_caldav_service():
    with patch('app.services.caldav_service.CalDAVService') as mock:
        mock_instance = MagicMock()
        mock_instance.sync_task_with_calendar.return_value = "test-event-uid"
        mock_instance.create_calendar.return_value = "test/calendar"
        mock_instance.storage = MagicMock()
        mock_instance.storage.discover.return_value = MagicMock()
        mock_instance.storage.discover.return_value.upload = MagicMock()
        mock_instance.storage.discover.return_value.list = MagicMock(return_value=[])
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_openai_service():
    with patch('app.services.pdf_analysis_service.OpenAIService') as mock:
        mock_instance = MagicMock()
        mock_instance.analyze_pdf.return_value = {
            "tasks": [
                {
                    "title": "Test Task",
                    "description": "Test Description",
                    "duration_hours": 5.0,
                    "hourly_rate": 80.0,
                    "estimated_hours": 5.0,
                    "confidence": 0.9,
                    "confidence_rationale": "Test rationale"
                }
            ],
            "hints": [
                {
                    "message": "Test hint",
                    "related_task": "Test Task"
                }
            ]
        }
        mock.return_value = mock_instance
        yield mock_instance

def test_create_task_with_caldav_sync(test_client, mock_caldav_service, mock_openai_service, db: Session):
    from app.models.project import Project
    from app.models.user import User
    user = db.query(User).filter(User.email == "admin@pmtool.test").first()
    project = Project(
        name="Test Project", 
        description="Test Description",
        user_id=user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    test_pdf = b"%PDF-1.4\nTest PDF Content"
    files = {"file": ("test.pdf", test_pdf, "application/pdf")}
    project_id = project.id
    
    # Upload PDF and analyze
    response = test_client.post(
        f"/api/v1/projects/{project_id}/analyze-pdf",
        files=files
    )
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    tasks = data["tasks"]
    assert len(tasks) > 0
    
    # Verify task creation and CalDAV sync
    task = tasks[0]
    assert task["id"] is not None
    assert task["caldav_event_uid"] is not None
    assert task["title"] == "Test Task"
    assert task["description"] == "Test Description"
    assert task["duration_hours"] == 5.0
    assert task["hourly_rate"] == 80.0
    assert task["status"] == "pending"
    
    # Verify task appears in todo list with CalDAV sync
    response = test_client.get("/api/v1/todo/list")
    assert response.status_code == 200
    result = response.json()
    assert "items" in result
    todo_tasks = result["items"]
    assert len(todo_tasks) > 0
    
    todo_task = next(t for t in todo_tasks if t["id"] == task["id"])
    assert todo_task["caldav_event_uid"] is not None
    assert todo_task["duration_hours"] == 5.0
    assert todo_task["hourly_rate"] == 80.0
    assert todo_task["title"] == "Test Task"
    assert todo_task["description"] == "Test Description"
    assert todo_task["confidence_score"] == 0.9
    assert "Test rationale" in todo_task["confidence_rationale"]
    
    # Verify CalDAV service was called correctly
    mock_caldav_service.sync_task_with_calendar.assert_called_with(
        {
            "id": task["id"],
            "title": "Test Task",
            "description": "Test Description",
            "duration_hours": 5.0,
            "hourly_rate": 80.0,
            "status": "pending",
            "confidence_score": 0.9,
            "confidence_rationale": mock_openai_service.return_value.analyze_pdf.return_value["tasks"][0]["confidence_rationale"]
        },
        f"{user.id}/calendar"
    )

def test_update_task_updates_caldav(test_client, mock_caldav_service, db: Session):
    # Create test project and task
    from app.models.project import Project
    from app.models.task import Task
    from app.models.user import User
    
    user = db.query(User).filter(User.email == "admin@pmtool.test").first()
    project = Project(
        name="Test Project", 
        description="Test Description",
        user_id=user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    task = Task(
        title="Test Task",
        description="Test Description",
        duration_hours=5.0,
        hourly_rate=80.0,
        project_id=project.id,
        status="pending",
        priority="medium",
        confidence_score=1.0,
        confidence_rationale="Test task",
        estimated_hours=5.0
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Test updating the task
    task_id = task.id
    update_data = {
        "description": "Updated description",
        "duration_hours": 6.0,
        "hourly_rate": 90.0,
        "status": "in_progress"
    }
    
    response = test_client.put(
        f"/api/v1/todo/tasks/{task_id}",
        json=update_data
    )
    assert response.status_code == 200
    
    # Verify CalDAV sync was called
    mock_caldav_service.sync_task_with_calendar.assert_called_once()
    
    # Verify task was updated
    response = test_client.get("/api/v1/todo/list")
    assert response.status_code == 200
    
    # First verify the update response format
    update_response = response.json()
    assert update_response["status"] == "success"
    updated_task = update_response["task"]
    assert updated_task["id"] == task_id
    assert updated_task["description"] == update_data["description"]
    assert updated_task["duration_hours"] == update_data["duration_hours"]
    assert updated_task["hourly_rate"] == update_data["hourly_rate"]
    assert updated_task["status"] == update_data["status"]
    
    # Then verify the task list
    result = response.json()
    assert "items" in result
    tasks = result["items"]
    task = next(t for t in tasks if t["id"] == task_id)
    assert task["description"] == update_data["description"]
    assert task["duration_hours"] == update_data["duration_hours"]
    assert task["hourly_rate"] == update_data["hourly_rate"]
    assert task["status"] == update_data["status"]
