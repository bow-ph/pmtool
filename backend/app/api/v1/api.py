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
    tasks,
    health,
    projects,
    subscriptions,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/api/v1", tags=["auth"])
api_router.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
api_router.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
api_router.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
api_router.include_router(caldav.router, prefix="/api/v1/caldav", tags=["caldav"])
api_router.include_router(estimations.router, prefix="/api/v1/estimations", tags=["estimations"])
api_router.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
api_router.include_router(invoices.router, prefix="/api/v1/invoices", tags=["invoices"])
api_router.include_router(packages.router, prefix="/api/v1/packages", tags=["packages"])
api_router.include_router(task_sync.router, prefix="/api/v1/task-sync", tags=["task-sync"])
api_router.include_router(scheduling.router, prefix="/api/v1/scheduling", tags=["scheduling"])
api_router.include_router(todo.router, prefix="/api/v1/todo", tags=["todo"], include_in_schema=True)
api_router.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["subscriptions"])
api_router.include_router(health.router, prefix="/api/v1/health", tags=["health"])
