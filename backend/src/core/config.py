"""harkushyn.com backend settings."""
import sys
from typing import Literal, List
from pydantic import PostgresDsn, RedisDsn, field_validator, model_validator, Field, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    PROJECT_NAME: str = "Anonimous Confessions"
    API_V1_STR: str = "/v1"
    
    APP_ENV: str # development / production

    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn

    SESSION_SECRET_KEY: str

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "https://demo.harkushyn.com",
        "https://harkushyn.com",
    ]


    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = ["development", "pre-production", "production"]
        if v not in allowed:
            raise ValueError(f"APP_ENV must be one of: {', '.join(allowed)}")
        return v
    
    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: List[str], info: ValidationInfo) -> List[str]:
        if info.data.get("APP_ENV") == "production":
            for origin in v:
                if "localhost" in origin or "*" in origin:
                    raise ValueError("In production, CORS origins must not include localhost URLs!")
        return v

    @field_validator("SESSION_SECRET_KEY")
    @classmethod
    def validate_secret(cls, v: str, info: ValidationInfo) -> str:
        if len(v) < 32:
            raise ValueError("SESSION_SECRET_KEY is too short! Min 32 chars.")
        return v
    

    # properties
    @property
    def database_url(self) -> str:
        return str(self.DATABASE_URL).replace(
            "postgresql://",
            "postgresql+psycopg_async://",
        )
    
    @property
    def redis_url(self) -> str:
        return str(self.REDIS_URL)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_ignore_empty=True,
        extra="ignore"
    )


try:
    settings = Settings()
except Exception as e:
    print(f"🔥 FATAL CONFIG ERROR: {e}", file=sys.stderr)
    sys.exit(1)
    


settings = Settings()
