import logging
from typing import Literal

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_db: str
    postgres_user: str
    postgres_password: SecretStr
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432


settings = Settings()
logger = logging.getLogger(__name__)

app = FastAPI(title="Policy RAG", version="0.1.0")


class HealthResponse(BaseModel):
    status: Literal["ok"]


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    try:
        with psycopg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password.get_secret_value(),
            connect_timeout=3,
            options="-c statement_timeout=3000",
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT extversion FROM pg_extension "
                    "WHERE extname = 'vector'"
                )
                if cursor.fetchone() is None:
                    raise HTTPException(
                        status_code=503,
                        detail="pgvector is not enabled",
                    )
    except psycopg.Error as exc:
        logger.exception("Database readiness check failed")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc

    return HealthResponse(status="ok")