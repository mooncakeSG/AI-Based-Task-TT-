from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App Settings
    app_name: str = "IntelliAssist.AI"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", "8000"))
    
    # CORS Settings
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,https://intelliassist-frontend-idaidfoq4-mooncakesgs-projects.vercel.app,https://intelliassist-frontend-9pniapdi0-mooncakesgs-projects.vercel.app,https://intelliassist-frontend-mjr0irfwc-mooncakesgs-projects.vercel.app,https://*.vercel.app,https://*.onrender.com,https://intelliassist-frontend.onrender.com"
    
    # Database Settings
    # PostgreSQL direct connection (preferred)
    database_url: str = ""  # postgresql://user:password@host:port/database
    
    # Supabase Settings (fallback)
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # File Upload Settings
    max_file_size: int = 5 * 1024 * 1024  # 5MB (optimized for audio transcription)
    allowed_file_types: str = "image/jpeg,image/png,image/gif,image/webp,audio/mpeg,audio/wav,audio/ogg,audio/m4a,application/pdf,text/plain"
    upload_dir: str = "uploads"
    
    # AI Service Settings
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = "llama3-8b-8192"
    
    # Hugging Face Settings
    hf_api_key: str = os.getenv("HF_API_KEY", "")
    hf_base_url: str = os.getenv("HF_BASE_URL", "https://api-inference.huggingface.co")
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Helper functions to convert comma-separated strings to lists
def get_cors_origins() -> List[str]:
    """Get CORS origins as a list"""
    return [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

def get_allowed_file_types() -> List[str]:
    """Get allowed file types as a list"""
    return [file_type.strip() for file_type in settings.allowed_file_types.split(",") if file_type.strip()]

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True) 