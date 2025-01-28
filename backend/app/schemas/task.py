from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TaskBase(BaseModel):
    description: str
    estimated_hours: float
    actual_hours: Optional[float] = 0.0  # Standardwert: 0.0
    status: str = "pending"  # pending, in_progress, completed
    project_id: Optional[int] = None
    priority: Optional[str] = "medium"  # Standardwert: medium
    confidence_score: Optional[float] = 0.0  # Standardwert: 0.0
    confidence_rationale: Optional[str] = None  # Detailed explanation of confidence score
    
    

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    description: Optional[str] = None
    estimated_hours: Optional[float] = None

class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
