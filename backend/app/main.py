from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.auth import get_current_user, oauth2_scheme
from app.models.user import User
import logging

# Configure OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Development test user
TEST_USER = User(
    id=1,
    email="admin@pmtool.test",
    is_active=True,
    is_superuser=True,
    subscription_type="enterprise",
    subscription_end_date=None
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=True,
    redirect_slashes=True
)

# Add CORS middleware with specific origins
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative dev port
    "http://172.16.5.2:5173",  # Docker dev server
    "https://docuplanai.com",
    "https://admin.docuplanai.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Length", "Content-Range"]
)



# Override authentication for development
if settings.DEBUG:
    async def get_current_user_override():
        return TEST_USER
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    # Add debug log for auth override
    logger.debug("Authentication override enabled for development with test user: %s", TEST_USER.email)


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
    error_message = f"🔥 Fehler in {request.url.path}: {str(exc)}"
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

@app.get("/")
def root():
    return {"message": "Welcome to PM Tool API"}
