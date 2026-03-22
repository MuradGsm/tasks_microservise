from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "worker-service"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    REDIS_URL: str = "redis://redis:6379/0"
    EVENTS_QUEUE_NAME: str = "sjira:events"

    NOTIFICATIONS_URL: str = "http://notifications-service:8000"
    ISSUE_URL: str = "http://issue-service:8000"

    NOTIFICATION_RETRY_ATTEMPTS: int = 3
    NOTIFICATION_RETRY_DELAY_SECONDS: float = 1.0
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()