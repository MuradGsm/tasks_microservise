from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "worker_service"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    REDIS_URL: str = "redis://redis:6379/0"
    EVENTS_QUEUE_NAME: str = "sjira:events"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()