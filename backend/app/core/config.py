from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "PM Tool"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "pmtool"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Mollie
    MOLLIE_TEST_API_KEY: str = "test_ENdGpCBJjm67KQCPfPWPqRjd6nBafw"
    MOLLIE_LIVE_API_KEY: str = "live_q3v2sAKHnAAd6BeSR4uahJ3QcKWGND"
    MOLLIE_MODE: str = "test"  # Change to "live" in production

    # CalDAV
    CALDAV_SERVER_URL: str = "https://pm.bow-agentur.de/caldav"
    CALDAV_USERNAME: Optional[str] = None  # Set via environment variable CALDAV_USERNAME
    CALDAV_PASSWORD: Optional[str] = None  # Set via environment variable CALDAV_PASSWORD
    CALDAV_AUTH_ENABLED: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
