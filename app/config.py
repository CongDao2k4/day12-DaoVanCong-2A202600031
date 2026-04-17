"""Production config — 12-Factor: tất cả từ environment variables."""
import os
import logging
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Type alias needed by email tools
TlsMode = Literal['starttls', 'ssl']

class Settings(BaseSettings):
    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    # Security
    agent_api_key: str = Field(default="dao-van-cong-secret-123")
    
    # LLM
    google_api_key: Optional[str] = Field(default=None)
    gemini_model: str = Field(default="gemini-1.5-flash")

    # Databases
    database_url: Optional[str] = Field(default=None)
    ctsv_database_url: Optional[str] = Field(default=None)

    # SMTP for Email tools
    smtp_host: Optional[str] = Field(default=None)
    smtp_port: Optional[int] = Field(default=587)
    smtp_user: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    smtp_from: Optional[str] = Field(default=None)
    smtp_tls_mode: TlsMode = Field(default="starttls")

    # Redis (Optional for history/rate limiting)
    redis_url: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def validate_production(self):
        if self.environment == "production":
            if self.agent_api_key == "dao-van-cong-secret-123":
                raise ValueError("BẮT BUỘC phải thay đổi AGENT_API_KEY trong production!")
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY là bắt buộc trong production!")
        return self

# Singleton instance
settings = Settings().validate_production()

# Legacy getters for backward compatibility if needed, 
# but better to use `settings` directly.
def get_database_url() -> Optional[str]:
    return settings.database_url

def get_ctsv_database_url() -> Optional[str]:
    return settings.ctsv_database_url

def get_google_api_key() -> Optional[str]:
    return settings.google_api_key

def get_gemini_model() -> str:
    return settings.gemini_model

def get_smtp_host() -> Optional[str]:
    return settings.smtp_host

def get_smtp_port() -> Optional[int]:
    return settings.smtp_port

def get_smtp_user() -> Optional[str]:
    return settings.smtp_user

def get_smtp_password() -> Optional[str]:
    return settings.smtp_password

def get_smtp_from() -> Optional[str]:
    return settings.smtp_from

def get_smtp_tls_mode() -> TlsMode:
    return settings.smtp_tls_mode
