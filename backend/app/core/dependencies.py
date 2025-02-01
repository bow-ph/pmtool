from typing import AsyncGenerator
from app.services.caldav_service import CalDAVService

async def get_caldav_service() -> AsyncGenerator[CalDAVService, None]:
    """Get CalDAV service instance."""
    service = CalDAVService()
    service._init_storage()
    try:
        yield service
    finally:
        # Cleanup if needed
        pass
