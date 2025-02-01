from typing import Dict, List
import pdfplumber
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.services.openai_service import OpenAIService
from app.models.task import Task
from sqlalchemy.orm import Session
import json
import tempfile
import os
from datetime import datetime

class PDFAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_service = OpenAIService()
        self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "pdfs")
        os.makedirs(self.upload_dir, exist_ok=True)

    async def store_pdf(self, file: UploadFile, user_id: int) -> str:
        """Store uploaded PDF and return its URL"""
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")

        try:
            content = await file.read()
            if not content.startswith(b'%PDF-'):
                raise HTTPException(status_code=400, detail="Invalid file type. File content is not a valid PDF.")

            # Create user-specific directory
            user_dir = os.path.join(self.upload_dir, str(user_id))
            os.makedirs(user_dir, exist_ok=True)

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = "".join(c for c in file.filename if c.isalnum() or c in ('-', '_')).lower()
            pdf_filename = f"{timestamp}_{safe_filename}"
            pdf_path = os.path.join(user_dir, pdf_filename)

            # Save the file
            with open(pdf_path, "wb") as f:
                f.write(content)

            return f"/api/v1/pdf/get/{user_id}/{pdf_filename}"

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing PDF: {str(e)}")

    async def get_pdf_path(self, pdf_id: str, user_id: int) -> str:
        """Get the full path of a stored PDF file"""
        try:
            user_id_str, filename = pdf_id.split("/", 1)
            if int(user_id_str) != user_id:
                raise HTTPException(status_code=403, detail="Access denied")

            pdf_path = os.path.join(self.upload_dir, str(user_id), filename)
            if not os.path.exists(pdf_path):
                raise HTTPException(status_code=404, detail="PDF not found")

            return pdf_path

        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid PDF ID format")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving PDF: {str(e)}")
        
    def _clean_text(self, text: str) -> str:
        """Remove common headers, footers, and clean up text"""
        # Split into lines
        lines = text.split('\n')
        
        # Remove empty lines and common headers/footers
        cleaned_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip if marked from previous iteration
            if skip_next:
                skip_next = False
                continue
                
            # Skip empty lines
            if not line:
                continue
                
            # Skip common headers/footers
            if any([
                line.isdigit(),  # Page numbers
                line.startswith(('Page ', 'Seite ')),  # Page headers
                line.startswith(('Tel:', 'Email:', 'www.')),  # Contact info
                line.lower().startswith(('datum:', 'date:')),  # Date headers
                line.startswith(('€', '$', '£')),  # Currency symbols at start
                line.endswith(('€', '$', '£')),  # Currency symbols at end
                'copyright' in line.lower(),  # Copyright notices
                'all rights reserved' in line.lower(),
                'confidential' in line.lower()
            ]):
                continue
                
            # Skip address blocks (multiple lines with commas and postal codes)
            if i < len(lines) - 1:
                next_line = lines[i + 1].strip()
                if ((',' in line or ',' in next_line) and 
                    any(char.isdigit() for char in line + next_line)):
                    skip_next = True
                    continue
                    
            # Remove common document metadata
            line = line.replace('Confidential', '').replace('DRAFT', '')
            line = line.strip('_-=')  # Remove common separators
            
            if line:  # Only add non-empty lines after cleaning
                cleaned_lines.append(line)
            
        return ' '.join(cleaned_lines)

    async def extract_text_from_pdf(self, file: UploadFile) -> str:
        """Extract text content from uploaded PDF file"""
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")
            
        try:
            # Create a temporary file to store the uploaded PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                content = await file.read()
                
                # Additional PDF header validation
                if not content.startswith(b'%PDF-'):
                    raise HTTPException(status_code=400, detail="Invalid file type. File content is not a valid PDF.")
                    
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
        except HTTPException:
            raise
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
            if isinstance(response, str):
                analysis_result = json.loads(response)
            else:
                analysis_result = response
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error parsing OpenAI response")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing PDF: {str(e)}")

        # Create tasks from analysis
        created_tasks = await self._create_tasks_from_analysis(project_id, analysis_result)

        return {
            "status": "success",
            "document_analysis": analysis_result.get("document_analysis", {
                "type": "unknown",
                "context": "",
                "client_type": "unknown",
                "complexity_level": "medium",
                "clarity_score": 0.0
            }),
            "tasks": created_tasks,
            "hints": analysis_result.get("hints", []),
            "total_estimated_hours": analysis_result.get("total_estimated_hours", 0),
            "risk_factors": analysis_result.get("risk_factors", []),
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

    async def _create_tasks_from_analysis(self, project_id: int, analysis: Dict) -> List[Dict]:
        """Create task records from OpenAI analysis"""
        created_tasks = []
        tasks = analysis.get("tasks", [])
        
        if not tasks:
            raise HTTPException(status_code=400, detail="No tasks found in analysis")
        
        for task_data in tasks:
            if "description" not in task_data:
                raise HTTPException(status_code=400, detail="Task missing required description field")
            if "estimated_hours" not in task_data:
                raise HTTPException(status_code=400, detail="Task missing required estimated_hours field")
                
            estimated_hours = float(task_data["estimated_hours"])
            if estimated_hours <= 0:
                raise HTTPException(status_code=400, detail="estimated_hours must be greater than 0")
                
            description = self._clean_text(task_data["description"])
            if not description.strip():
                raise HTTPException(status_code=400, detail="Task description cannot be empty")
                
            task = Task(
                project_id=project_id,
                title=task_data.get("title", description[:50]),
                description=description,
                duration_hours=float(task_data.get("duration_hours", estimated_hours)),
                hourly_rate=float(task_data.get("hourly_rate", 0.0)),
                estimated_hours=estimated_hours,
                actual_hours=task_data.get("actual_hours", None),
                status="pending",
                priority=task_data.get("complexity", "medium").lower(),
                confidence_score=task_data.get("confidence", 0.0),
                confidence_rationale=task_data.get("confidence_rationale", "")
            )
            self.db.add(task)
            created_tasks.append({
                "title": task.title,
                "description": task.description,
                "duration_hours": task.duration_hours,
                "hourly_rate": task.hourly_rate,
                "estimated_hours": task.estimated_hours,
                "priority": task.priority,
                "confidence_score": task.confidence_score,
                "confidence_rationale": task.confidence_rationale
            })
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error saving tasks: {str(e)}")
            
        return created_tasks
