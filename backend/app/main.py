from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.api import api_router
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=True,
    # Enable automatic redirect for trailing slashes
    redirect_slashes=True
)


# Debug middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request path: {request.url.path}")
    logger.debug(f"Request method: {request.method}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code}")
    return response

# Include API router
app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

@app.get("/")
def root():
    return {"message": "Welcome to PM Tool API"}
