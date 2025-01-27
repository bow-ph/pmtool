from app.core.config import settings
print("Environment loaded successfully")
print("Checking required settings:")
print(f"Database: {settings.DATABASE_NAME}")
print(f"Redis Host: {settings.REDIS_HOST}")
print(f"Frontend URL: {settings.FRONTEND_URL}")
print(f"Backend URL: {settings.BACKEND_URL}")
