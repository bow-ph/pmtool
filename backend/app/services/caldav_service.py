from radicale import Application as RadicaleApp
from radicale.storage import load as load_storage
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
import os
import bcrypt
from fastapi import HTTPException
from app.core.config import settings

class CalDAVService:
    def __init__(self):
        """Initialize CalDAV service with authentication"""
        try:
            # Initialize authentication
            self._init_auth()
            
            # Configure Radicale storage with authentication
            config: Dict[str, Any] = {
                "type": "multifilesystem",
                "filesystem_folder": "/var/lib/radicale/collections",
                "auth": {
                    "type": None,
                    "htpasswd_filename": None,
                    "htpasswd_encryption": "bcrypt"
                }
            }
            
            if settings.CALDAV_AUTH_ENABLED:
                config["auth"]["type"] = "htpasswd"
                config["auth"]["htpasswd_filename"] = "/etc/radicale/users"
            
            self.storage = load_storage(config)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize CalDAV service: {str(e)}"
            )
        
    def _init_auth(self):
        """Initialize authentication by creating htpasswd file"""
        if not settings.CALDAV_AUTH_ENABLED:
            return

        try:
            if settings.CALDAV_AUTH_ENABLED:
                if not settings.CALDAV_USERNAME or not settings.CALDAV_PASSWORD:
                    raise ValueError("CalDAV authentication is enabled but credentials are missing")

                htpasswd_dir = os.path.dirname("/etc/radicale/users")
                if not os.path.exists(htpasswd_dir):
                    os.makedirs(htpasswd_dir, mode=0o755, exist_ok=True)

                if not os.path.exists("/etc/radicale/users"):
                    # Generate password hash
                    if not isinstance(settings.CALDAV_PASSWORD, str):
                        raise ValueError("CALDAV_PASSWORD must be a string")
                    password = settings.CALDAV_PASSWORD.encode('utf-8')
                    salt = bcrypt.gensalt()
                    hashed = bcrypt.hashpw(password, salt)
                
                # Write to htpasswd file with secure permissions
                with open("/etc/radicale/users", "w") as f:
                    f.write(f"{settings.CALDAV_USERNAME}:{hashed.decode('utf-8')}\n")
                
                # Set secure permissions on htpasswd file
                os.chmod("/etc/radicale/users", 0o600)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize CalDAV authentication: {str(e)}"
            )

    def create_calendar(self, user_id: int, calendar_name: str = "PM Tool"):
        """Create a new calendar for a user"""
        calendar_path = f"{user_id}/{calendar_name}"
        props = {
            "D:displayname": calendar_name,
            "C:supported-calendar-component-set": ["VEVENT"],
        }
        self.storage.create_collection(calendar_path, props)
        return calendar_path

    def add_task(self, calendar_path: str, task_data: dict):
        """Add a task as an event to the calendar"""
        collection = self.storage.discover(calendar_path)
        
        # Create iCalendar event
        event = {
            "component": "VEVENT",
            "uid": str(uuid.uuid4()),
            "summary": task_data["description"],
            "dtstart": task_data["start_date"].strftime("%Y%m%dT%H%M%SZ"),
            "dtend": task_data["end_date"].strftime("%Y%m%dT%H%M%SZ"),
            "description": f"Estimated hours: {task_data['estimated_hours']}",
        }
        
        collection.upload(event)
        return event["uid"]

    def update_task(self, calendar_path: str, event_uid: str, task_data: dict):
        """Update an existing task in the calendar"""
        collection = self.storage.discover(calendar_path)
        event = collection.get_item(event_uid)
        
        if event:
            event_data = event.get_component()
            event_data["summary"] = task_data["description"]
            event_data["dtstart"] = task_data["start_date"].strftime("%Y%m%dT%H%M%SZ")
            event_data["dtend"] = task_data["end_date"].strftime("%Y%m%dT%H%M%SZ")
            event_data["description"] = f"Estimated hours: {task_data['estimated_hours']}"
            
            collection.upload(event_data)
            return True
        return False

    def delete_task(self, calendar_path: str, event_uid: str):
        """Delete a task from the calendar"""
        collection = self.storage.discover(calendar_path)
        event = collection.get_item(event_uid)
        
        if event:
            collection.delete(event_uid)
            return True
        return False

    def get_tasks(self, calendar_path: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        """Get all tasks in a date range"""
        collection = self.storage.discover(calendar_path)
        tasks = []
        
        for event in collection.list():
            event_data = event.get_component()
            event_start = datetime.strptime(event_data["dtstart"], "%Y%m%dT%H%M%SZ")
            event_end = datetime.strptime(event_data["dtend"], "%Y%m%dT%H%M%SZ")
            
            if start_date and end_date:
                if start_date <= event_start <= end_date or start_date <= event_end <= end_date:
                    tasks.append({
                        "uid": event_data["uid"],
                        "description": event_data["summary"],
                        "start_date": event_start,
                        "end_date": event_end,
                        "estimated_hours": float(event_data["description"].split(": ")[1])
                    })
            else:
                tasks.append({
                    "uid": event_data["uid"],
                    "description": event_data["summary"],
                    "start_date": event_start,
                    "end_date": event_end,
                    "estimated_hours": float(event_data["description"].split(": ")[1])
                })
        
        return tasks
