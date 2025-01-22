from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.base import get_db
from app.models.user import User
from app.services.caldav_service import CalDAVService
from app.core.auth import get_current_user

router = APIRouter()
caldav_service = CalDAVService()

@router.post("/calendars")
def create_calendar(
    calendar_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new calendar for the current user"""
    try:
        calendar_path = caldav_service.create_calendar(current_user.id, calendar_name)
        return {"calendar_path": calendar_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{calendar_path}")
def add_task(
    calendar_path: str,
    task_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a task to the calendar"""
    try:
        event_uid = caldav_service.add_task(calendar_path, task_data)
        return {"event_uid": event_uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/{calendar_path}/{event_uid}")
def update_task(
    calendar_path: str,
    event_uid: str,
    task_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task in the calendar"""
    if not caldav_service.update_task(calendar_path, event_uid, task_data):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "updated"}

@router.delete("/tasks/{calendar_path}/{event_uid}")
def delete_task(
    calendar_path: str,
    event_uid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task from the calendar"""
    if not caldav_service.delete_task(calendar_path, event_uid):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted"}

@router.get("/tasks/{calendar_path}")
def get_tasks(
    calendar_path: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks in a date range"""
    try:
        tasks = caldav_service.get_tasks(calendar_path, start_date, end_date)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
