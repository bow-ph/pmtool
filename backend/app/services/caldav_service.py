from radicale import Application as RadicaleApp
from radicale.storage import load as load_storage
from datetime import datetime
from typing import List, Optional
import uuid
import os

class CalDAVService:
    def __init__(self):
        # Configure Radicale storage
        self.storage = load_storage({
            "type": "multifilesystem",
            "filesystem_folder": "/var/lib/radicale/collections",
        })

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
