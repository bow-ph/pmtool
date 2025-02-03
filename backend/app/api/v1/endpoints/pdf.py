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

@router.post("/upload", response_model=dict)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploadet eine PDF-Datei mit Fortschrittsanzeige durch Chunks und speichert sie sicher ab"""
    
    # Verzeichnis für Uploads sicherstellen
    upload_dir = "/var/www/docuplanai/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    os.chmod(upload_dir, 0o755)  # Stellt sicher, dass der Ordner zugänglich ist

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)

    chunk_size = 8192  # 8KB Chunks für Fortschrittsanzeige

    try:
        # Datei in Chunks schreiben, um RAM-Verbrauch zu reduzieren
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)  # Datei wird in Blöcken gespeichert
        
        return {
            "status": "success",
            "filename": file.filename,
            "stored_filename": filename,
            "upload_time": datetime.now().isoformat(),
            "file_url": f"/uploads/{filename}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Datei: {str(e)}")

@router.post("/analyze/{project_id}", response_model=dict)
async def analyze_pdf(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analysiert eine hochgeladene PDF-Datei und erstellt Tasks"""
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Keine Datei bereitgestellt")
        
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Nur PDF-Dateien sind erlaubt.")
    
    try:
        # Datei in Chunks lesen
        content = bytearray()
        chunk_size = 8192  # 8KB
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            content.extend(chunk)
        
        if not content:
            raise HTTPException(status_code=400, detail="Leere Datei empfangen")
        
        # Datei für erneute Verarbeitung zurücksetzen
        await file.seek(0)
        
        pdf_service = PDFAnalysisService(db)
        pdf_url = await pdf_service.store_pdf(file, current_user.id)
        analysis_result = await pdf_service.analyze_pdf(project_id, file)
        
        return {
            "status": "success",
            "pdf_url": pdf_url,
            "tasks": analysis_result.get("tasks", []),
            "hints": analysis_result.get("hints", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei der Analyse: {str(e)}")

@router.get("/get/{user_id}/{filename}")
async def get_pdf(
    user_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lädt eine gespeicherte PDF-Datei herunter"""
    pdf_service = PDFAnalysisService(db)
    pdf_path = await pdf_service.get_pdf_path(f"{user_id}/{filename}", current_user.id)
    return FileResponse(pdf_path, media_type="application/pdf")
