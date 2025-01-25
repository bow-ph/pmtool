from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Project Configuration
    PROJECT_NAME: str = "DocuPlanAI"
    API_V1_STR: str = "/v1"
    
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

    # API Keys
    OPENAI_API_KEY: str = os.environ.get("Open_AI_API", "")
    MOLLIE_TEST_API_KEY: str = os.environ.get("Mollie___Test_API_Key", "")
    MOLLIE_LIVE_API_KEY: str = os.environ.get("Mollie___Live_API_Key", "")
    SENDGRID_API_KEY: str = os.environ.get("Sendgrid___DocuPlanAI", "")

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_file_encoding": "utf-8",
        "validate_default": True,
        "validate_assignment": True,
        "extra": "allow",
        "env_prefix": "",
        "use_enum_values": True,
        "str_strip_whitespace": True,
        "protected_namespaces": (),
        "env_nested_delimiter": "__",
        "arbitrary_types_allowed": True,
        "json_encoders": {
            "datetime": str
        }
    }

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
    CORS_ORIGINS: List[str] = ["https://docuplanai.com", "http://localhost:3000"]

    # Server Configuration
    SERVER_IP: Optional[str] = None
    SERVER_PASSWORD: Optional[str] = None

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}/{self.DATABASE_NAME}"

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
