from fastapi import APIRouter, Depends, HTTPException, Response
from app.services.caldav_service import CalDAVService
from app.core.auth import get_current_user
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/{user_id}.ics")
async def get_user_calendar(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        caldav_service = CalDAVService()
        await caldav_service.initialize()
        calendar_data = await caldav_service.generate_ics_feed(user_id)
        
        return Response(
            content=calendar_data,
            media_type="text/calendar",
            headers={
                "Content-Disposition": f"attachment; filename=calendar-{user_id}.ics"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate calendar feed")
