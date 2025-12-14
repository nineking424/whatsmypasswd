from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "WhatsmyPasswd"
    debug: bool = False

    # Security
    master_password: str
    secret_key: str
    encryption_key: str  # AES-256 key (32 bytes, base64 encoded)

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/whatsmypasswd.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
