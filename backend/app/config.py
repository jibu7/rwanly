from pydantic_settings import BaseSettings
from typing import List
from pydantic import Field


class Settings(BaseSettings):
    # Application settings
    app_name: str = "rwanly Core ERP"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str
    
    # CORS - Parse comma-separated string
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
