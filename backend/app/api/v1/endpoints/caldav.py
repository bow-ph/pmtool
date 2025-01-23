from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import re
import uuid

from app.core.database import get_db
from app.models.user import User
from app.core.auth import get_current_user
from app.core.config import settings

# Pydantic models for request/response
class TaskData(BaseModel):
    description: str
    start_date: datetime
    end_date: datetime
    estimated_hours: float

class CalendarResponse(BaseModel):
    calendar_path: str
    caldav_url: str

class TaskResponse(BaseModel):
    event_uid: str
    caldav_url: str

def validate_calendar_path(path: str) -> bool:
    """Validate calendar path format (user_id/calendar_name)"""
    pattern = r'^\d+/[^/]+$'
    return bool(re.match(pattern, path))

router = APIRouter()

@router.post("/calendars", response_model=CalendarResponse)
def create_calendar(
    calendar_name: str = Path(..., description="Name of the calendar to create"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mock implementation for calendar creation during development"""
    calendar_path = f"{current_user.id}/{calendar_name}"
    caldav_url = f"{settings.CALDAV_SERVER_URL}/{calendar_path}"
    return CalendarResponse(calendar_path=calendar_path, caldav_url=caldav_url)

@router.post("/tasks/{calendar_path}", response_model=TaskResponse)
def add_task(
    task_data: TaskData,
    calendar_path: str = Path(..., description="Calendar path in format: user_id/calendar_name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mock implementation for task creation during development"""
    if not validate_calendar_path(calendar_path):
        raise HTTPException(
            status_code=400,
            detail="Invalid calendar path. Must be in format: user_id/calendar_name"
        )
    
    event_uid = str(uuid.uuid4())
    caldav_url = f"{settings.CALDAV_SERVER_URL}/{calendar_path}"
    return TaskResponse(event_uid=event_uid, caldav_url=caldav_url)

@router.put("/tasks/{calendar_path}/{event_uid}", response_model=TaskResponse)
def update_task(
    task_data: TaskData,
    calendar_path: str = Path(..., description="Calendar path in format: user_id/calendar_name"),
    event_uid: str = Path(..., description="Unique identifier of the event to update"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mock implementation for task update during development"""
    if not validate_calendar_path(calendar_path):
        raise HTTPException(
            status_code=400,
            detail="Invalid calendar path. Must be in format: user_id/calendar_name"
        )
        
    caldav_url = f"{settings.CALDAV_SERVER_URL}/{calendar_path}"
    return TaskResponse(event_uid=event_uid, caldav_url=caldav_url)

class TaskList(BaseModel):
    tasks: List[TaskData]
    caldav_url: str

class DeleteResponse(BaseModel):
    status: str
    caldav_url: str

@router.delete("/tasks/{calendar_path}/{event_uid}", response_model=DeleteResponse)
def delete_task(
    calendar_path: str = Path(..., description="Calendar path in format: user_id/calendar_name"),
    event_uid: str = Path(..., description="Unique identifier of the event to delete"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mock implementation for task deletion during development"""
    if not validate_calendar_path(calendar_path):
        raise HTTPException(
            status_code=400,
            detail="Invalid calendar path. Must be in format: user_id/calendar_name"
        )
        
    caldav_url = f"{settings.CALDAV_SERVER_URL}/{calendar_path}"
    return DeleteResponse(status="deleted", caldav_url=caldav_url)

@router.get("/tasks/{calendar_path}", response_model=TaskList)
def get_tasks(
    calendar_path: str = Path(..., description="Calendar path in format: user_id/calendar_name"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mock implementation for task listing during development"""
    if not validate_calendar_path(calendar_path):
        raise HTTPException(
            status_code=400,
            detail="Invalid calendar path. Must be in format: user_id/calendar_name"
        )
    
    caldav_url = f"{settings.CALDAV_SERVER_URL}/{calendar_path}"
    return TaskList(tasks=[], caldav_url=caldav_url)
