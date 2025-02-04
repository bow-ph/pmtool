from typing import Dict, List, Union
import PyPDF2
from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.services.openai_service import OpenAIService
from app.services.caldav_service import CalDAVService
from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from sqlalchemy.orm import Session
import json
import tempfile
import os
from datetime import datetime, timedelta
class PDFAnalysisService:
    def __init__(self, db: Session, test_mode: bool = False):
        self.db = db
        self.openai_service = OpenAIService(test_mode=test_mode)
        self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "pdfs")
        os.makedirs(self.upload_dir, exist_ok=True)

    async def store_pdf(self, file: UploadFile, user_id: int) -> str:
        """Store uploaded PDF and return its URL"""
        print(f"Storing PDF file: {file.filename}")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")

        try:
            # Read file content in chunks
            content = bytearray()
            chunk_size = 8192  # 8KB chunks
            
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                content.extend(chunk)
            
            print(f"Read {len(content)} bytes from file")
            
            if not content:
                raise HTTPException(status_code=400, detail="Empty file received")
                
            if not content.startswith(b'%PDF-'):
                raise HTTPException(status_code=400, detail="Invalid file type. File content is not a valid PDF.")

            # Create user-specific directory
            user_dir = os.path.join(self.upload_dir, str(user_id))
            os.makedirs(user_dir, exist_ok=True)
            print(f"Created/verified user directory: {user_dir}")

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = "".join(c for c in file.filename if c.isalnum() or c in ('-', '_')).lower()
            pdf_filename = f"{timestamp}_{safe_filename}"
            pdf_path = os.path.join(user_dir, pdf_filename)

            # Save the file
            with open(pdf_path, "wb") as f:
                f.write(content)
            print(f"Saved PDF to: {pdf_path}")

            # Reset file position for subsequent operations
            await file.seek(0)
            
            return f"/api/v1/pdf/get/{user_id}/{pdf_filename}"

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing PDF: {str(e)}")

    async def get_project_pdfs(self, project_id: int, user_id: int) -> list:
        """Get list of PDFs uploaded for a project"""
        try:
            user_dir = os.path.join(self.upload_dir, str(user_id))
            if not os.path.exists(user_dir):
                return []

            files = []
            for filename in os.listdir(user_dir):
                if filename.lower().endswith('.pdf'):
                    files.append({
                        "filename": filename,
                        "url": f"/api/v1/pdf/get/{user_id}/{filename}",
                        "uploaded_at": datetime.fromtimestamp(os.path.getctime(os.path.join(user_dir, filename))).isoformat()
                    })
            return sorted(files, key=lambda x: x["uploaded_at"], reverse=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing PDFs: {str(e)}")

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

    async def extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text content from PDF bytes"""
        if not content.startswith(b'%PDF'):
            raise HTTPException(status_code=400, detail="Invalid PDF format")

        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=True)
            temp_file.write(content)
            temp_file.flush()
            
            try:
                import pdfplumber
                with pdfplumber.open(temp_file.name) as pdf:
                    if len(pdf.pages) == 0:
                        raise HTTPException(status_code=400, detail="PDF file contains no pages")
                    
                    text_parts = []
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    
                    if not text_parts:
                        raise HTTPException(status_code=400, detail="No text content found in PDF")
                    
                    return self._clean_text("\n".join(text_parts))
            except Exception as e:
                print(f"PDF extraction error: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error extracting text from PDF: {str(e)}")
            finally:
                if temp_file:
                    temp_file.close()
                if temp_file and os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                    print(f"Cleaned up temporary file: {temp_file.name}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

    async def analyze_pdf(self, project_id: int, content: bytes) -> Dict:
        """Analyze PDF content and create tasks with time estimates"""
        try:
            print(f"Starting PDF analysis for project {project_id}")
            print(f"Content size: {len(content)} bytes")
            print(f"Content starts with: {content[:20].hex()}")
            
            if not content or not content.startswith(b'%PDF'):
                print("Error: Invalid PDF format detected")
                raise HTTPException(status_code=400, detail="Invalid PDF file format")

            pdf_text = await self.extract_text_from_pdf(content)
            if not pdf_text:
                raise HTTPException(status_code=400, detail="No text content found in PDF")

            # Analyze text with OpenAI
            max_retries = 5
            last_error = None
            analysis_result = None
            
            for attempt in range(max_retries):
                try:
                    response_str = await self.openai_service.analyze_pdf_text(pdf_text)
                    analysis_result = response_str if isinstance(response_str, dict) else json.loads(response_str)
                    if "tasks" in analysis_result and analysis_result["tasks"]:
                        break
                except json.JSONDecodeError as e:
                    last_error = f"Error parsing OpenAI response: {str(e)}"
                except Exception as e:
                    last_error = f"Error analyzing PDF: {str(e)}"
                
                if attempt == max_retries - 1 and last_error:
                    raise HTTPException(status_code=500, detail=last_error)
            
            # Create tasks from analysis
            if not analysis_result:
                raise HTTPException(status_code=500, detail="Failed to analyze PDF content")
                
            tasks = await self._create_tasks_from_analysis(project_id, analysis_result)
            
            return {
                "status": "success",
                "tasks": tasks,
                "document_analysis": {
                    "type": "project_proposal",
                    "context": "Project task planning",
                    "client_type": "business",
                    "complexity_level": "medium",
                    "clarity_score": 0.8
                },
                "hints": analysis_result.get("hints", []),
                "confidence_analysis": (analysis_result or {}).get("confidence_analysis", {
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
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

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
                
            # Parse planned timeframe if available
            planned_timeframe = task_data.get("planned_timeframe", "")
            start_date = datetime.now()
            end_date = start_date + timedelta(hours=float(task_data.get("duration_hours", estimated_hours)))
            
            if planned_timeframe:
                try:
                    start_str, end_str = planned_timeframe.split(" - ")
                    start_date = datetime.strptime(start_str, "%Y-%m-%d")
                    end_date = datetime.strptime(end_str, "%Y-%m-%d")
                except Exception:
                    print(f"Warning: Could not parse planned_timeframe '{planned_timeframe}', using default")

            # Create task with required fields
            # Handle numeric fields with safe defaults
            try:
                duration_hours = float(task_data.get("duration_hours") or task_data.get("estimated_hours") or 1.0)
                hourly_rate = float(task_data.get("hourly_rate") or 920.0)
                estimated_hours = float(task_data.get("estimated_hours") or duration_hours)
                confidence_score = float(task_data.get("confidence") or 0.8)
            except (TypeError, ValueError):
                duration_hours = 1.0
                hourly_rate = 920.0
                estimated_hours = 1.0
                confidence_score = 0.8

            task = Task(
                project_id=project_id,
                title=task_data.get("title") or description.split('\n')[0][:100],
                description=description,
                duration_hours=duration_hours,
                hourly_rate=hourly_rate,
                estimated_hours=estimated_hours,
                actual_hours=None,
                status="pending",
                priority=task_data.get("complexity", "medium").lower(),
                confidence_score=confidence_score,
                confidence_rationale=task_data.get("confidence_rationale") or ""
            )
            
            # Add to session and get ID
            self.db.add(task)
            self.db.flush()

            # Get project user ID for CalDAV sync
            project = self.db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Sync with CalDAV
            # First commit the task to ensure it exists in the database
            self.db.commit()

            # Then try to sync with CalDAV
            try:
                print(f"Starting CalDAV sync for task {task.id} in project {project_id}")
                caldav_service = CalDAVService()  # Service auto-initializes in __init__
                
                # Get user email for calendar path
                user = self.db.query(User).filter(User.id == project.user_id).first()
                if not user:
                    raise ValueError(f"User {project.user_id} not found")
                    
                calendar_path = f"{user.email}/calendar"
                print(f"Using calendar path: {calendar_path}")
                
                # Prepare task data for sync
                caldav_task_data = {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "start_date": datetime.now(),
                    "end_date": datetime.now() + timedelta(hours=task.duration_hours),
                    "estimated_hours": task.estimated_hours,
                    "duration_hours": task.duration_hours,
                    "hourly_rate": task.hourly_rate,
                    "status": task.status,
                    "priority": task.priority,
                    "confidence_score": task.confidence_score,
                    "confidence_rationale": task.confidence_rationale
                }
                
                # Try to sync with CalDAV but don't let failures affect task creation
                try:
                    event_uid = await caldav_service.sync_task_with_calendar(caldav_task_data, calendar_path)
                    if event_uid:
                        task.caldav_event_uid = event_uid
                        print(f"Successfully synced task {task.id} with CalDAV event {event_uid}")
                        self.db.commit()  # Commit the CalDAV UID update
                except Exception as caldav_error:
                    print(f"Warning: CalDAV sync failed but task was created: {str(caldav_error)}")
            except Exception as e:
                print(f"Warning: Failed to sync task with CalDAV: {str(e)}")
                # Continue without CalDAV sync - task is already saved

            # Get planned timeframe from task data
            planned_timeframe = task_data.get("planned_timeframe", "")
            if not planned_timeframe:
                start_date = datetime.now()
                end_date = start_date + timedelta(hours=float(task.duration_hours or task.estimated_hours))
                planned_timeframe = f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}"

            created_tasks.append({
                "title": task.title,
                "description": task.description,
                "duration_hours": task.duration_hours,
                "hourly_rate": task.hourly_rate,
                "estimated_hours": task.estimated_hours,
                "priority": task.priority,
                "complexity": task.priority,
                "confidence": task.confidence_score,
                "confidence_score": task.confidence_score,
                "confidence_rationale": task.confidence_rationale,
                "caldav_event_uid": task.caldav_event_uid,
                "status": task.status,
                "requires_client_input": False,
                "technical_requirements": [],
                "deliverables": [],
                "planned_timeframe": planned_timeframe
            })
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error saving tasks: {str(e)}")
            
        return created_tasks
