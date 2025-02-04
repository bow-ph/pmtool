from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.task import Task
from app.services.pdf_analysis_service import PDFAnalysisService
from app.services.caldav_service import CalDAVService
from fastapi.responses import FileResponse
from datetime import datetime
import os

router = APIRouter()

@router.post("/upload/{project_id}", response_model=dict)
async def upload_pdf(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pdf_service = PDFAnalysisService(db)
    pdf_url = await pdf_service.store_pdf(file, current_user.id)
    return {"status": "success", "pdf_url": pdf_url}

@router.post("/analyze/{project_id}", response_model=dict)
async def analyze_pdf(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Received PDF analysis request for project {project_id}")
    print(f"File info - Filename: {file.filename}, Content-Type: {file.content_type}")
    
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")
    
    try:
        # Read file content in chunks to handle large files
        content = bytearray()
        chunk_size = 8192  # 8KB chunks
        
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            content.extend(chunk)
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file received")
            
        print(f"Successfully read PDF file. Size: {len(content)} bytes")
        print(f"First 20 bytes: {content[:20].hex()}")
        
        # Reset file position for subsequent reads
        await file.seek(0)
        
        pdf_service = PDFAnalysisService(db)
        
        # Store and analyze PDF
        print("Storing PDF...")
        pdf_url = await pdf_service.store_pdf(file, current_user.id)
        print(f"PDF stored successfully at {pdf_url}")
        
        print("Starting PDF analysis...")
        analysis_result = await pdf_service.analyze_pdf(project_id, content)
        print(f"Analysis complete. Found {len(analysis_result.get('tasks', []))} tasks")
        
        # Create tasks and sync with CalDAV
        caldav_service = CalDAVService()
        await caldav_service.initialize()
        tasks = []
        
        for task_data in analysis_result.get("tasks", []):
            task = Task(
                title=task_data["title"],
                description=task_data["description"],
                duration_hours=float(task_data["duration_hours"]),
                hourly_rate=float(task_data["hourly_rate"]),
                status="pending",
                project_id=project_id,
                confidence_score=task_data.get("confidence", 0.9),
                confidence_rationale=task_data.get("confidence_rationale", "Generated from PDF analysis"),
                estimated_hours=float(task_data["duration_hours"])
            )
            db.add(task)
            db.commit()  # Commit to ensure task has an ID
            
            # Sync with CalDAV
            calendar_path = f"{current_user.id}/calendar"
            await caldav_service.create_calendar(current_user.id, "PM Tool Calendar")
            caldav_event_uid = await caldav_service.sync_task_with_calendar(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "duration_hours": task.duration_hours,
                    "hourly_rate": task.hourly_rate,
                    "status": task.status,
                    "confidence_score": task.confidence_score,
                    "confidence_rationale": task.confidence_rationale,
                    "start_date": datetime.now()
                },
                calendar_path
            )
            task.caldav_event_uid = caldav_event_uid
            db.add(task)  # Re-add task with caldav_event_uid
            tasks.append(task)
        
        db.commit()
        
        # Update response with task IDs and CalDAV event UIDs
        analysis_result["tasks"] = [
            {
                **task_data,
                "id": task.id,
                "caldav_event_uid": task.caldav_event_uid
            }
            for task_data, task in zip(analysis_result["tasks"], tasks)
        ]
        
        return {
            "status": "success",
            "pdf_url": pdf_url,
            "document_analysis": analysis_result.get("document_analysis", {}),
            "tasks": analysis_result["tasks"],
            "hints": analysis_result.get("hints", []),
            "confidence_analysis": analysis_result.get("confidence_analysis", {
                "overall_confidence": 0.0,
                "rationale": "",
                "improvement_suggestions": [],
                "accuracy_factors": {
                    "document_clarity": 0.0,
                    "technical_complexity": 0.0,
                    "dependency_risk": 0.0,
                    "client_input_risk": 0.0
                }
            })
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during PDF analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze PDF: {str(e)}"
        )

@router.get("/files/{project_id}", response_model=list)
async def get_uploaded_pdfs(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pdf_service = PDFAnalysisService(db)
    files = await pdf_service.get_project_pdfs(project_id, current_user.id)
    return files

@router.get("/get/{user_id}/{filename}")
async def get_pdf(
    user_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pdf_service = PDFAnalysisService(db)
    pdf_path = await pdf_service.get_pdf_path(f"{user_id}/{filename}", current_user.id)
    return FileResponse(pdf_path, media_type="application/pdf")
