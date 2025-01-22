from fastapi import APIRouter
from .endpoints import payments, pricing, caldav, auth, estimations

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["pricing"])
api_router.include_router(caldav.router, prefix="/caldav", tags=["caldav"])
api_router.include_router(estimations.router, prefix="/estimations", tags=["estimations"])
