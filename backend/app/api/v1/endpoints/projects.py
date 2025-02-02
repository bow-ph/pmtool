from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
import os
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


@router.post("/{project_id}/upload-pdf")
async def upload_pdf(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    # Verify project belongs to user
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
        
    # Verify file content is actually a PDF
    content = await file.read()
    if not content.startswith(b'%PDF-'):
        raise HTTPException(status_code=400, detail="Invalid file type. File content is not a valid PDF.")
    
    upload_dir = "/var/docuplanai/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    os.chmod(upload_dir, 0o755)  # Ensure directory is readable and executable
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    content = await file.read()
    if not content.startswith(b'%PDF-'):
        raise HTTPException(status_code=400, detail="Invalid file type. File content is not a valid PDF.")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "filename": file.filename,
        "stored_filename": filename,
        "upload_time": datetime.now().isoformat(),
        "file_url": f"/uploads/{filename}"
    }

@router.get("/{project_id}/uploaded-pdfs")
async def get_uploaded_pdfs(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict]:
    upload_dir = "/var/docuplanai/uploads"
    if not os.path.exists(upload_dir):
        return []
    
    files = []
    for filename in os.listdir(upload_dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(upload_dir, filename)
            stat = os.stat(file_path)
            # Handle filenames with or without timestamp prefix
            display_name = filename.split('_', 1)[1] if '_' in filename else filename
            files.append({
                "filename": display_name,
                "stored_filename": filename,
                "upload_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "file_url": f"/uploads/{filename}"
            })
    
    return sorted(files, key=lambda x: x["upload_time"], reverse=True)

class PDFAnalysisRequest(BaseModel):
    file_path: str | None = None
    content: str | None = None

@router.post("/{project_id}/analyze-pdf/{stored_filename}")
async def analyze_pdf(
    project_id: int,
    stored_filename: str,
    request: PDFAnalysisRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Handle file path directly since we're using stored_filename
    file_path = os.path.join("/var/docuplanai/uploads", stored_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"PDF file not found: {stored_filename}")
        
    pdf_service = PDFAnalysisService(db)
    try:
        print(f"Starting PDF analysis for file: {stored_filename}")
        result = await pdf_service.analyze_pdf(project_id, file_path)
        task_count = len(result.get('tasks', [])) if result else 0
        print(f"Analysis completed successfully: {task_count} tasks found")
        if task_count == 0:
            print("Warning: No tasks were generated from the analysis")
        return result
    except Exception as e:
        print(f"Error during PDF analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during PDF analysis: {str(e)}")

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

