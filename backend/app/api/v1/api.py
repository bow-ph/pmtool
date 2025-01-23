from fastapi import APIRouter
from .endpoints import (
    payments,
    caldav,
    auth,
    estimations,
    admin,
    invoices,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(caldav.router, prefix="/caldav", tags=["caldav"])
api_router.include_router(estimations.router, prefix="/estimations", tags=["estimations"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(invoices.router, tags=["invoices"])
