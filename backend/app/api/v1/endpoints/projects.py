from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.project import Project
from app.models.user import User
from app.services.pdf_analysis_service import PDFAnalysisService
from app.services.estimation_service import EstimationService

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

router = APIRouter()

@router.post("", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Create a new project"""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description
    )


@router.post("/{project_id}/analyze-pdf")
async def analyze_pdf(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Analyze a PDF file and extract tasks

    
    Args:
        project_id: ID of the project
        file: PDF file to analyze
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Dict containing analysis results
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Verify project belongs to user
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

        
    pdf_service = PDFAnalysisService(db)
    result = await pdf_service.analyze_pdf(project_id, file)
    return result

@router.get("/")
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[ProjectResponse]:
    """List all projects for the current user"""
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    return [
        ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description
        ) for project in projects
    ]

@router.get("/{project_id}/proactive-hints")
async def get_proactive_hints(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get proactive hints for a project"""
    # Verify project belongs to user
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    estimation_service = EstimationService(db)
    hints = await estimation_service.generate_proactive_hints(project_id)
    return hints

