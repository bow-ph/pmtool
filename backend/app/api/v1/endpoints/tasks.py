from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.crud.task import task

router = APIRouter()

@router.get("/", response_model=List[Task])
def read_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve tasks.
    """
    return task.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=Task)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: TaskCreate,
):
    """
    Create new task.
    """
    return task.create(db=db, obj_in=task_in)

@router.get("/{task_id}", response_model=Task)
def read_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
):
    """
    Get task by ID.
    """
    task_obj = task.get(db=db, id=task_id)
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_obj

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
    task_obj = task.get(db=db, id=task_id)
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.update(db=db, db_obj=task_obj, obj_in=task_in)

@router.delete("/{task_id}", response_model=Task)
def delete_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
):
    """
    Delete task.
    """
    task_obj = task.get(db=db, id=task_id)
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.remove(db=db, id=task_id)
