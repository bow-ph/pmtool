import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import openai
from app.services.openai_service import OpenAIService
import json

@pytest.fixture
def openai_service():
    with patch.dict('os.environ', {'Open_AI_API': 'test-key'}):
        return OpenAIService()

@pytest.mark.asyncio
async def test_analyze_pdf_text(openai_service):
    mock_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "tasks": [
                        {
                            "description": "Test task",
                            "estimated_hours": 4.0,
                            "confidence": 0.8,
                            "dependencies": []
                        }
                    ],
                    "total_estimated_hours": 4.0,
                    "risk_factors": ["Test risk"]
                })
            }
        }]
    }
    
    with patch('openai.ChatCompletion.acreate', return_value=mock_response):
        result = await openai_service.analyze_pdf_text("Test PDF content")
        result_dict = json.loads(result)
        
        assert "tasks" in result_dict
        assert len(result_dict["tasks"]) == 1
        assert result_dict["tasks"][0]["estimated_hours"] == 4.0
        assert result_dict["total_estimated_hours"] == 4.0

@pytest.mark.asyncio
async def test_analyze_financial_impact(openai_service):
    mock_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
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
            }
        }]
    }
    
    project_stats = {"total_estimated_hours": 40}
    tasks = [{"description": "Test task", "estimated_hours": 4}]
    
    with patch('openai.ChatCompletion.acreate', return_value=mock_response):
        result = await openai_service.analyze_financial_impact(project_stats, tasks)
        result_dict = json.loads(result)
        
        assert "financial_impact" in result_dict
        assert result_dict["financial_impact"]["risk_level"] == "medium"
        assert "time_impact" in result_dict
        assert len(result_dict["recommendations"]) == 1

@pytest.mark.asyncio
async def test_validate_time_estimates(openai_service):
    mock_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
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
            }
        }]
    }
    
    tasks = [{"id": "1", "description": "Test task", "estimated_hours": 4}]
    
    with patch('openai.ChatCompletion.acreate', return_value=mock_response):
        result = await openai_service.validate_time_estimates(tasks)
        result_dict = json.loads(result)
        
        assert "validated_tasks" in result_dict
        assert len(result_dict["validated_tasks"]) == 1
        assert "overall_assessment" in result_dict

@pytest.mark.asyncio
async def test_openai_rate_limit_error(openai_service):
    with patch('openai.ChatCompletion.acreate', side_effect=openai.error.RateLimitError()):
        with pytest.raises(HTTPException) as exc_info:
            await openai_service.analyze_pdf_text("Test content")
        assert exc_info.value.status_code == 429

@pytest.mark.asyncio
async def test_openai_api_error(openai_service):
    with patch('openai.ChatCompletion.acreate', side_effect=openai.error.APIError()):
        with pytest.raises(HTTPException) as exc_info:
            await openai_service.analyze_pdf_text("Test content")
        assert exc_info.value.status_code == 500
