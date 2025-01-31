from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def get_by_project(self, db: Session, *, project_id: int) -> List[Task]:
        return db.query(Task).filter(Task.project_id == project_id).all()

    def get_by_status(self, db: Session, *, status: str) -> List[Task]:
        return db.query(Task).filter(Task.status == status).all()

    def get_by_priority(self, db: Session, *, priority: str) -> List[Task]:
        return db.query(Task).filter(Task.priority == priority).all()

    def update_status(
        self, db: Session, *, task_id: int, status: str
    ) -> Optional[Task]:
        task_obj = self.get(db=db, id=task_id)
        if not task_obj:
            return None
        task_obj.status = status
        db.add(task_obj)
        db.commit()
        db.refresh(task_obj)
        return task_obj

    def update_hours(
        self, db: Session, *, task_id: int, actual_hours: float
    ) -> Optional[Task]:
        task_obj = self.get(db=db, id=task_id)
        if not task_obj:
            return None
        task_obj.actual_hours = actual_hours
        db.add(task_obj)
        db.commit()
        db.refresh(task_obj)
        return task_obj

task = CRUDTask(Task)
