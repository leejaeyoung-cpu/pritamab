"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Anticancer Drug System"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./anticancer.db"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    UPLOAD_FOLDER: Path = Path("uploads")
    MAX_FILE_SIZE: int = 16777216  # 16MB
    ALLOWED_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".xlsx", ".csv"]
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # AI Models
    MODEL_PATH: Path = Path("../models")
    CELLPOSE_MODEL: str = "cyto2"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Create necessary directories
settings.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(exist_ok=True)
