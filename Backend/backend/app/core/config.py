import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TraceX"
    app_env: str = "development"
    app_version: str = "1.0.0"
    debug: bool = True
    
    cors_origins: list[str] = ["http://localhost", "http://localhost:8080", "http://localhost:3000"]
    cors_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: list[str] = ["*"]
    cors_credentials: bool = True

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "tracex"
    postgres_user: str = "tracex"
    postgres_password: str = "tracex_dev_password"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "tracex_dev_password"

    jwt_secret_key: str = "change-this-development-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    bootstrap_admin_email: str | None = None
    bootstrap_admin_password: str | None = None

    # M4 NLP Extraction Path
    extraction_documents_path: str = str(Path(__file__).resolve().parent.parent.parent.parent.parent / "TRACEX_PREPARED" / "documents.csv")

    # M8 ML Analytics
    tracex_model_dir: str = str(Path(__file__).resolve().parent.parent.parent / "ml_models")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()