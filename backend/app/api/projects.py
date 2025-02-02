from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
import os
from datetime import datetime

from app.core.database import get_db
from app.services.pdf_analysis_service import PDFAnalysisService
from app.services.estimation_service import EstimationService
from app.services.caldav_service import CalDAVService
from app.schemas.task import Task, TaskCreate

router = APIRouter(prefix="/projects", tags=["projects"])
caldav_service = CalDAVService()

@router.post("/{project_id}/upload-pdf")
async def upload_pdf(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """Store PDF file and return file info"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    upload_dir = "/var/docuplanai/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
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
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Get list of uploaded PDFs for a project"""
    upload_dir = "/var/docuplanai/uploads"
    if not os.path.exists(upload_dir):
        return []
    
    files = []
    for filename in os.listdir(upload_dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(upload_dir, filename)
            stat = os.stat(file_path)
            files.append({
                "filename": filename.split('_', 1)[1],  # Remove timestamp prefix
                "stored_filename": filename,
                "upload_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "file_url": f"/uploads/{filename}"
            })
    
    return sorted(files, key=lambda x: x["upload_time"], reverse=True)

@router.post("/{project_id}/analyze-pdf")
async def analyze_pdf(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Analyze a PDF file to extract tasks and time estimates
    
    Args:
        project_id: ID of the project
        file: PDF file to analyze
        db: Database session
        
    Returns:
        dict: Analysis results including tasks and estimates
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
        
    pdf_service = PDFAnalysisService(db)
    result = await pdf_service.analyze_pdf(project_id, file)
    return result

@router.get("/{project_id}/proactive-hints")
async def get_proactive_hints(
    project_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get proactive hints about financial and time impact for a project
    
    Args:
        project_id: ID of the project
        db: Database session
        
    Returns:
        dict: Analysis results including financial impact and recommendations
    """
    try:
        estimation_service = EstimationService(db)
        result = await estimation_service.generate_proactive_hints(project_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating proactive hints: {str(e)}")

@router.post("/{project_id}/tasks", response_model=List[Task])
async def create_tasks(
    project_id: int,
    tasks: List[TaskCreate],
    db: Session = Depends(get_db)
) -> List[Task]:
    """Create tasks from PDF analysis and sync with CalDAV"""
    try:
        # Create calendar if it doesn't exist
        calendar_path = await caldav_service.create_calendar(project_id)
        
        created_tasks = []
        for task_data in tasks:
            # Add task to CalDAV calendar
            task_dict = task_data.model_dump()
            task_dict["project_id"] = project_id
            
            # Create task in CalDAV with retry mechanism
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    await caldav_service.add_task(task_dict, calendar_path)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    continue
            
            # Add to response
            created_tasks.append(Task(**task_dict))
        
        return created_tasks
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create tasks: {str(e)}"
        )
