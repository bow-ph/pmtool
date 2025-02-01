from pydantic_settings import BaseSettings
import os
from typing import List, Optional

class Settings(BaseSettings):
    # Application Configuration
    PROJECT_NAME: str = "DocuPlanAI"
    VERSION: str = "1.0.0"
    API_VERSION: str = "v1"
    API_V1_STR: str = "/api/v1"

    # JWT Configuration
    SECRET_KEY: str = os.getenv("JWT_SECRET", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Database Configuration
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "bow_db")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "pmtool")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "pmtool")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False

    @property
    def redis_url(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        protocol = "rediss" if self.REDIS_SSL else "redis"
        return f"{protocol}://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}"

    # CalDAV Configuration
    CALDAV_HOST: str = "localhost"
    CALDAV_PORT: int = 5232
    CALDAV_SSL: bool = False
    CALDAV_USERNAME: str = os.getenv("CALDAV_USERNAME", "pmtool")
    CALDAV_PASSWORD: str = os.getenv("CALDAV_PASSWORD", "pmtool")
    CALDAV_AUTH_ENABLED: bool = os.getenv("CALDAV_AUTH_ENABLED", "true").lower() == "true"
    
    CALDAV_STORAGE_PATH: str = os.getenv("CALDAV_STORAGE_PATH", "/tmp/caldav_storage")

    @property
    def caldav_storage_path(self) -> str:
        """Get the absolute path to CalDAV storage directory"""
        base_path = self.CALDAV_STORAGE_PATH
        if not os.path.isabs(base_path):
            base_path = os.path.join(os.getcwd(), base_path)
        collection_root = os.path.join(base_path, "collection-root")
        os.makedirs(collection_root, mode=0o755, exist_ok=True)
        print(f"CalDAV storage path: {collection_root}")
        return base_path

    @property
    def caldav_url(self) -> str:
        protocol = "https" if self.CALDAV_SSL else "http"
        return f"{protocol}://{self.CALDAV_HOST}:{self.CALDAV_PORT}"

    CALDAV_PUBLIC_URL: str = "https://docuplanai.com/caldav"

    # Project Configuration
    PROJECT_NAME: str = "PM Tool"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Project Management Tool API"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    SECRET_KEY: str

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
    SESSION_SECRET: str

    # Service Configuration
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = ["admin.docuplanai.com", "localhost"]

    # Server Configuration
    SERVER_IP: Optional[str] = None
    SERVER_PASSWORD: Optional[str] = None

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}/{self.DATABASE_NAME}?client_encoding=utf8"

    # Model Config
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_file_encoding": "utf-8",
        "extra": "allow",
        "validate_default": True,
        "protected_namespaces": (),
        "validate_assignment": True,
        "use_enum_values": True,
        "str_strip_whitespace": True,
        "str_to_lower": False,
        "str_to_upper": False,
        "arbitrary_types_allowed": True,
        "json_schema_extra": lambda config: {
            "examples": [{"DATABASE_NAME": "pmtool", "DATABASE_USER": "pmtool"}]
        }
    }

settings = Settings()
