from typing import Dict, List
import pdfplumber
from fastapi import UploadFile, HTTPException
from app.services.openai_service import OpenAIService
from app.models.task import Task
from sqlalchemy.orm import Session
import json
import tempfile
import os

class PDFAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_service = OpenAIService()
        
    def _clean_text(self, text: str) -> str:
        """Remove common headers, footers, and clean up text"""
        # Split into lines
        lines = text.split('\n')
        
        # Remove empty lines and common headers/footers
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
            # Skip common headers/footers (page numbers, dates, etc.)
            if line.isdigit() or line.startswith('Page ') or line.startswith('Seite '):
                continue
            cleaned_lines.append(line)
            
        return ' '.join(cleaned_lines)

    async def extract_text_from_pdf(self, file: UploadFile) -> str:
        """Extract text content from uploaded PDF file"""
        try:
            # Create a temporary file to store the uploaded PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file.flush()
                
                # Extract text using pdfplumber
                pdf_text = ""
                with pdfplumber.open(tmp_file.name) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            pdf_text += text + "\n"
                            
                # Clean up temporary file
                os.unlink(tmp_file.name)
                return pdf_text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

    async def analyze_pdf(self, project_id: int, file: UploadFile) -> Dict:
        """Analyze PDF and create tasks with time estimates"""
        # Extract text from PDF
        pdf_text = await self.extract_text_from_pdf(file)
        if not pdf_text:
            raise HTTPException(status_code=400, detail="No text content found in PDF")

        # Analyze text with OpenAI
        try:
            response = await self.openai_service.analyze_pdf_text(pdf_text)
            analysis_result = json.loads(response)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error parsing OpenAI response")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing PDF: {str(e)}")

        # Create tasks from analysis
        created_tasks = await self._create_tasks_from_analysis(project_id, analysis_result)

        return {
            "status": "success",
            "tasks": created_tasks,
            "total_estimated_hours": analysis_result.get("total_estimated_hours", 0),
            "risk_factors": analysis_result.get("risk_factors", []),
            "confidence_analysis": analysis_result.get("confidence_analysis", {
                "overall_confidence": 0.0,
                "rationale": "",
                "improvement_suggestions": []
            })
        }

    async def _create_tasks_from_analysis(self, project_id: int, analysis: Dict) -> List[Dict]:
        """Create task records from OpenAI analysis"""
        created_tasks = []
        tasks = analysis.get("tasks", [])
        
        for task_data in tasks:
            # Clean task description by removing common headers/footers
            description = self._clean_text(task_data["description"])
            task = Task(
                project_id=project_id,
                description=description,
                estimated_hours=task_data["estimated_hours"],
                status="pending",
                confidence_score=task_data.get("confidence", 0.0),
                confidence_rationale=task_data.get("confidence_rationale", "")
            )
            self.db.add(task)
            created_tasks.append({
                "description": task.description,
                "estimated_hours": task.estimated_hours,
                "confidence_score": task.confidence_score,
                "confidence_rationale": task.confidence_rationale
            })
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error saving tasks: {str(e)}")
            
        return created_tasks
