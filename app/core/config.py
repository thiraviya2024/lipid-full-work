# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/lipidai"
    
    # MIMIC Database
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
    
    # ============================================================
    # CORS - Allowed Origins
    # Add any frontend URLs that need to access this API
    # ============================================================
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",          # React default
        "http://localhost:5500",          # VS Code Live Server
        "http://127.0.0.1:5500",          # VS Code Live Server (IP)
        "http://127.0.0.1:3000",          # React (IP)
        "https://lipidai-frontend.vercel.app",  # Vercel deployment
        "https://lipidai-frontend.netlify.app", # Netlify deployment
        "*"  # For testing - allows all origins (remove in production)
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
