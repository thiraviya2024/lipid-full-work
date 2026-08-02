from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ValidationInfo
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/lipidai"
    
    # MIMIC Database (add this line!)
    MIMIC_DATABASE_URL: Optional[str] = None
    
    # Groq
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    DEFAULT_LLM_PROVIDER: str = "groq"  # groq, openai, ollama, deepseek
    
    # ============================================================
    # FILE UPLOAD
    # ============================================================
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf", ".docx", ".doc", ".txt", 
        ".xlsx", ".xls", ".csv",
        ".png", ".jpg", ".jpeg", ".gif", ".tiff"
    ]
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "text/plain",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/csv",
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/tiff",
    ]
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # This ignores extra fields from .env


# Singleton instance
settings = Settings()