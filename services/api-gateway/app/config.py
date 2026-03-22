import os


class Settings:
    SERVICE_NAME = "api-gateway"

    IDENTITY_URL = os.getenv("IDENTITY_URL", "http://identity-service:8000")
    PROJECT_URL = os.getenv("PROJECT_URL", "http://project-service:8000")
    ISSUE_URL = os.getenv("ISSUE_URL", "http://issue-service:8000")
    NOTIFICATIONS_URL = os.getenv(
        "NOTIFICATIONS_URL",
        "http://notifications-service:8000",
    )

    AUTH_TIMEOUT_SECONDS = float(os.getenv("AUTH_TIMEOUT_SECONDS", "5"))
    UPSTREAM_TIMEOUT_SECONDS = float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "10"))

    CORS_ALLOW_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
        if origin.strip()
    ]


settings = Settings()