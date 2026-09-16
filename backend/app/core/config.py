import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/smart_dine")
    DIRECT_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/smart_dine")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # JWT Authentication
    JWT_SECRET: str = Field(default="change-this-to-a-secure-random-string")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Application
    NEXT_PUBLIC_APP_URL: str = Field(default="http://localhost:3000")
    NODE_ENV: str = Field(default="development")

    # CORS
    CORS_ORIGINS: list = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
        ]
    )

    # Storage
    STORAGE_BUCKET: str = Field(default="smart-dine-media")
    STORAGE_ENDPOINT: str = Field(default="http://localhost:9000")
    STORAGE_ACCESS_KEY: str = Field(default="minio")
    STORAGE_SECRET_KEY: str = Field(default="minio123")

    # Payment Provider
    PAYMENT_PROVIDER_KEY: str = Field(default="your-payment-key")
    PAYMENT_PROVIDER_SECRET: str = Field(default="your-payment-secret")

    # AI
    AI_API_KEY: str = Field(default="your-ai-api-key")

    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)


settings = Settings()