from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TaskBase(BaseModel):
    description: str
    estimated_hours: float
    actual_hours: Optional[float] = None
    status: str = "pending"  # pending, in_progress, completed
    project_id: Optional[int] = None
    priority: Optional[str] = None  # high, medium, low
    confidence_score: Optional[float] = None  # AI confidence in the estimate (0-1)
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
