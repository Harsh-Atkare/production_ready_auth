from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "Simple Auth API"
    APP_VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database - THIS COMES FROM RENDER!
    DATABASE_URL: str
    
    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()