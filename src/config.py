from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/crypto_db"
    database_test_url: str = (
        "postgresql://postgres:postgres@localhost:5433/crypto_test_db"
    )

    # Application
    debug: bool = False
    log_level: str = "INFO"
    environment: str = "local"
    max_upload_size_bytes: int = 10_485_760  # 10 MB
    cors_allowed_origins: str = "*"

    # Security
    secret_key: str = "change-me-in-production"
    jwt_access_token_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"


settings = Settings()
