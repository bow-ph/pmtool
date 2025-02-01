from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.pdf_analysis_service import PDFAnalysisService
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pdf_service = PDFAnalysisService(db)
    pdf_url = await pdf_service.store_pdf(file, current_user.id)
    return {"pdf_url": pdf_url}

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
