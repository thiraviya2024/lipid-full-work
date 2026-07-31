from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/lipidai"
    
    # MIMIC Database (add this line!)
    MIMIC_DATABASE_URL: Optional[str] = None
    
    # Groq
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # App
    APP_NAME: str = "LipidAI API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt", ".xlsx", ".xls", ".csv", ".jpg", ".jpeg", ".png"]
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # This ignores extra fields from .env


settings = Settings()