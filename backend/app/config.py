from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Core settings
    PROJECT_NAME: str = "Legal Proofreader API"
    API_V1_STR: str = "/api/v1"

    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/app"
    DB_ECHO: bool = False # Set to True for debugging SQL queries

    # JWT settings
    SECRET_KEY: str = "a_very_secret_key_that_should_be_in_env"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Load settings from a .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()