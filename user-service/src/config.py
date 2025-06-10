# user-service/src/config.py
import os
from typing import Optional

class Settings:
    """
    User service settings
    """
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/userdb"
    )

    # JWT settings
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-this-in-production" # Important: Change this for production and use environment variables
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Service settings
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "user-service")
    SERVICE_VERSION: str = os.getenv("SERVICE_VERSION", "1.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Environment settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development") # e.g., development, staging, production
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO") # e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL

    # CORS settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",") # Comma-separated list of allowed origins

    # Redis settings (for caching and session management, if used)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL") # e.g., redis://localhost:6379/0

    # Email settings (for sending verification emails, etc.)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD") # Store sensitive data like this in environment variables or secrets management
    SMTP_FROM_EMAIL: Optional[str] = os.getenv("SMTP_FROM_EMAIL")

settings = Settings()