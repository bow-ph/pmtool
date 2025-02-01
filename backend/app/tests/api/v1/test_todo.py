import pytest
import pytest_asyncio
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.services.pdf_analysis_service import PDFAnalysisService
from app.services.caldav_service import CalDAVService
from app.core.auth import create_access_token
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.dependencies import get_caldav_service
from unittest.mock import MagicMock, AsyncMock, patch, ANY
from datetime import datetime, timedelta

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

@pytest_asyncio.fixture
async def mock_caldav_service():
    """Mock CalDAV service for testing"""
    mock_service = AsyncMock(spec=CalDAVService)
    mock_service.is_testing = True
    mock_service._init_storage = MagicMock()  # Not async in actual implementation
    mock_service.create_calendar = AsyncMock(return_value="test/calendar")
    mock_service.storage = MagicMock()  # Storage is not async
    mock_service.storage.folder = "/tmp/caldav_storage"
    mock_service.storage.discover = MagicMock()
    mock_service.storage.discover.return_value = MagicMock()
    mock_service.storage.discover.return_value.upload = MagicMock()
    mock_service.storage.discover.return_value.list = MagicMock(return_value=[])
    mock_service.storage.discover.return_value.get_component = MagicMock(return_value={
        "uid": "test-event-uid",
        "summary": "Test Task",
        "description": "Test Description",
        "dtstart": datetime.now().strftime("%Y%m%dT%H%M%SZ"),
        "dtend": (datetime.now() + timedelta(hours=5)).strftime("%Y%m%dT%H%M%SZ"),
        "x-pm-tool-duration-hours": "5.0",
        "x-pm-tool-hourly-rate": "80.0",
        "x-pm-tool-confidence": "1.0",
        "x-pm-tool-rationale": "Test rationale"
    })

    async def mock_sync(*args, **kwargs):
        print(f"Mock sync called with args: {args}, kwargs: {kwargs}")
        return "test-event-uid"

    mock_service.sync_task_with_calendar = AsyncMock(side_effect=mock_sync)

    async def mock_get_caldav():
        yield mock_service

    app.dependency_overrides[get_caldav_service] = mock_get_caldav
    try:
        yield mock_service
    finally:
        app.dependency_overrides.pop(get_caldav_service, None)

