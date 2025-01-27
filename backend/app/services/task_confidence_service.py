from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.task import Task
import logging

logger = logging.getLogger(__name__)

class TaskConfidenceService:
    """Service for handling task confidence scoring and analysis"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def calculate_confidence_score(self, task_data: Dict) -> float:
        """Calculate confidence score based on task attributes"""
        base_score = 1.0
        factors = []
        
        # Check description clarity
        description = task_data.get("description", "")
        if len(description.split()) < 5:
            factors.append(0.7)  # Penalize very short descriptions
        elif len(description.split()) > 50:
            factors.append(0.9)  # Slightly penalize very long descriptions
        else:
            factors.append(1.0)
            
        # Check time estimate
        estimated_hours = task_data.get("estimated_hours", 0)
        if estimated_hours <= 0:
            factors.append(0.5)  # Invalid time estimate
        elif estimated_hours > 40:
            factors.append(0.8)  # Long tasks have more uncertainty
        else:
            factors.append(1.0)
            
        # Check dependencies
        dependencies = task_data.get("dependencies", [])
        if dependencies:
            factors.append(0.9)  # Tasks with dependencies have slightly lower confidence
            
        # Check technical requirements
        tech_reqs = task_data.get("technical_requirements", [])
        if tech_reqs:
            factors.append(0.95)  # Technical requirements add slight uncertainty
            
        # Check if task requires client input
        if task_data.get("requires_client_input", False):
            factors.append(0.85)  # Client input adds uncertainty
            
        # Calculate final score
        for factor in factors:
            base_score *= factor
            
        return round(max(min(base_score, 1.0), 0.0), 2)
        
    def analyze_task_confidence(self, task_data: Dict) -> Dict:
        """Analyze task confidence and provide detailed rationale"""
        confidence_score = self.calculate_confidence_score(task_data)
        
        # Generate confidence rationale
        rationale_points = []
        
        # Description analysis
        description = task_data.get("description", "")
        words = len(description.split())
        if words < 5:
            rationale_points.append("Task description is too brief")
        elif words > 50:
            rationale_points.append("Task description is very detailed but may include unnecessary complexity")
        else:
            rationale_points.append("Task description is clear and concise")
            
        # Time estimate analysis
        hours = task_data.get("estimated_hours", 0)
        if hours <= 0:
            rationale_points.append("Invalid time estimate")
        elif hours > 40:
            rationale_points.append("Long duration increases uncertainty")
        else:
            rationale_points.append(f"Time estimate of {hours} hours is reasonable")
            
        # Dependencies analysis
        deps = task_data.get("dependencies", [])
        if deps:
            rationale_points.append(f"Task has {len(deps)} dependencies which may affect timeline")
            
        # Technical requirements analysis
        tech_reqs = task_data.get("technical_requirements", [])
        if tech_reqs:
            rationale_points.append(f"Task involves {len(tech_reqs)} technical requirements")
            
        # Client input analysis
        if task_data.get("requires_client_input", False):
            rationale_points.append("Task requires client input which may cause delays")
            
        return {
            "confidence_score": confidence_score,
            "confidence_rationale": ". ".join(rationale_points),
            "risk_factors": self._identify_risk_factors(task_data),
            "improvement_suggestions": self._generate_suggestions(task_data)
        }
        
    def _identify_risk_factors(self, task_data: Dict) -> List[str]:
        """Identify potential risk factors for the task"""
        risks = []
        
        if task_data.get("requires_client_input", False):
            risks.append("Client input dependency")
            
        if task_data.get("dependencies", []):
            risks.append("Task dependencies may cause delays")
            
        if task_data.get("estimated_hours", 0) > 40:
            risks.append("Long duration increases complexity and uncertainty")
            
        if task_data.get("technical_requirements", []):
            risks.append("Technical requirements may require specific expertise")
            
        if task_data.get("complexity", "") == "high":
            risks.append("High task complexity")
            
        return risks
        
    def _generate_suggestions(self, task_data: Dict) -> List[str]:
        """Generate suggestions for improving task confidence"""
        suggestions = []
        
        # Description-based suggestions
        description = task_data.get("description", "")
        if len(description.split()) < 5:
            suggestions.append("Add more detail to task description")
        elif len(description.split()) > 50:
            suggestions.append("Consider breaking down into smaller tasks")
            
        # Time estimate suggestions
        hours = task_data.get("estimated_hours", 0)
        if hours > 40:
            suggestions.append("Break down into smaller tasks")
        elif hours <= 0:
            suggestions.append("Provide realistic time estimate")
            
        # Dependency suggestions
        if task_data.get("dependencies", []):
            suggestions.append("Review dependencies for potential optimization")
            
        # Client input suggestions
        if task_data.get("requires_client_input", False):
            suggestions.append("Plan for client communication early")
            
        return suggestions
