from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.hint_confirmation import HintConfirmation
from typing import Dict

router = APIRouter()

@router.post("/{project_id}/confirm_hint")
async def confirm_hint(
    project_id: int,
    hint_data: Dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    confirmation = HintConfirmation(
        project_id=project_id,
        hint_message=hint_data.get("message", ""),
        confirmed_by=current_user.id
    )
    db.add(confirmation)
    db.commit()
        
    return {"status": "success", "message": "Hint confirmed"}
