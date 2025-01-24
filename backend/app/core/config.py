from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Database Configuration
    DB_NAME: str = "pmtool"
    DB_USER: str = "pmtool"
    DB_PASSWORD: str
    DB_HOST: str = "localhost"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None

    # CalDAV Configuration
    CALDAV_URL: str = "http://localhost:5232"
    CALDAV_PUBLIC_URL: str = "https://docuplanai.com/caldav"

    # API Keys
    OPENAI_API_KEY: str
    MOLLIE_TEST_API_KEY: str
    MOLLIE_LIVE_API_KEY: str
    SENDGRID_API_KEY: str

    # Application URLs
    FRONTEND_URL: str = "https://docuplanai.com"
    BACKEND_URL: str = "https://admin.docuplanai.com"

    # Email Configuration
    EMAILS_FROM_EMAIL: str = "noreply@docuplanai.com"
    EMAILS_FROM_NAME: str = "DocuPlanAI"

    # JWT Configuration
    JWT_SECRET: str

    # Service Configuration
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = ["admin.docuplanai.com", "localhost"]
    CORS_ORIGINS: List[str] = ["https://docuplanai.com", "http://localhost:3000"]

    # Server Configuration
    SERVER_IP: Optional[str] = None
    SERVER_PASSWORD: Optional[str] = None

    # Model Config
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_file_encoding": "utf-8"
    }

settings = Settings()
