import pytest
from unittest.mock import patch, MagicMock
from app.services.caldav_service import CalDAVService
from datetime import datetime, timedelta

@pytest.fixture
def caldav_service():
    with patch.dict('os.environ', {
        'CALDAV_USERNAME': 'test_user',
        'CALDAV_PASSWORD': 'test_pass'
    }):
        return CalDAVService()

def test_calendar_path_format(caldav_service):
    """Test that calendar path follows the required format"""
    user_id = 123
    calendar_name = "Test Calendar"
    calendar_path = caldav_service.create_calendar(user_id, calendar_name)
    assert calendar_path == f"{user_id}/{calendar_name}"

@pytest.mark.asyncio
async def test_add_task(caldav_service):
    """Test adding a task to the calendar"""
    calendar_path = "123/Test Calendar"
    task_data = {
        "description": "Test Task",
        "start_date": datetime.now(),
        "end_date": datetime.now() + timedelta(hours=2),
        "estimated_hours": 2.0
    }
    
    with patch('radicale.storage.load') as mock_storage:
        mock_collection = MagicMock()
        mock_storage.return_value.discover.return_value = mock_collection
        
        event_uid = caldav_service.add_task(calendar_path, task_data)
        assert event_uid is not None
        mock_collection.upload.assert_called_once()

@pytest.mark.asyncio
async def test_update_task(caldav_service):
    """Test updating an existing task"""
    calendar_path = "123/Test Calendar"
    event_uid = "test-uid"
    task_data = {
        "description": "Updated Task",
        "start_date": datetime.now(),
        "end_date": datetime.now() + timedelta(hours=2),
        "estimated_hours": 3.0
    }
    
    with patch('radicale.storage.load') as mock_storage:
        mock_collection = MagicMock()
        mock_event = MagicMock()
        mock_storage.return_value.discover.return_value = mock_collection
        mock_collection.get_item.return_value = mock_event
        
        result = caldav_service.update_task(calendar_path, event_uid, task_data)
        assert result is True
        mock_collection.upload.assert_called_once()

@pytest.mark.asyncio
async def test_delete_task(caldav_service):
    """Test deleting a task"""
    calendar_path = "123/Test Calendar"
    event_uid = "test-uid"
    
    with patch('radicale.storage.load') as mock_storage:
        mock_collection = MagicMock()
        mock_event = MagicMock()
        mock_storage.return_value.discover.return_value = mock_collection
        mock_collection.get_item.return_value = mock_event
        
        result = caldav_service.delete_task(calendar_path, event_uid)
        assert result is True
        mock_collection.delete.assert_called_once_with(event_uid)

@pytest.mark.asyncio
async def test_get_tasks(caldav_service):
    """Test retrieving tasks in a date range"""
    calendar_path = "123/Test Calendar"
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    mock_event_data = {
        "uid": "test-uid",
        "summary": "Test Task",
        "dtstart": start_date.strftime("%Y%m%dT%H%M%SZ"),
        "dtend": (start_date + timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ"),
        "description": "Estimated hours: 2.0"
    }
    
    with patch('radicale.storage.load') as mock_storage:
        mock_collection = MagicMock()
        mock_event = MagicMock()
        mock_event.get_component.return_value = mock_event_data
        mock_storage.return_value.discover.return_value = mock_collection
        mock_collection.list.return_value = [mock_event]
        
        tasks = caldav_service.get_tasks(calendar_path, start_date, end_date)
        assert len(tasks) == 1
        assert tasks[0]["uid"] == "test-uid"
        assert tasks[0]["estimated_hours"] == 2.0

def test_authentication_disabled(caldav_service):
    """Test CalDAV service with authentication disabled"""
    with patch.dict('os.environ', {'CALDAV_AUTH_ENABLED': 'false'}):
        service = CalDAVService()
        assert service.storage.configuration["auth"]["type"] is None

def test_authentication_enabled(caldav_service):
    """Test CalDAV service with authentication enabled"""
    assert caldav_service.storage.configuration["auth"]["type"] == "htpasswd"
    assert caldav_service.storage.configuration["auth"]["htpasswd_encryption"] == "bcrypt"
