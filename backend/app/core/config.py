from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_NAME: str = "pmtool"
    DATABASE_USER: str = "pmtool"
    DATABASE_PASSWORD: str
    DATABASE_HOST: str = "localhost"

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
