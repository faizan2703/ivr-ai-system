"""Configuration settings for the IVR system"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    APP_NAME: str = "IVR AI Agent System"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Vector Database Configuration
    VECTOR_DB_PATH: str = "./data/chroma"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Twilio Configuration (for phone integration)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # RAG Configuration
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVAL_TOP_K: int = 3
    
    # IVR Configuration
    MAX_RETRIES: int = 3
    CONVERSATION_TIMEOUT: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
