from fastapi import APIRouter
from app.api.v1.endpoints import (
    payments,
    caldav,
    auth,
    estimations,
    admin,
    invoices,
    packages,
    scheduling,
    task_sync,
    todo,
    health,
    pdf,
    hints,
    _projects
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
api_router.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
api_router.include_router(caldav.router, prefix="/api/v1/calendar", tags=["calendar"])
api_router.include_router(estimations.router, prefix="/api/v1/estimations", tags=["estimations"])
api_router.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
api_router.include_router(invoices.router, prefix="/api/v1/invoices", tags=["invoices"])
api_router.include_router(packages.router, prefix="/api/v1/packages", tags=["packages"])
api_router.include_router(task_sync.router, prefix="/api/v1/task-sync", tags=["task-sync"])
api_router.include_router(scheduling.router, prefix="/api/v1/scheduling", tags=["scheduling"])
api_router.include_router(todo.router, prefix="/api/v1/todo", tags=["todo"], include_in_schema=True)
api_router.include_router(health.router, tags=["health"])
api_router.include_router(pdf.router, prefix="/api/v1/pdf", tags=["pdf"])
api_router.include_router(hints.router, prefix="/api/v1/projects", tags=["hints"])
api_router.include_router(_projects.router, prefix="/api/v1/projects", tags=["projects"])