@pytest.fixture
def mock_openai_service():
    with patch('app.services.pdf_analysis_service.OpenAIService') as mock:
        mock_instance = AsyncMock()
        mock_instance.analyze_pdf_text.return_value = {
            "document_analysis": {
                "type": "test",
                "context": "Test document for system validation",
                "client_type": "business",
                "complexity_level": "low",
                "clarity_score": 1.0
            },
            "tasks": [
                {
                    "id": 1,
                    "title": "Test Task",
                    "description": "Test Description",
                    "duration_hours": 5.0,
                    "hourly_rate": 80.0,
                    "estimated_hours": 5.0,
                    "planned_timeframe": "2025-02-10 - 2025-02-12",
                    "confidence": 0.9,
                    "confidence_rationale": "Test task with high confidence",
                    "dependencies": [],
                    "complexity": "low",
                    "requires_client_input": False,
                    "technical_requirements": ["None"],
                    "deliverables": ["Test deliverable"]
                }
            ],
            "hints": [
                {
                    "message": "This is a test hint",
                    "related_task": "Test Task",
                    "priority": "low",
                    "impact": "time",
                    "acus": 8  # 2 ACUs = 15 minutes, so 5 hours = 40 ACUs
                }
            ],
            "total_estimated_hours": 5.0,
            "risk_factors": ["None - test document"],
            "confidence_analysis": {
                "overall_confidence": 1.0,
                "rationale": "Test document",
                "improvement_suggestions": [],
                "accuracy_factors": {
                    "document_clarity": 1.0,
                    "technical_complexity": 0.5,
                    "dependency_risk": 0.0,
                    "client_input_risk": 0.0
                }
            }
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_create_task_with_caldav_sync(test_client, mock_caldav_service, mock_openai_service, db: Session):
    from app.models.project import Project
    from app.models.user import User
    from app.services.caldav_service import CalDAVService
    user = db.query(User).filter(User.email == "admin@pmtool.test").first()
    project = Project(
        name="Test Project", 
        description="Test Description",
        user_id=user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    test_pdf = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n72 712 Td\n(test pdf content) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000079 00000 n\n0000000173 00000 n\n0000000301 00000 n\n0000000379 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n492\n%%EOF"
    files = {"file": ("test.pdf", test_pdf, "application/pdf")}
    project_id = project.id
    
    # Upload PDF and analyze
    response = test_client.post(
        f"/api/v1/projects/{project_id}/analyze-pdf",
        files=files
    )
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content}")
    assert response.status_code == 200
    data = response.json()
    
    # Verify document analysis
    assert "document_analysis" in data
    doc_analysis = data["document_analysis"]
    assert "type" in doc_analysis
    assert "context" in doc_analysis
    assert "client_type" in doc_analysis
    assert "complexity_level" in doc_analysis
    assert "clarity_score" in doc_analysis
    assert isinstance(doc_analysis["clarity_score"], (int, float))
    
    # Verify tasks
    assert "tasks" in data
    tasks = data["tasks"]
    assert len(tasks) > 0
    
    # Verify task structure
    task = tasks[0]
    assert "title" in task
    assert "description" in task
    assert task["description"] == "Test Description"
    assert task["duration_hours"] == 5.0
    assert task["hourly_rate"] == 80.0
    assert task["planned_timeframe"] == "2025-02-10 - 2025-02-12"
    assert task["confidence"] == 0.9
    assert "confidence_rationale" in task
    assert task["complexity"] == "low"
    assert isinstance(task["requires_client_input"], bool)
    assert isinstance(task["technical_requirements"], list)
    assert isinstance(task["deliverables"], list)
    assert task["caldav_event_uid"] is not None
    
    # Verify hints
    assert "hints" in data
    hints = data["hints"]
    assert len(hints) > 0
    hint = hints[0]
    assert "message" in hint
    assert "related_task" in hint
    assert "priority" in hint
    assert "impact" in hint
    
    # Verify confidence analysis
    assert "confidence_analysis" in data
    conf_analysis = data["confidence_analysis"]
    assert "overall_confidence" in conf_analysis
    assert "rationale" in conf_analysis
    assert "improvement_suggestions" in conf_analysis
    assert "accuracy_factors" in conf_analysis
    accuracy = conf_analysis["accuracy_factors"]
    assert "document_clarity" in accuracy
    assert "technical_complexity" in accuracy
    assert "dependency_risk" in accuracy
    assert "client_input_risk" in accuracy
    
    # Verify task appears in todo list with CalDAV sync
    response = test_client.get("/api/v1/todo/list")
    assert response.status_code == 200
    result = response.json()
    assert "items" in result
    todo_tasks = result["items"]
    assert len(todo_tasks) > 0
    
    # Find the task by matching its description and caldav_event_uid
    todo_task = next(t for t in todo_tasks if t["description"] == "Test Description" and t["caldav_event_uid"] == task["caldav_event_uid"])
    assert todo_task["duration_hours"] == 5.0
    assert todo_task["hourly_rate"] == 80.0
    assert todo_task["description"] == "Test Description"
    assert todo_task["confidence_score"] == 0.9
    assert todo_task["confidence_rationale"] is not None
    
    # Verify CalDAV service was called correctly
    # Wait a bit for async operations to complete
    await asyncio.sleep(0.1)
    
    # Verify CalDAV sync was called
    mock_caldav_service.sync_task_with_calendar.assert_awaited_once()
    
    # Get the last call's arguments
    call_args = mock_caldav_service.sync_task_with_calendar.await_args
    assert call_args is not None, "No call arguments found"
    
    # Extract task data and calendar path from the call
    task_data, calendar_path = call_args[0]
    
    # Verify task data
    assert task_data["description"] == "Test Description"
    assert task_data["duration_hours"] == 5.0
    assert task_data["hourly_rate"] == 80.0
    assert task_data["status"] == "pending"
    assert task_data["confidence_score"] == 0.9
    assert isinstance(task_data["start_date"], datetime)
    
    # Verify calendar path
    assert calendar_path == f"{user.id}/calendar"

@pytest.mark.asyncio
async def test_update_task_updates_caldav(test_client, mock_caldav_service, db: Session):
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
    
    # Wait for async operations to complete
    await asyncio.sleep(0.1)
    
    # Verify CalDAV sync was called correctly
    mock_caldav_service.sync_task_with_calendar.assert_awaited_once()
    
    # Get the last call's arguments
    call_args = mock_caldav_service.sync_task_with_calendar.await_args
    assert call_args is not None, "No call arguments found"
    
    task_data, calendar_path = call_args[0]
    
    # Verify the task data
    assert task_data["id"] == task_id
    assert task_data["title"] == "Test Task"
    assert task_data["description"] == "Updated description"
    assert task_data["duration_hours"] == 6.0
    assert task_data["hourly_rate"] == 90.0
    assert task_data["status"] == "in_progress"
    assert isinstance(task_data["start_date"], datetime)
    
    # Verify calendar path
    assert calendar_path == f"{user.id}/calendar"
    
    # Verify task was updated
    response = test_client.get("/api/v1/todo/list")
    assert response.status_code == 200
    
    # Verify the update response format
    update_response = response.json()
    assert update_response["status"] == "success"
    assert "task" in update_response
    task = update_response["task"]
    assert task["description"] == "Updated description"
    assert task["duration_hours"] == 6.0
    assert task["hourly_rate"] == 90.0
    assert task["status"] == "in_progress"
    assert "created_at" in task
    assert "updated_at" in task
    assert task["created_at"] is not None
    assert task["updated_at"] is not None
    
    # Verify task list contains updated task
    response = test_client.get("/api/v1/todo/list")
    assert response.status_code == 200
    result = response.json()
    assert "items" in result
    tasks = result["items"]
    updated_task = next(t for t in tasks if t["description"] == update_data["description"])
    assert updated_task["duration_hours"] == update_data["duration_hours"]
    assert updated_task["hourly_rate"] == update_data["hourly_rate"]
    assert updated_task["status"] == update_data["status"]
