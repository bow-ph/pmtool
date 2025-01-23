import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.estimation_service import EstimationService
import json

@pytest.fixture
def db_session():
    return MagicMock()

@pytest.fixture
def estimation_service(db_session):
    with patch('app.services.openai_service.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock()
        mock_openai.return_value = mock_client
        service = EstimationService(db_session)
        return service

def test_analyze_estimate_accuracy(estimation_service, db_session):
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.estimated_hours = 4.0
    mock_task.actual_hours = 5.0
    
    db_session.query().filter().first.return_value = mock_task
    
    result = estimation_service.analyze_estimate_accuracy(1)
    assert result["status"] == "analyzed"
    assert result["deviation_hours"] == 1.0
    assert result["deviation_percentage"] == 25.0
    assert result["accuracy_rating"] == "good"

def test_get_project_estimation_stats(estimation_service, db_session):
    mock_project = MagicMock()
    mock_project.id = 1
    
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.estimated_hours = 4.0
    mock_task.actual_hours = 5.0
    
    db_session.query().filter().first.return_value = mock_project
    db_session.query().filter().all.return_value = [mock_task]
    
    result = estimation_service.get_project_estimation_stats(1)
    assert result["status"] == "analyzed"
    assert result["total_tasks"] == 1
    assert result["total_estimated_hours"] == 4.0
    assert result["total_actual_hours"] == 5.0

@pytest.mark.asyncio
async def test_generate_proactive_hints(estimation_service):
    # Mock project stats and tasks
    mock_project_stats = {
        "project_id": 1,
        "total_estimated_hours": 40,
        "total_actual_hours": 45
    }
    
    mock_tasks = [
        MagicMock(
            id=1,
            description="Test task",
            estimated_hours=4.0,
            actual_hours=5.0,
            status="completed",
            confidence_score=0.8
        )
    ]
    
    # Mock database queries
    estimation_service.get_project_estimation_stats = MagicMock(return_value=mock_project_stats)
    estimation_service.db.query().filter().all.return_value = mock_tasks
    
    # Mock OpenAI responses
    mock_financial_analysis = json.dumps({
        "financial_impact": {
            "risk_level": "medium",
            "potential_cost_overrun": 1000.0,
            "confidence": 0.7
        },
        "time_impact": {
            "risk_level": "low",
            "potential_delay_hours": 8.0,
            "confidence": 0.8
        },
        "recommendations": [
            {
                "type": "cost",
                "description": "Test recommendation",
                "priority": "high"
            }
        ]
    })
    
    mock_time_validation = json.dumps({
        "validated_tasks": [
            {
                "task_id": "1",
                "original_estimate": 4.0,
                "suggested_estimate": 5.0,
                "confidence": 0.8,
                "adjustment_reason": "Test reason"
            }
        ],
        "overall_assessment": {
            "estimation_quality": "good",
            "suggestions": ["Test suggestion"]
        }
    })
    
    with patch('app.services.openai_service.OpenAIService.analyze_financial_impact',
              return_value=mock_financial_analysis), \
         patch('app.services.openai_service.OpenAIService.validate_time_estimates',
              return_value=mock_time_validation):
        
        result = await estimation_service.generate_proactive_hints(1)
        
        assert result["status"] == "success"
        assert "financial_impact" in result
        assert "time_impact" in result
        assert "recommendations" in result
        assert "time_validation" in result
        
        assert result["financial_impact"]["risk_level"] == "medium"
        assert result["time_impact"]["risk_level"] == "low"
        assert len(result["recommendations"]) == 1
