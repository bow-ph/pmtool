import os
from typing import Dict, List, Optional
import openai
from fastapi import HTTPException

class OpenAIService:
    """Service for handling OpenAI API interactions"""
    
    def __init__(self):
        """Initialize the OpenAI service with API key from environment"""
        self.api_key = os.getenv("Open_AI_API")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = self.api_key
        
    async def analyze_pdf_text(self, text: str) -> Dict:
        """
        Analyze PDF text to extract tasks and time estimates
        
        Args:
            text (str): The extracted text from the PDF
            
        Returns:
            Dict: Contains extracted tasks and their time estimates
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a project management assistant specialized in analyzing project documents and extracting tasks with time estimates. Format your response as JSON with the following structure:
{
    "tasks": [
        {
            "description": "Task description",
            "estimated_hours": float,
            "confidence": float (0-1),
            "dependencies": ["other task descriptions"]
        }
    ],
    "total_estimated_hours": float,
    "risk_factors": ["list of potential risks"]
}"""},
                    {"role": "user", "content": f"Extract tasks and time estimates from this project document:\n\n{text}"}
                ]
            )
            return response['choices'][0]['message']['content']
        except openai.error.RateLimitError:
            raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded")
        except openai.error.APIError as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
            
    async def analyze_financial_impact(self, project_stats: Dict, tasks: List[Dict]) -> Dict:
        """
        Analyze financial impact and provide proactive hints based on project statistics and tasks
        
        Args:
            project_stats (Dict): Current project statistics
            tasks (List[Dict]): List of tasks with their estimates and actual times
            
        Returns:
            Dict: Contains financial impact analysis and recommendations
        """
        try:
            # Prepare the data for OpenAI
            context = {
                "project_stats": project_stats,
                "tasks": tasks
            }
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a project management advisor specialized in financial and time impact analysis. Format your response as JSON with the following structure:
{
    "financial_impact": {
        "risk_level": "low|medium|high",
        "potential_cost_overrun": float,
        "confidence": float (0-1)
    },
    "time_impact": {
        "risk_level": "low|medium|high",
        "potential_delay_hours": float,
        "confidence": float (0-1)
    },
    "recommendations": [
        {
            "type": "cost|time|resource",
            "description": "Detailed recommendation",
            "priority": "low|medium|high"
        }
    ]
}"""},
                    {"role": "user", "content": f"Analyze the financial and time impact for this project data:\n\n{context}"}
                ]
            )
            return response['choices'][0]['message']['content']
        except openai.error.RateLimitError:
            raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded")
        except openai.error.APIError as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
            
    async def validate_time_estimates(self, tasks: List[Dict], historical_data: Optional[Dict] = None) -> Dict:
        """
        Validate time estimates for tasks using AI and historical data if available
        
        Args:
            tasks (List[Dict]): List of tasks with their estimates
            historical_data (Optional[Dict]): Historical project data for reference
            
        Returns:
            Dict: Contains validation results and suggestions
        """
        try:
            context = {
                "tasks": tasks,
                "historical_data": historical_data
            }
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a project estimation validator. Format your response as JSON with the following structure:
{
    "validated_tasks": [
        {
            "task_id": "original task id",
            "original_estimate": float,
            "suggested_estimate": float,
            "confidence": float (0-1),
            "adjustment_reason": "explanation"
        }
    ],
    "overall_assessment": {
        "estimation_quality": "good|needs_review|poor",
        "suggestions": ["list of suggestions"]
    }
}"""},
                    {"role": "user", "content": f"Validate these time estimates based on the provided context:\n\n{context}"}
                ]
            )
            return response['choices'][0]['message']['content']
        except openai.error.RateLimitError:
            raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded")
        except openai.error.APIError as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
