from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import aiofiles
import tempfile
import os
from app.core.database import get_db
from app.services.openai_service import OpenAIService
from app.services.pdf_analysis_service import PDFAnalysisService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{project_id}/analyze-pdf")
async def analyze_pdf(
    request: Request,
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Analyze PDF file using OpenAI integration"""
    try:
        logger.debug(f"Initializing PDF analysis for project {project_id}")
        logger.debug(f"Received file: {file.filename}")
        
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # Initialize services
            openai_service = OpenAIService()
            pdf_service = PDFAnalysisService(db)
            
            # Process the PDF
            logger.debug("Starting PDF analysis")
            analysis_result = await pdf_service.analyze_pdf(project_id, temp_path)
            logger.debug("PDF analysis completed successfully")
            
            return JSONResponse(
                content={
                    "status": "success",
                    "project_id": project_id,
                    "analysis": analysis_result
                }
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except HTTPException as e:
        logger.error(f"HTTP error during PDF analysis: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Error during PDF analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
