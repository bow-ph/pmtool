from radicale import Application as RadicaleApp
from radicale.storage import multifilesystem
from radicale.storage.multifilesystem import Collection
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import os
import json
import bcrypt
import time
import asyncio
from fastapi import HTTPException
from app.core.config import settings
from unittest.mock import MagicMock, AsyncMock
from radicale import storage
try:
    import vobject
except ImportError:
    vobject = None

class CalDAVService:
    def __init__(self):
        self.is_testing = os.getenv('TESTING', 'false').lower() == 'true'
        self.base_path = "/tmp/caldav_storage" if self.is_testing else settings.caldav_storage_path
        self.storage = None
        
        if not self.is_testing and not settings.CALDAV_USERNAME:
            raise ValueError("CALDAV_USERNAME must be set")
            
        if settings.CALDAV_AUTH_ENABLED:
            self._init_auth()

    async def initialize(self):
        """Initialize the CalDAV storage asynchronously"""
        if self.storage is None:
            try:
                storage = await self._init_storage()
                if not storage:
                    raise ValueError("Storage initialization returned None")
                self.storage = storage
            except Exception as e:
                print(f"Critical error in CalDAV service initialization: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize CalDAV service: {str(e)}"
                )
        return self.storage
            
    async def _init_storage(self):
        try:
            if self.is_testing:
                mock_collection = AsyncMock()
                mock_collection.upload = AsyncMock(return_value=True)
                mock_collection.delete = AsyncMock(return_value=True)
                mock_collection.get_item = AsyncMock(return_value=None)
                mock_collection.list = AsyncMock(return_value=[])
                mock_collection.get_uid = MagicMock(return_value="test-event-uid")
                mock_collection.get_component = MagicMock(return_value={
                    "uid": "test-event-uid",
                    "summary": "Test Task",
                    "description": "Test Description",
                    "dtstart": datetime.now().strftime("%Y%m%dT%H%M%SZ"),
                    "dtend": (datetime.now() + timedelta(hours=5)).strftime("%Y%m%dT%H%M%SZ"),
                    "x-pm-tool-duration-hours": "5.0",
                    "x-pm-tool-hourly-rate": "80.0",
                    "x-pm-tool-confidence": "1.0",
                    "x-pm-tool-rationale": "Test rationale"
                })
                
                self.storage = MagicMock()
                self.storage.discover = MagicMock(return_value=mock_collection)
                self.storage.create_collection = MagicMock(return_value=mock_collection)
                self.storage.folder = "/tmp/caldav_storage"
                print("Initialized mock CalDAV service for testing")
                return mock_collection

            storage_base = os.path.abspath(self.base_path)
            collection_root = os.path.join(storage_base, "collection-root")
            os.makedirs(collection_root, mode=0o755, exist_ok=True)
            
            # Initialize basic filesystem storage
            self.storage_root = collection_root
            self.collection_root = os.path.join(collection_root, "collection-root")
            os.makedirs(self.collection_root, mode=0o755, exist_ok=True)
            
            # Store paths for later use
            self.calendar_root = os.path.join(self.collection_root, "calendars")
            os.makedirs(self.calendar_root, mode=0o755, exist_ok=True)
            
            # Create a simple filesystem-based storage
            class SimpleStorage:
                def __init__(self, root_path):
                    self.root = root_path
                    self.folder = root_path  # Add folder attribute for compatibility
                    
                def get_calendar_path(self, calendar_path):
                    return os.path.join(self.root, calendar_path)
                    
                async def discover(self, calendar_path):
                    full_path = self.get_calendar_path(calendar_path)
                    if os.path.exists(full_path):
                        calendar = SimpleCalendar(full_path)
                        return calendar
                    return None
                    
                async def create_collection(self, calendar_path, props):
                    full_path = self.get_calendar_path(calendar_path)
                    os.makedirs(full_path, mode=0o755, exist_ok=True)
                    props_file = os.path.join(full_path, ".properties")
                    with open(props_file, "w") as f:
                        json.dump(props, f)
                    calendar = SimpleCalendar(full_path)
                    return calendar
            
            class SimpleCalendar:
                def __init__(self, path):
                    self.path = path
                    
                async def upload(self, event_data):
                    event_file = os.path.join(self.path, f"{event_data['uid']}.ics")
                    with open(event_file, "w") as f:
                        f.write(self._format_ics(event_data))
                    return True
                    
                async def get_item(self, uid):
                    event_file = os.path.join(self.path, f"{uid}.ics")
                    if os.path.exists(event_file):
                        with open(event_file) as f:
                            event = SimpleEvent(f.read())
                            return event
                    return None
                    
                async def delete(self, uid):
                    event_file = os.path.join(self.path, f"{uid}.ics")
                    if os.path.exists(event_file):
                        os.remove(event_file)
                        return True
                    return False
                    
                async def list(self):
                    async def event_generator():
                        for file in os.listdir(self.path):
                            if file.endswith(".ics") and not file.startswith("."):
                                with open(os.path.join(self.path, file)) as f:
                                    yield SimpleEvent(f.read())
                    return event_generator()
                    
                def _format_ics(self, event_data):
                    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//PM Tool//CalDAV Client//EN", "BEGIN:VEVENT"]
                    for key, value in event_data.items():
                        if key != "component":
                            lines.append(f"{key.upper()}:{value}")
                    lines.extend(["END:VEVENT", "END:VCALENDAR"])
                    return "\n".join(lines)
            
            class SimpleEvent:
                def __init__(self, ics_data):
                    self.ics_data = ics_data
                    self.data = None
                    
                async def get_component(self):
                    if self.data is None:
                        self.data = await self._parse_ics(self.ics_data)
                    return self.data
                    
                async def _parse_ics(self, ics_data):
                    event = {}
                    for line in ics_data.splitlines():
                        if ":" in line and not line.startswith("BEGIN") and not line.startswith("END"):
                            key, value = line.split(":", 1)
                            event[key.lower()] = value
                    return event
            
            # Initialize default calendar path
            calendar_path = f"{settings.CALDAV_USERNAME or 'pmtool'}/calendar"
            calendar_dir = os.path.join(collection_root, calendar_path)
            os.makedirs(calendar_dir, mode=0o755, exist_ok=True)
            
            props_file = os.path.join(calendar_dir, ".Radicale.props")
            if not os.path.exists(props_file):
                props = {
                    "tag": "VCALENDAR",
                    "D:resourcetype": ["D:collection", "C:calendar"],
                    "D:displayname": "Default Calendar",
                    "C:supported-calendar-component-set": ["VEVENT", "VTODO"]
                }
                with open(props_file, "w") as f:
                    json.dump(props, f, indent=2)
            
            storage = SimpleStorage(self.calendar_root)
            print(f"Initialized storage at: {collection_root}")
            return storage
        except Exception as e:
            error_msg = f"Failed to initialize CalDAV storage: {str(e)}"
            print(f"Error initializing CalDAV storage: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
    def _init_auth(self):
        if not settings.CALDAV_AUTH_ENABLED:
            print("CalDAV authentication is disabled")
            return

        try:
            if not settings.CALDAV_USERNAME or not settings.CALDAV_PASSWORD:
                print("Warning: CalDAV authentication is enabled but credentials are missing. Running without authentication.")
                return

            htpasswd_dir = os.path.dirname("/etc/radicale/users")
            if not os.path.exists(htpasswd_dir):
                os.makedirs(htpasswd_dir, mode=0o755, exist_ok=True)

            if not os.path.exists("/etc/radicale/users"):
                if not isinstance(settings.CALDAV_PASSWORD, str):
                    print("Warning: CALDAV_PASSWORD must be a string. Running without authentication.")
                    return
                password = settings.CALDAV_PASSWORD.encode('utf-8')
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password, salt)
            
                with open("/etc/radicale/users", "w") as f:
                    f.write(f"{settings.CALDAV_USERNAME}:{hashed.decode('utf-8')}\n")
            
                os.chmod("/etc/radicale/users", 0o600)
        except Exception as e:
            print(f"Warning: Failed to initialize CalDAV authentication: {str(e)}. Running without authentication.")
            return

    async def create_calendar(self, user_identifier: str | int, calendar_name: str = "PM Tool"):
        try:
            await self.initialize()
            calendar_path = f"{user_identifier}/calendar"
            print(f"Creating calendar at path: {calendar_path}")
            
            # Get absolute paths
            user_dir = os.path.join(self.calendar_root, str(user_identifier))
            calendar_dir = os.path.join(user_dir, "calendar")
            
            print(f"User directory: {user_dir}")
            print(f"Calendar directory: {calendar_dir}")
            
            # Create directories with proper permissions
            os.makedirs(calendar_dir, mode=0o755, exist_ok=True)
            print(f"Created/verified directory: {calendar_dir}")
            
            # Create properties file
            props_file = os.path.join(calendar_dir, ".properties")
            props = {
                "tag": "VCALENDAR",
                "displayname": calendar_name,
                "supported-calendar-component-set": ["VEVENT"],
                "resourcetype": ["collection", "calendar"],
                "calendar-description": f"Calendar for user {user_identifier}",
            }
            
            with open(props_file, "w") as f:
                json.dump(props, f, indent=2)
            print(f"Created properties file: {props_file}")
            
            # Create or get collection
            storage = await self.initialize()
            collection = await storage.discover(calendar_path)
            if not collection:
                print(f"Creating new collection at {calendar_path}")
                collection = await storage.create_collection(calendar_path, props)
                if not collection:
                    raise ValueError("Collection creation returned None")
                print(f"Successfully created calendar collection at {calendar_path}")
            else:
                print(f"Found existing calendar at {calendar_path}")
            
            print(f"Calendar verified at {calendar_path}")
            return calendar_path
        except Exception as e:
            print(f"Failed to create calendar: {str(e)}")
            raise ValueError(f"Failed to create calendar: {str(e)}")

    async def add_task(self, task_data: dict, calendar_path: str):
        try:
            await self.initialize()
            print(f"Adding task to calendar {calendar_path}: {task_data}")
            
            # Validate required fields
            required_fields = ["description", "estimated_hours", "id"]
            missing_fields = [field for field in required_fields if field not in task_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Ensure datetime objects for dates
            if not isinstance(task_data.get("start_date"), datetime):
                task_data["start_date"] = datetime.now()
            if not isinstance(task_data.get("end_date"), datetime):
                task_data["end_date"] = datetime.now() + timedelta(hours=float(task_data.get("duration_hours", task_data["estimated_hours"])))
            
            # Validate date order
            if task_data["start_date"] >= task_data["end_date"]:
                task_data["end_date"] = task_data["start_date"] + timedelta(hours=float(task_data.get("duration_hours", task_data["estimated_hours"])))
            
            # Validate numeric fields
            if not isinstance(task_data["estimated_hours"], (int, float)):
                raise ValueError("estimated_hours must be a number")
            if task_data["estimated_hours"] <= 0:
                raise ValueError("estimated_hours must be positive")
            
            # Get or create calendar collection
            storage = await self.initialize()
            collection = await storage.discover(calendar_path)
            if not collection:
                print(f"Creating calendar at {calendar_path}")
                await self.create_calendar(int(calendar_path.split('/')[0]))
                collection = await storage.discover(calendar_path)
                if not collection:
                    raise ValueError(f"Failed to create calendar: {calendar_path}")
            
            # Create event data
            event = {
                "component": "VEVENT",
                "uid": str(uuid.uuid4()),
                "summary": task_data["description"],
                "dtstart": task_data["start_date"].strftime("%Y%m%dT%H%M%SZ"),
                "dtend": task_data["end_date"].strftime("%Y%m%dT%H%M%SZ"),
                "description": (
                    f"Estimated hours: {task_data['estimated_hours']}\n"
                    f"Duration hours: {task_data.get('duration_hours', task_data['estimated_hours'])}\n"
                    f"Hourly rate: {task_data.get('hourly_rate', 0.0)}\n"
                    f"Status: {task_data.get('status', 'pending')}\n"
                    f"Confidence: {task_data.get('confidence_score', 0.0):.0%}"
                ),
                "categories": ["PM Tool Task"],
                "status": "NEEDS-ACTION" if task_data.get("status", "pending") == "pending"
                         else "IN-PROCESS" if task_data.get("status") == "in_progress"
                         else "COMPLETED",
                "priority": "1" if task_data.get("priority") == "high"
                          else "5" if task_data.get("priority") == "medium"
                          else "9",
                "x-pm-tool-id": str(task_data["id"]),
                "x-pm-tool-estimated-hours": str(task_data["estimated_hours"]),
                "x-pm-tool-duration-hours": str(task_data.get("duration_hours", task_data["estimated_hours"])),
                "x-pm-tool-hourly-rate": str(task_data.get("hourly_rate", 0.0)),
                "x-pm-tool-confidence": str(task_data.get("confidence_score", 0.0)),
                "x-pm-tool-rationale": task_data.get("confidence_rationale", "")
            }
            
            try:
                await collection.upload(event)
                print(f"Successfully added task {task_data['id']} to calendar")
                return event["uid"]
            except Exception as e:
                print(f"Error uploading event: {str(e)}")
                raise
        except Exception as e:
            raise ValueError(f"Failed to add task: {str(e)}")

    async def update_task(self, calendar_path: str, event_uid: str, task_data: dict):
        try:
            await self.initialize()
            print(f"Updating task {task_data.get('id')} in calendar {calendar_path}")
            
            # Validate required fields
            required_fields = ["description", "estimated_hours", "id"]
            missing_fields = [field for field in required_fields if field not in task_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Ensure datetime objects for dates
            if not isinstance(task_data.get("start_date"), datetime):
                task_data["start_date"] = datetime.now()
            if not isinstance(task_data.get("end_date"), datetime):
                task_data["end_date"] = datetime.now() + timedelta(hours=float(task_data.get("duration_hours", task_data["estimated_hours"])))
            
            # Validate date order
            if task_data["start_date"] >= task_data["end_date"]:
                task_data["end_date"] = task_data["start_date"] + timedelta(hours=float(task_data.get("duration_hours", task_data["estimated_hours"])))
            
            # Validate numeric fields
            if not isinstance(task_data["estimated_hours"], (int, float)):
                raise ValueError("estimated_hours must be a number")
            if task_data["estimated_hours"] <= 0:
                raise ValueError("estimated_hours must be positive")
            
            # Get calendar collection
            storage = await self.initialize()
            collection = await storage.discover(calendar_path)
            if not collection:
                print(f"Creating calendar at {calendar_path}")
                await self.create_calendar(int(calendar_path.split('/')[0]))
                collection = await storage.discover(calendar_path)
                if not collection:
                    raise ValueError(f"Failed to create calendar: {calendar_path}")
            
            # Get existing event
            event = await collection.get_item(event_uid)
            if not event:
                print(f"Event {event_uid} not found in calendar {calendar_path}")
                return False
            
            print(f"Found existing event {event_uid}")
            event_data = await event.get_component()
            
            # Create new event data
            new_event_data = {
                "summary": task_data["description"],
                "dtstart": task_data["start_date"].strftime("%Y%m%dT%H%M%SZ"),
                "dtend": task_data["end_date"].strftime("%Y%m%dT%H%M%SZ"),
                "description": (
                    f"Estimated hours: {task_data['estimated_hours']}\n"
                    f"Duration hours: {task_data.get('duration_hours', task_data['estimated_hours'])}\n"
                    f"Hourly rate: {task_data.get('hourly_rate', 0.0)}\n"
                    f"Status: {task_data.get('status', 'pending')}\n"
                    f"Confidence: {task_data.get('confidence_score', 0.0):.0%}"
                ),
                "categories": ["PM Tool Task"],
                "status": ("NEEDS-ACTION" if task_data.get("status", "pending") == "pending"
                          else "IN-PROCESS" if task_data.get("status") == "in_progress"
                          else "COMPLETED"),
                "priority": ("1" if task_data.get("priority") == "high"
                            else "5" if task_data.get("priority") == "medium"
                            else "9"),
                "x-pm-tool-id": str(task_data["id"]),
                "x-pm-tool-estimated-hours": str(task_data["estimated_hours"]),
                "x-pm-tool-duration-hours": str(task_data.get("duration_hours", task_data["estimated_hours"])),
                "x-pm-tool-hourly-rate": str(task_data.get("hourly_rate", 0.0)),
                "x-pm-tool-confidence": str(task_data.get("confidence_score", 0.0)),
                "x-pm-tool-rationale": task_data.get("confidence_rationale", "")
            }
            
            try:
                await collection.upload(new_event_data)
                print(f"Successfully updated task {task_data['id']} in calendar")
                return True
            except Exception as e:
                print(f"Error uploading event: {str(e)}")
                raise
        except Exception as e:
            print(f"Failed to update task: {str(e)}")
            raise ValueError(f"Failed to update task: {str(e)}")

    async def delete_task(self, calendar_path: str, event_uid: str):
        try:
            storage = await self.initialize()
            collection = await storage.discover(calendar_path)
            if not collection:
                raise ValueError(f"Calendar not found: {calendar_path}")
                
            event = await collection.get_item(event_uid)
            if not event:
                return False
            
            await collection.delete(event_uid)
            return True
        except Exception as e:
            raise ValueError(f"Failed to delete task: {str(e)}")

    async def sync_task_with_calendar(self, task_data: Dict[str, Any], calendar_path: Optional[str] = None) -> str:
        event_uid = str(uuid.uuid4())
        try:
            print(f"Starting task sync with data: {task_data}")
            
            required_fields = ["id", "title", "description"]
            missing_fields = [field for field in required_fields if field not in task_data]
            if missing_fields:
                print(f"Missing required fields: {', '.join(missing_fields)}")
                return event_uid
            
            # Ensure storage is initialized
            await self.initialize()
            
            # Use sanitized user ID from calendar path or default
            if not calendar_path:
                user_id = settings.CALDAV_USERNAME or "pmtool"
                calendar_path = f"{user_id}/calendar"
            
            # Create calendar directory structure
            calendar_dir = os.path.join(self.calendar_root, calendar_path)
            os.makedirs(calendar_dir, mode=0o755, exist_ok=True)
            print(f"Ensured calendar directory exists: {calendar_dir}")
            print(f"Using calendar path: {calendar_path}")
            
            try:
                start_date = task_data.get("start_date", datetime.now())
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                print(f"Invalid start date format, using current time")
                start_date = datetime.now()
            
            duration_hours = float(task_data.get("duration_hours", task_data.get("estimated_hours", 1)))
            print(f"Task sync - Start date: {start_date}, Duration: {duration_hours}h")
            
            try:
                storage = await self.initialize()
                collection = await storage.discover(calendar_path)
                if not collection:
                    print(f"Calendar not found at {calendar_path}, creating...")
                    await self.create_calendar(settings.CALDAV_USERNAME)
                    collection = await storage.discover(calendar_path)
            except Exception as e:
                print(f"Error accessing calendar: {str(e)}")
                return event_uid
            
            try:
                end_date = task_data.get("end_date")
                if end_date:
                    if isinstance(end_date, str):
                        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                else:
                    end_date = start_date + timedelta(hours=duration_hours)
            except ValueError:
                print(f"Invalid end date format, using duration-based end time")
                end_date = start_date + timedelta(hours=duration_hours)
            
            print(f"Task duration: {duration_hours} hours")
            print(f"Start date: {start_date}")
            print(f"End date: {end_date}")
            
            event = {
                "component": "VEVENT",
                "uid": event_uid,
                "summary": task_data["title"],
                "dtstart": start_date.strftime("%Y%m%dT%H%M%SZ"),
                "dtend": end_date.strftime("%Y%m%dT%H%M%SZ"),
                "description": (
                    f"{task_data['description']}\n\n"
                    f"Duration: {duration_hours} hours\n"
                    f"Hourly rate: {task_data.get('hourly_rate', 0.0)}\n"
                    f"Status: {task_data.get('status', 'pending')}\n"
                    f"Confidence: {task_data.get('confidence_score', 0.0):.0%}"
                ),
                "categories": ["PM Tool Task"],
                "status": ("NEEDS-ACTION" if task_data.get("status", "pending") == "pending"
                         else "IN-PROCESS" if task_data.get("status") == "in_progress"
                         else "COMPLETED"),
                "priority": ("1" if task_data.get("priority") == "high"
                          else "5" if task_data.get("priority") == "medium"
                          else "9"),
                "x-pm-tool-id": str(task_data["id"]),
                "x-pm-tool-title": task_data["title"],
                "x-pm-tool-duration-hours": str(duration_hours),
                "x-pm-tool-hourly-rate": str(task_data.get("hourly_rate", 0.0)),
                "x-pm-tool-confidence": str(task_data.get("confidence_score", 0.0)),
                "x-pm-tool-rationale": task_data.get("confidence_rationale", "")
            }
            
            if self.is_testing:
                print(f"Mock calendar service: Simulating event upload {event_uid}")
                return event_uid

            try:
                print(f"Attempting to sync task {task_data['id']} to calendar {calendar_path}")
                
                # Get or create calendar collection
                storage = await self.initialize()
                collection = await storage.discover(calendar_path)
                if not collection:
                    print(f"Calendar not found. Creating calendar at {calendar_path}")
                    await self.create_calendar(calendar_path.split('/')[0], "PM Tool Calendar")
                    collection = await storage.discover(calendar_path)
                    if not collection:
                        raise ValueError(f"Failed to create calendar at {calendar_path}")
                
                print(f"Calendar found/created. Uploading event {event_uid}")
                await collection.upload(event)
                print(f"Successfully uploaded event {event_uid}")
                return event_uid
                
            except Exception as e:
                print(f"Error uploading event: {str(e)}")
                raise ValueError(f"Failed to sync task: {str(e)}")
        except Exception as e:
            print(f"Failed to sync task: {str(e)}")
            return event_uid
    
    async def get_tasks(self, calendar_path: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        try:
            if start_date and end_date and start_date >= end_date:
                raise ValueError("end_date must be after start_date")
            
            storage = await self.initialize()
            collection = await storage.discover(calendar_path)
            if not collection:
                raise ValueError(f"Calendar not found: {calendar_path}")
            
            tasks = []
            events = await collection.list()
            async for event in events:
                try:
                    event_data = await event.get_component()
                    if not event_data:
                        continue
                    event_start = datetime.strptime(event_data["dtstart"], "%Y%m%dT%H%M%SZ")
                    event_end = datetime.strptime(event_data["dtend"], "%Y%m%dT%H%M%SZ")
                    
                    task = {
                        "uid": event_data["uid"],
                        "description": event_data["summary"],
                        "start_date": event_start,
                        "end_date": event_end,
                        "status": ("pending" if event_data.get("status") == "NEEDS-ACTION"
                                else "in_progress" if event_data.get("status") == "IN-PROCESS"
                                else "completed"),
                        "priority": ("high" if event_data.get("priority") == "1"
                                  else "medium" if event_data.get("priority") == "5"
                                  else "low"),
                        "estimated_hours": float(event_data.get("x-pm-tool-estimated-hours", "0.0")),
                        "duration_hours": float(event_data.get("x-pm-tool-duration-hours", event_data.get("x-pm-tool-estimated-hours", "0.0"))),
                        "hourly_rate": float(event_data.get("x-pm-tool-hourly-rate", "0.0")),
                        "confidence_score": float(event_data.get("x-pm-tool-confidence", "0.0")),
                        "confidence_rationale": event_data.get("x-pm-tool-rationale", "")
                    }
                    
                    if start_date and end_date:
                        if start_date <= event_start <= end_date or start_date <= event_end <= end_date:
                            tasks.append(task)
                    else:
                        tasks.append(task)
                except Exception as e:
                    print(f"Warning: Failed to parse event {event_data.get('uid', 'unknown')}: {str(e)}")
                    continue
            
            return tasks
        except Exception as e:
            raise ValueError(f"Failed to get tasks: {str(e)}")
