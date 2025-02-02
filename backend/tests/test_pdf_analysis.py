import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
import os
import json
import asyncio
from pytest_mock import MockerFixture
from app.main import app
from app.services.openai_service import OpenAIService
from app.services.pdf_analysis_service import PDFAnalysisService
from app.models.project import Project
from app.models.user import User
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user

# Configure test client
client = TestClient(app)

@pytest.fixture
def mock_current_user():
    mock_user = User(
        id=1,
        email="test@example.com",
        is_active=True,
        subscription_type="enterprise"
    )
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield mock_user
    app.dependency_overrides = {}

@pytest.fixture
def mock_db():
    mock_session = MagicMock(spec=Session)
    
    # Mock project query
    mock_project = Project(
        id=1,
        user_id=1,
        name="Test Project",
        description="Test Description",
        created_at="2024-02-01T00:00:00",
        status="active",
        is_active=True
    )
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_project
    mock_session.query.return_value = mock_query
    
    # Override get_db dependency
    app.dependency_overrides[get_db] = lambda: mock_session
    yield mock_session
    app.dependency_overrides = {}

@pytest.fixture
def mock_pdf_content():
    return "Test PDF content for analysis"

@pytest.fixture
def mock_pdf_service(mocker: MockerFixture):
    mock_service = mocker.patch('app.services.pdf_analysis_service.PDFAnalysisService')
    mock_service.return_value.read_pdf_content.return_value = "Test PDF content for analysis"
    return mock_service

@pytest.fixture
def mock_openai_response():
    return {
        "document_analysis": {
            "type": "quote",
            "context": "Test document context",
            "client_type": "business",
            "complexity_level": "medium",
            "clarity_score": 0.8
        },
        "tasks": [
            {
                "title": "Test Task",
                "description": "Test task description",
                "duration_hours": 2.5,
                "hourly_rate": 80.0,
                "estimated_hours": 2.5,
                "planned_timeframe": "2024-02-01 - 2024-02-02",
                "confidence": 0.9,
                "confidence_rationale": "Clear task description",
                "dependencies": [],
                "complexity": "low",
                "requires_client_input": False,
                "technical_requirements": ["Python"],
                "deliverables": ["Code"]
            }
        ],
        "hints": [],
        "total_estimated_hours": 2.5,
        "risk_factors": [],
        "confidence_analysis": {
            "overall_confidence": 0.9,
            "rationale": "Clear document",
            "improvement_suggestions": [],
            "accuracy_factors": {
                "document_clarity": 0.9,
                "technical_complexity": 0.7,
                "scope_definition": 0.8
            }
        }
    }

@pytest.mark.asyncio
async def test_analyze_pdf_with_retry(mock_pdf_content, mock_pdf_service, mock_openai_response, mock_db, mock_current_user):
    with patch('app.services.openai_service.OpenAIService.analyze_pdf_text') as mock_analyze:
        # Mock analyze_pdf_text to simulate failures and then success
        mock_analyze.side_effect = [
            HTTPException(status_code=429, detail="Rate limit exceeded"),  # First attempt fails
            HTTPException(status_code=429, detail="Rate limit exceeded"),  # Second attempt fails
            mock_openai_response  # Third attempt succeeds
        ]

        # Test the analysis endpoint
        response = client.post(
            "/api/v1/projects/1/analyze-pdf/test.pdf",
            headers={"Authorization": "Bearer test-token"},
            json={"content": mock_pdf_content}
        )

        assert response.status_code == 200
        result = response.json()
        
        # Verify retry mechanism
        assert mock_analyze.call_count == 3
        
        # Verify response structure
        assert "tasks" in result
        assert len(result["tasks"]) > 0
        assert "title" in result["tasks"][0]
        assert "duration_hours" in result["tasks"][0]
        assert "hourly_rate" in result["tasks"][0]

@pytest.mark.asyncio
async def test_analyze_pdf_max_retries(mock_pdf_content, mock_pdf_service, mock_db, mock_current_user):
    with patch('app.services.openai_service.OpenAIService.analyze_pdf_text') as mock_analyze:
        # Mock analyze_pdf_text to simulate consistent failures
        mock_analyze.side_effect = [
            HTTPException(status_code=429, detail="Rate limit exceeded")
            for _ in range(5)  # Fail all 5 attempts
        ]
        
        # Test the analysis endpoint
        response = client.post(
            "/api/v1/projects/1/analyze-pdf/test.pdf",
            headers={"Authorization": "Bearer test-token"},
            json={"content": mock_pdf_content}
        )
        
        assert response.status_code == 500
        assert "Rate limit exceeded" in response.json()["detail"]
        assert mock_analyze.call_count == 5  # Max retries
