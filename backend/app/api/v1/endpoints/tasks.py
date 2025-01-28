from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.crud.task import task

# Logging import
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[Task])
def read_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve tasks.
    """
    try:
        logger.info("Retrieving tasks with skip=%s, limit=%s", skip, limit)
        tasks = task.get_multi(db, skip=skip, limit=limit)
        return tasks
    except Exception as e:
        logger.error("Error retrieving tasks: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/", response_model=Task)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: TaskCreate,
):
    """
    Create new task.
    """
    try:
        logger.info("Creating task with data: %s", task_in.dict())
        return task.create(db=db, obj_in=task_in)
    except Exception as e:
        logger.error("Error creating task: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{task_id}", response_model=Task)
def read_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
):
    """
    Get task by ID.
    """
    try:
        logger.info("Retrieving task with ID: %s", task_id)
        task_obj = task.get(db=db, id=task_id)
        if not task_obj:
            logger.warning("Task with ID %s not found", task_id)
            raise HTTPException(status_code=404, detail="Task not found")
        return task_obj
    except Exception as e:
        logger.error("Error retrieving task with ID %s: %s", task_id, str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/{task_id}", response_model=Task)
def update_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    task_in: TaskUpdate,
):
    """
    Update task.
    """
    try:
        logger.info("Updating task with ID %s and data: %s", task_id, task_in.dict())
        task_obj = task.get(db=db, id=task_id)
        if not task_obj:
            logger.warning("Task with ID %s not found for update", task_id)
            raise HTTPException(status_code=404, detail="Task not found")
        return task.update(db=db, db_obj=task_obj, obj_in=task_in)
    except Exception as e:
        logger.error("Error updating task with ID %s: %s", task_id, str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/{task_id}", response_model=Task)
def delete_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
):
    """
    Delete task.
    """
    try:
        logger.info("Deleting task with ID: %s", task_id)
        task_obj = task.get(db=db, id=task_id)
        if not task_obj:
            logger.warning("Task with ID %s not found for deletion", task_id)
            raise HTTPException(status_code=404, detail="Task not found")
        return task.remove(db=db, id=task_id)
    except Exception as e:
        logger.error("Error deleting task with ID %s: %s", task_id, str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
