from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.core.auth import get_current_user
from app.services.caldav_service import CalDAVService

router = APIRouter()

@router.get("/list", response_model=dict)
async def get_todo_list(
    status: Optional[str] = Query(None, enum=['pending', 'in_progress', 'completed']),
    priority: Optional[str] = Query(None, enum=['high', 'medium', 'low']),
    project_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get filtered todo list for current user"""
    try:
        # Base query for user's tasks
        query = db.query(Task).join(Task.project).filter(
            Project.user_id == current_user.id
        )
        
        # Apply filters
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if start_date:
            query = query.filter(Task.created_at >= start_date)
        if end_date:
            query = query.filter(Task.created_at <= end_date)
            
        # Get tasks
        tasks = query.all()
        
        # Count by status
        pending = sum(1 for task in tasks if task.status == 'pending')
        in_progress = sum(1 for task in tasks if task.status == 'in_progress')
        completed = sum(1 for task in tasks if task.status == 'completed')
        
        return {
            "items": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "estimated_hours": task.estimated_hours,
                    "actual_hours": task.actual_hours,
                    "duration_hours": task.duration_hours,
                    "hourly_rate": task.hourly_rate,
                    "status": task.status,
                    "priority": task.priority,
                    "confidence_score": task.confidence_score,
                    "confidence_rationale": task.confidence_rationale,
                    "project_id": task.project_id,
                    "caldav_event_uid": task.caldav_event_uid,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
                for task in tasks
            ],
            "total_items": len(tasks),
            "pending_items": pending,
            "in_progress_items": in_progress,
            "completed_items": completed
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get todo list: {str(e)}"
        )

from pydantic import BaseModel

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[str] = None
    actual_hours: Optional[float] = None
    duration_hours: Optional[float] = None
    hourly_rate: Optional[float] = None
    project_id: Optional[int] = None

@router.post("/tasks", response_model=dict)
async def create_task(
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        task = Task(
            title=task_data.title,
            description=task_data.description,
            duration_hours=task_data.duration_hours,
            hourly_rate=task_data.hourly_rate,
            status="pending",
            priority=task_data.priority or "medium",
            project_id=task_data.project_id,
            confidence_score=1.0,
            confidence_rationale="Manually created task",
            estimated_hours=task_data.duration_hours or 0.0
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Sync with CalDAV
        try:
            caldav_service = CalDAVService()
            
            # Create calendar path using user's email as identifier
            user_id = current_user.email.split('@')[0].replace('.', '_')
            calendar_path = f"{user_id}/calendar"
            print(f"Using calendar path: {calendar_path}")
            
            # Create calendar if it doesn't exist
            caldav_service.create_calendar(user_id, "PM Tool Calendar")
            print(f"Ensured calendar exists at {calendar_path}")
            
            # Sync task with calendar
            event_uid = caldav_service.sync_task_with_calendar({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "estimated_hours": task.estimated_hours,
                "duration_hours": task.duration_hours,
                "hourly_rate": task.hourly_rate,
                "status": task.status,
                "priority": task.priority,
                "confidence_score": task.confidence_score,
                "confidence_rationale": task.confidence_rationale,
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(hours=float(task.duration_hours or task.estimated_hours))
            }, calendar_path)
            
            # Update task with calendar event UID
            task.caldav_event_uid = event_uid
            db.commit()
            
            return {
                "status": "success",
                "task": {
                    "id": task.id,
                    "caldav_event_uid": event_uid,
                    "title": task.title,
                    "description": task.description,
                    "duration_hours": task.duration_hours,
                    "hourly_rate": task.hourly_rate,
                    "status": task.status,
                    "priority": task.priority,
                    "confidence_score": task.confidence_score,
                    "confidence_rationale": task.confidence_rationale
                }
            }
        except Exception as caldav_error:
            print(f"CalDAV sync error: {str(caldav_error)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to sync task with calendar: {str(caldav_error)}"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create task: {str(e)}"
        )

@router.put("/tasks/{task_id}", response_model=dict)
async def update_todo_item(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a todo item and sync with calendar"""
    try:
        # Get task with project join for user verification
        task = db.query(Task).join(Task.project).filter(
            Task.id == task_id,
            Project.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        print(f"Updating task {task_id} for user {current_user.email}")
        
        # Store original values for rollback
        original_values = {
            "title": task.title,
            "description": task.description,
            "duration_hours": task.duration_hours,
            "hourly_rate": task.hourly_rate,
            "status": task.status,
            "priority": task.priority,
            "caldav_event_uid": task.caldav_event_uid
        }
        
        try:
            # Update task fields
            update_data = task_update.dict(exclude_unset=True)
            print(f"Updating fields: {update_data}")
            
            for field, value in update_data.items():
                setattr(task, field, value)
            
            # Commit database changes
            db.commit()
            db.refresh(task)
            print(f"Database update successful for task {task_id}")
            
            # Prepare calendar sync
            try:
                caldav_service = CalDAVService()
                user_id = current_user.email.split('@')[0].replace('.', '_')
                calendar_path = f"{user_id}/calendar"
                
                # Create calendar if it doesn't exist
                caldav_service.create_calendar(user_id, "PM Tool Calendar")
                print(f"Ensured calendar exists at {calendar_path}")
                
                # Sync with calendar
                event_uid = caldav_service.sync_task_with_calendar({
                    "id": task.id,
                    "title": task.title or original_values["title"],
                    "description": task.description,
                    "estimated_hours": task.estimated_hours,
                    "duration_hours": task.duration_hours,
                    "hourly_rate": task.hourly_rate,
                    "status": task.status,
                    "priority": task.priority,
                    "confidence_score": task.confidence_score,
                    "confidence_rationale": task.confidence_rationale,
                    "caldav_event_uid": task.caldav_event_uid,
                    "start_date": datetime.now(),
                    "end_date": datetime.now() + timedelta(hours=float(task.duration_hours or task.estimated_hours))
                }, calendar_path)
                
                print(f"Calendar sync successful with event_uid: {event_uid}")
                
                if not task.caldav_event_uid:
                    task.caldav_event_uid = event_uid
                    db.commit()
                
                return {
                    "status": "success",
                    "task": {
                        "id": task.id,
                        "caldav_event_uid": event_uid,
                        "title": task.title,
                        "description": task.description,
                        "duration_hours": task.duration_hours,
                        "hourly_rate": task.hourly_rate,
                        "status": task.status,
                        "priority": task.priority,
                        "confidence_score": task.confidence_score,
                        "confidence_rationale": task.confidence_rationale
                    }
                }
            except Exception as caldav_error:
                print(f"CalDAV sync error: {str(caldav_error)}")
                # Rollback database changes on calendar sync failure
                for field, value in original_values.items():
                    setattr(task, field, value)
                db.commit()
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to sync task with calendar: {str(caldav_error)}"
                )
        except Exception as update_error:
            print(f"Task update error: {str(update_error)}")
            # Rollback to original values
            for field, value in original_values.items():
                setattr(task, field, value)
            db.commit()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update task: {str(update_error)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/sync-status", response_model=dict)
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get CalDAV synchronization status for user's tasks"""
    try:
        caldav_service = CalDAVService()
        calendar_path = f"{current_user.email}/calendar"
        
        tasks = db.query(Task).join(Task.project).filter(
            Project.user_id == current_user.id
        ).all()
        
        synced_count = 0
        failed_count = 0
        failed_tasks = []
        
        try:
            events = caldav_service.get_tasks(calendar_path)
            event_map = {e.get("x-pm-tool-id"): e for e in events}
            
            for task in tasks:
                if str(task.id) in event_map:
                    event = event_map[str(task.id)]
                    if (task.caldav_event_uid == event.get("uid") and
                        task.title == event.get("x-pm-tool-title") and
                        str(task.duration_hours) == event.get("x-pm-tool-duration-hours") and
                        str(task.hourly_rate) == event.get("x-pm-tool-hourly-rate")):
                        synced_count += 1
                    else:
                        failed_count += 1
                        failed_tasks.append({
                            "id": task.id,
                            "title": task.title,
                            "reason": "Task data mismatch with calendar event"
                        })
                else:
                    failed_count += 1
                    failed_tasks.append({
                        "id": task.id,
                        "title": task.title,
                        "reason": "No matching calendar event found"
                    })
                    
            return {
                "status": "success",
                "total_tasks": len(tasks),
                "synced_tasks": synced_count,
                "failed_tasks": failed_count,
                "failed_task_details": failed_tasks,
                "last_sync": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error fetching calendar events: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to fetch calendar events: {str(e)}",
                "total_tasks": len(tasks),
                "synced_tasks": 0,
                "failed_tasks": len(tasks),
                "failed_task_details": [{"id": t.id, "title": t.title, "reason": "Calendar access error"} for t in tasks],
                "last_sync": datetime.utcnow().isoformat()
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync status: {str(e)}"
        )
