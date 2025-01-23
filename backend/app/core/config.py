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
    POSTGRES_DB: str = "bow_db"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    # Security
    SECRET_KEY: str = ""  # Set via environment variable SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587  # SendGrid SMTP port
    SMTP_HOST: str = "smtp.sendgrid.net"
    SMTP_USER: str = "apikey"  # SendGrid uses 'apikey' as username
    SMTP_PASSWORD: Optional[str] = None  # Set via environment variable SENDGRID_API_KEY
    EMAILS_FROM_EMAIL: str = "noreply@bow-agentur.de"
    EMAILS_FROM_NAME: str = "PM Tool"
    
    @property
    def email_enabled(self) -> bool:
        return bool(
            self.SMTP_HOST
            and self.SMTP_PORT
            and self.SMTP_USER
            and self.SMTP_PASSWORD
            and self.EMAILS_FROM_EMAIL
        )

    # Mollie
    MOLLIE_TEST_API_KEY: str = ""  # Set via environment variable MOLLIE_TEST_API_KEY
    MOLLIE_LIVE_API_KEY: str = ""  # Set via environment variable MOLLIE_LIVE_API_KEY
    MOLLIE_MODE: str = "test"  # Set via environment variable MOLLIE_MODE

    # Company Information for Invoices
    COMPANY_NAME: str = "BOW Agentur"
    COMPANY_ADDRESS: str = "Musterstraße 123, 12345 Musterstadt"
    COMPANY_VAT: str = "DE123456789"
    COMPANY_EMAIL: str = "info@bow-agentur.de"
    COMPANY_PHONE: str = "+49 123 456789"
    COMPANY_WEBSITE: str = "https://bow-agentur.de"
    COMPANY_BANK_INFO: str = "IBAN: DE123456789\nBIC: DEUTDEDB123"

    # CalDAV
    CALDAV_SERVER_URL: str = "https://pm.bow-agentur.de/caldav"
    CALDAV_USERNAME: Optional[str] = None  # Set via environment variable CALDAV_USERNAME
    CALDAV_PASSWORD: Optional[str] = None  # Set via environment variable CALDAV_PASSWORD
    CALDAV_AUTH_ENABLED: str = "false"  # Set to "true" to enable authentication

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
