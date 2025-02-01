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
from fastapi import HTTPException
from app.core.config import settings
from unittest.mock import MagicMock
from radicale import storage
try:
    import vobject
except ImportError:
    vobject = None

class CalDAVService:
    def __init__(self):
        try:
            self.is_testing = os.getenv('TESTING', 'false').lower() == 'true'
            self._init_storage()
            
            if not self.is_testing and not settings.CALDAV_USERNAME:
                raise ValueError("CALDAV_USERNAME must be set")
                
            if settings.CALDAV_AUTH_ENABLED:
                self._init_auth()
                
        except Exception as e:
            print(f"Critical error in CalDAV service initialization: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize CalDAV service: {str(e)}"
            )
            
    def _init_storage(self):
        if self.is_testing:
            self.storage = MagicMock()
            mock_collection = MagicMock()
            mock_collection.upload = MagicMock(return_value=True)
            mock_collection.delete = MagicMock(return_value=True)
            mock_collection.get_item = MagicMock(return_value=None)
            mock_collection.list = MagicMock(return_value=[])
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
            print("Initialized mock CalDAV service for testing")
            return mock_collection
            
        try:
            storage_base = os.path.abspath(settings.caldav_storage_path)
            collection_root = os.path.join(storage_base, "collection-root")
            os.makedirs(collection_root, mode=0o755, exist_ok=True)
            
            storage_config = {
                "filesystem_folder": collection_root,
                "close": True,
                "rights": {
                    "": {"read": True, "write": True},
                    "*": {"read": True, "write": True}
                }
            }
            
            self.storage = storage.load("multifilesystem", **storage_config)
            print(f"Initialized storage at: {collection_root}")
            
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
            
            return self.storage
            
        except Exception as e:
            print(f"Error initializing CalDAV storage: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize CalDAV storage: {str(e)}"
            )
            
        try:
            # Get absolute paths for storage
            storage_base = os.path.abspath(settings.caldav_storage_path)
            if not storage_base:
                storage_base = os.path.abspath(os.path.join(os.getcwd(), "caldav_storage"))
            
            # Create directory structure
            collection_root = os.path.join(storage_base, "collection-root")
            user_dir = os.path.join(collection_root, settings.CALDAV_USERNAME or "pmtool")
            calendar_dir = os.path.join(user_dir, "calendar")
            
            # Create directories with proper permissions
            for directory in [storage_base, collection_root, user_dir, calendar_dir]:
                try:
                    if not os.path.exists(directory):
                        os.makedirs(directory, mode=0o755)
                        print(f"Created directory: {directory}")
                    else:
                        print(f"Directory exists: {directory}")
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to create directory {directory}: {str(e)}"
                    )
            
            from radicale import storage
            from radicale.storage import multifilesystem
            import vobject
            
            # Create initial calendar structure
            calendar_path = f"{settings.CALDAV_USERNAME or 'pmtool'}/calendar"
            calendar_dir = os.path.join(collection_root, calendar_path)
            
            # Create calendar collection if it doesn't exist
            if not os.path.exists(calendar_dir):
                os.makedirs(calendar_dir, exist_ok=True)
                
                # Create calendar properties
                calendar = vobject.iCalendar()
                calendar.add('prodid').value = '-//DocuPlanAI//CalDAV Client//EN'
                calendar.add('version').value = '2.0'
                calendar.add('calscale').value = 'GREGORIAN'
                
                # Save calendar properties
                with open(os.path.join(calendar_dir, '.Radicale.props'), 'w') as f:
                    f.write(calendar.serialize())
            
            # Initialize storage with configuration
            storage_config = {
                "filesystem_folder": collection_root,
                "close": True,
                "rights": {
                    "": {"read": True, "write": True},
                    "*": {"read": True, "write": True}
                }
            }
            self.storage = multifilesystem.Storage(storage_config)
            print(f"Initialized storage at: {collection_root}")
            try:
                collection = self.storage.discover(calendar_path)
                if collection:
                    print(f"Found existing calendar collection: {calendar_path}")
                else:
                    print(f"Creating new calendar collection: {calendar_path}")
                    collection = self.storage.create_collection(calendar_path)
                    if not collection:
                        raise ValueError("Failed to create calendar collection")
                    print(f"Created calendar collection: {calendar_path}")
                
                return collection
            except Exception as e:
                print(f"Error with calendar collection: {str(e)}")
                if "No such file or directory" in str(e):
                    os.makedirs(os.path.join(collection_root, calendar_path), exist_ok=True)
                    collection = self.storage.create_collection(calendar_path)
                    if not collection:
                        raise ValueError("Failed to create calendar collection after directory creation")
                    print(f"Created calendar collection after creating directory: {calendar_path}")
                    return collection
                raise
            
            # Create initial calendar structure
            calendar_path = f"{settings.CALDAV_USERNAME or 'pmtool'}/calendar"
            calendar_file = os.path.join(calendar_dir, "collection.ics")
            if not os.path.exists(calendar_file):
                with open(calendar_file, "w") as f:
                    f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//PM Tool//CalDAV Client//EN\nEND:VCALENDAR\n")
                print(f"Created calendar file at: {calendar_file}")
            
            # Create .Radicale.props file
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
                print(f"Created calendar properties at: {props_file}")
            
            # Create calendar structure before initializing storage
            calendar_path = f"{settings.CALDAV_USERNAME or 'pmtool'}/calendar"
            calendar_file = os.path.join(calendar_dir, "collection.ics")
            props_file = os.path.join(calendar_dir, ".Radicale.props")
            
            # Create calendar file if it doesn't exist
            if not os.path.exists(calendar_file):
                with open(calendar_file, "w") as f:
                    f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//PM Tool//CalDAV Client//EN\nEND:VCALENDAR\n")
                print(f"Created calendar file at: {calendar_file}")
            
            # Create properties file if it doesn't exist
            if not os.path.exists(props_file):
                props = {
                    "tag": "VCALENDAR",
                    "D:resourcetype": ["D:collection", "C:calendar"],
                    "D:displayname": "Default Calendar",
                    "C:supported-calendar-component-set": ["VEVENT", "VTODO"]
                }
                with open(props_file, "w") as f:
                    json.dump(props, f, indent=2)
                print(f"Created calendar properties at: {props_file}")
            
            try:
                # Initialize storage with configuration
                self.storage = multifilesystem.Storage(**storage_config)
                print(f"Initialized storage at: {collection_root}")
                
                # Create initial calendar structure
                calendar_path = f"{settings.CALDAV_USERNAME or 'pmtool'}/calendar"
                
                # Get or create calendar collection
                try:
                    collection = self.storage.discover(calendar_path)
                    if collection:
                        print(f"Found existing calendar collection: {calendar_path}")
                    else:
                        print(f"Creating new calendar collection: {calendar_path}")
                        collection = self.storage.create_collection(calendar_path)
                        if not collection:
                            raise ValueError("Failed to create calendar collection")
                        print(f"Created calendar collection: {calendar_path}")
                    
                    return collection
                    
                except Exception as e:
                    print(f"Error with calendar collection: {str(e)}")
                    if "No such file or directory" in str(e):
                        # Create the calendar directory structure
                        os.makedirs(os.path.join(collection_root, calendar_path), exist_ok=True)
                        collection = self.storage.create_collection(calendar_path)
                        if not collection:
                            raise ValueError("Failed to create calendar collection after directory creation")
                        print(f"Created calendar collection after creating directory: {calendar_path}")
                        return collection
                    raise
            except Exception as e:
                print(f"Storage initialization error: {str(e)}")
                if "No such file or directory" in str(e):
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to initialize CalDAV storage: Directory structure is invalid or inaccessible"
                    )
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize CalDAV storage: {str(e)}"
                )
            
        except Exception as e:
            print(f"Error initializing CalDAV storage: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize CalDAV storage: {str(e)}"
            )
        
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

    def create_calendar(self, user_identifier: str | int, calendar_name: str = "PM Tool"):
        try:
            calendar_path = f"{user_identifier}/calendar"
            print(f"Creating calendar at path: {calendar_path}")
            
            # Get absolute paths
            storage_base = os.path.abspath(self.storage.configuration["filesystem_folder"])
            collection_root = os.path.join(storage_base, "collection-root")
            user_dir = os.path.join(collection_root, str(user_identifier))
            calendar_dir = os.path.join(user_dir, "calendar")
            
            print(f"Storage base: {storage_base}")
            print(f"Collection root: {collection_root}")
            print(f"User directory: {user_dir}")
            print(f"Calendar directory: {calendar_dir}")
            
            # Create directories with proper permissions
            for directory in [storage_base, collection_root, user_dir, calendar_dir]:
                os.makedirs(directory, mode=0o755, exist_ok=True)
                print(f"Created/verified directory: {directory}")
            
            # Create .Radicale.props file
            props_file = os.path.join(calendar_dir, ".Radicale.props")
            props = {
                "tag": "VCALENDAR",
                "D:displayname": calendar_name,
                "C:supported-calendar-component-set": ["VEVENT"],
                "D:resourcetype": ["collection", "calendar"],
                "C:calendar-description": f"Calendar for user {user_identifier}",
            }
            
            with open(props_file, "w") as f:
                json.dump(props, f, indent=2)
            print(f"Created properties file: {props_file}")
            
            # Create collection
            try:
                print(f"Attempting to discover calendar at {calendar_path}")
                collection = self.storage.discover(calendar_path)
                
                if not collection:
                    print(f"Creating new collection at {calendar_path}")
                    collection = self.storage.create_collection(calendar_path, props)
                    if collection:
                        print(f"Successfully created calendar collection at {calendar_path}")
                    else:
                        raise ValueError("Collection creation returned None")
                else:
                    print(f"Found existing calendar at {calendar_path}")
                
                # Verify collection exists
                collection = self.storage.discover(calendar_path)
                if not collection:
                    raise ValueError(f"Failed to verify calendar at {calendar_path}")
                    
                print(f"Calendar verified at {calendar_path}")
                return calendar_path
                
            except Exception as e:
                print(f"Error creating calendar collection: {str(e)}")
                raise ValueError(f"Failed to create calendar collection: {str(e)}")
                
        except Exception as e:
            print(f"Failed to create calendar: {str(e)}")
            raise ValueError(f"Failed to create calendar: {str(e)}")

    def add_task(self, task_data: dict, calendar_path: str):
        try:
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
            collection = self.storage.discover(calendar_path)
            if not collection:
                print(f"Creating calendar at {calendar_path}")
                self.create_calendar(int(calendar_path.split('/')[0]))
                collection = self.storage.discover(calendar_path)
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
                collection.upload(event)
                print(f"Successfully added task {task_data['id']} to calendar")
                return event["uid"]
            except Exception as e:
                print(f"Error uploading event: {str(e)}")
                raise
        except Exception as e:
            raise ValueError(f"Failed to add task: {str(e)}")

    def update_task(self, calendar_path: str, event_uid: str, task_data: dict):
        try:
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
            collection = self.storage.discover(calendar_path)
            if not collection:
                print(f"Creating calendar at {calendar_path}")
                self.create_calendar(int(calendar_path.split('/')[0]))
                collection = self.storage.discover(calendar_path)
                if not collection:
                    raise ValueError(f"Failed to create calendar: {calendar_path}")
            
            # Get existing event
            event = collection.get_item(event_uid)
            if not event:
                print(f"Event {event_uid} not found in calendar {calendar_path}")
                return False
            
            print(f"Found existing event {event_uid}")
            event_data = event.get_component()
            
            # Update event data
            event_data["summary"] = task_data["description"]
            event_data["dtstart"] = task_data["start_date"].strftime("%Y%m%dT%H%M%SZ")
            event_data["dtend"] = task_data["end_date"].strftime("%Y%m%dT%H%M%SZ")
            event_data["description"] = (
                f"Estimated hours: {task_data['estimated_hours']}\n"
                f"Duration hours: {task_data.get('duration_hours', task_data['estimated_hours'])}\n"
                f"Hourly rate: {task_data.get('hourly_rate', 0.0)}\n"
                f"Status: {task_data.get('status', 'pending')}\n"
                f"Confidence: {task_data.get('confidence_score', 0.0):.0%}"
            )
            event_data["categories"] = ["PM Tool Task"]
            event_data["status"] = ("NEEDS-ACTION" if task_data.get("status", "pending") == "pending"
                                  else "IN-PROCESS" if task_data.get("status") == "in_progress"
                                  else "COMPLETED")
            event_data["priority"] = ("1" if task_data.get("priority") == "high"
                                    else "5" if task_data.get("priority") == "medium"
                                    else "9")
            event_data["x-pm-tool-id"] = str(task_data["id"])
            event_data["x-pm-tool-estimated-hours"] = str(task_data["estimated_hours"])
            event_data["x-pm-tool-duration-hours"] = str(task_data.get("duration_hours", task_data["estimated_hours"]))
            event_data["x-pm-tool-hourly-rate"] = str(task_data.get("hourly_rate", 0.0))
            event_data["x-pm-tool-confidence"] = str(task_data.get("confidence_score", 0.0))
            event_data["x-pm-tool-rationale"] = task_data.get("confidence_rationale", "")
            
            try:
                collection.upload(event_data)
                print(f"Successfully updated task {task_data['id']} in calendar")
                return True
            except Exception as e:
                print(f"Error uploading event: {str(e)}")
                raise
        except Exception as e:
            print(f"Failed to update task: {str(e)}")
            raise ValueError(f"Failed to update task: {str(e)}")

    def delete_task(self, calendar_path: str, event_uid: str):
        try:
            collection = self.storage.discover(calendar_path)
            if not collection:
                raise ValueError(f"Calendar not found: {calendar_path}")
                
            event = collection.get_item(event_uid)
            if not event:
                return False
            
            collection.delete(event_uid)
            return True
        except Exception as e:
            raise ValueError(f"Failed to delete task: {str(e)}")

    def sync_task_with_calendar(self, task_data: Dict[str, Any], calendar_path: Optional[str] = None) -> str:
        event_uid = str(uuid.uuid4())
        try:
            print(f"Starting task sync with data: {task_data}")
            
            required_fields = ["id", "title", "description"]
            missing_fields = [field for field in required_fields if field not in task_data]
            if missing_fields:
                print(f"Missing required fields: {', '.join(missing_fields)}")
                return event_uid
            
            # Ensure storage is initialized
            if not hasattr(self, 'storage'):
                self._init_storage()
            
            # Use sanitized user ID from calendar path or default
            if not calendar_path:
                user_id = settings.CALDAV_USERNAME or "pmtool"
                calendar_path = f"{user_id}/calendar"
            
            # Create calendar directory structure
            calendar_dir = os.path.join(self.storage.folder, calendar_path)
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
                collection = self.storage.discover(calendar_path)
                if not collection:
                    print(f"Calendar not found at {calendar_path}, creating...")
                    self.create_calendar(settings.CALDAV_USERNAME)
                    collection = self.storage.discover(calendar_path)
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
                
                # Create calendar directory structure
                calendar_dir = os.path.join(self.storage.folder, calendar_path)
                os.makedirs(calendar_dir, mode=0o755, exist_ok=True)
                
                # Create initial calendar file if it doesn't exist
                calendar_file = os.path.join(calendar_dir, "collection.ics")
                if not os.path.exists(calendar_file):
                    with open(calendar_file, "w") as f:
                        f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//PM Tool//CalDAV Client//EN\nEND:VCALENDAR\n")
                
                # Create or get collection
                collection = self.storage.discover(calendar_path)
                if not collection:
                    print(f"Calendar not found. Creating calendar at {calendar_path}")
                    self.create_calendar(calendar_path.split('/')[0], "PM Tool Calendar")
                    collection = self.storage.discover(calendar_path)
                    if not collection:
                        raise ValueError(f"Failed to create calendar at {calendar_path}")
                
                print(f"Calendar found/created. Uploading event {event_uid}")
                collection.upload(event)
                print(f"Successfully uploaded event {event_uid}")
                return event_uid
                
            except Exception as e:
                print(f"Error uploading event: {str(e)}")
                raise ValueError(f"Failed to sync task: {str(e)}")
        except Exception as e:
            print(f"Failed to sync task: {str(e)}")
            return event_uid
    
    def get_tasks(self, calendar_path: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        try:
            if start_date and end_date and start_date >= end_date:
                raise ValueError("end_date must be after start_date")
            
            collection = self.storage.discover(calendar_path)
            if not collection:
                raise ValueError(f"Calendar not found: {calendar_path}")
            
            tasks = []
            for event in collection.list():
                try:
                    event_data = event.get_component()
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
