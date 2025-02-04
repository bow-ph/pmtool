import pytest
from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from app.core.database import SessionLocal
from app.core.auth import create_access_token
import json
import os
import shutil
from pathlib import Path

# Test fixtures
@pytest.fixture(scope="function")
def test_uploads_dir():
    # Create test uploads directory
    uploads_dir = Path("/home/ubuntu/repos/pmtool/backend/uploads/pdfs")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    yield str(uploads_dir)
    # Clean up after test
    if uploads_dir.exists():
        shutil.rmtree(uploads_dir)

@pytest.fixture(scope="function")
def test_pdf_file():
    # Create a test PDF file with test content
    content = "test pdf content"
    pdf_path = Path("test.pdf")
    
    # Use reportlab to create a valid PDF
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(100, 750, content)
    c.save()
    
    yield str(pdf_path)
    # Clean up
    if pdf_path.exists():
        pdf_path.unlink()

def test_pdf_analysis_endpoint(client, db, test_user, auth_headers, test_uploads_dir, test_pdf_file):
    # Create project for test
    project = Project(
        name="Test Project",
        description="Test Description",
        user_id=test_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Upload PDF
    with open(test_pdf_file, "rb") as f:
        files = {"file": ("test.pdf", f, "application/pdf")}
        response = client.post(
            "/api/v1/pdf/upload-pdfs",
            files=files,
            headers=auth_headers
        )
    assert response.status_code == 200, f"PDF upload failed: {response.text}"
    pdf_url = response.json()["pdf_url"]

    # Analyze PDF
    with open(test_pdf_file, "rb") as f:
        files = {"file": ("test.pdf", f, "application/pdf")}
        response = client.post(
            f"/api/v1/pdf/analyze/{project.id}",
            files=files,
            headers=auth_headers
        )
    assert response.status_code == 200, f"PDF analysis failed: {response.text}"
    result = response.json()

    # Verify response structure
    assert "tasks" in result, "Response missing tasks"
    assert len(result["tasks"]) > 0, "No tasks generated from analysis"
    task = result["tasks"][0]
    
    # Verify task fields
    required_fields = [
        "title", "description", "duration_hours", "hourly_rate",
        "estimated_hours", "confidence_score", "confidence_rationale"
    ]
    for field in required_fields:
        assert field in task, f"Task missing {field}"
    
    # Verify numeric fields
    numeric_fields = ["duration_hours", "hourly_rate", "estimated_hours", "confidence_score"]
    for field in numeric_fields:
        assert isinstance(task[field], (int, float)), f"{field} is not a number"
    
    # Verify task creation in database
    db_task = db.query(Task).filter(Task.project_id == project.id).first()
    assert db_task is not None, "Task not created in database"
    assert db_task.duration_hours == task["duration_hours"]
    assert db_task.hourly_rate == task["hourly_rate"]
    assert db_task.title == task["title"]
    
    # Verify hints
    assert "hints" in result, "Response missing hints"
    if result["hints"]:
        hint = result["hints"][0]
        assert "message" in hint, "Hint missing message"
        assert "related_task" in hint, "Hint missing related_task"

def test_task_creation_with_new_fields(db, test_user, test_project):
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "duration_hours": 5.0,
        "hourly_rate": 80.0,
        "estimated_hours": 5.0,
        "project_id": test_project.id,
        "confidence_score": 0.9,
        "confidence_rationale": "Test task with high confidence"
    }

    # Create task
    task = Task(**task_data)
    db.add(task)
    db.commit()
    db.refresh(task)

    # Verify task was created with correct fields
    assert task.duration_hours == 5.0, "duration_hours not saved correctly"
    assert task.hourly_rate == 80.0, "hourly_rate not saved correctly"
    assert task.title == "Test Task", "title not saved correctly"
    
    # Clean up
    db.delete(task)
    db.commit()
