import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'database' / 'cron_monitor.db').as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    REQUEST_RETRY_COUNT = int(os.getenv("REQUEST_RETRY_COUNT", "2"))
    REQUEST_RETRY_BACKOFF_SECONDS = float(
        os.getenv("REQUEST_RETRY_BACKOFF_SECONDS", "1")
    )
    NOMINATIM_BASE_URL = os.getenv(
        "NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org"
    )

    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
    SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "UTC")
    SCHEDULER_HOURLY_MINUTE = int(os.getenv("SCHEDULER_HOURLY_MINUTE", "0"))
    SCHEDULER_DAILY_HOUR = int(os.getenv("SCHEDULER_DAILY_HOUR", "1"))
    SCHEDULER_DAILY_MINUTE = int(os.getenv("SCHEDULER_DAILY_MINUTE", "0"))
    MONITORING_SCHEDULER_ENABLED = (
        os.getenv("MONITORING_SCHEDULER_ENABLED", "false").lower() == "true"
    )
    MONITORING_SCHEDULER_CRON = os.getenv(
        "MONITORING_SCHEDULER_CRON", "0 2 22-28 * sun"
    )
    MONITORING_SCHEDULER_TIMEZONE = os.getenv("MONITORING_SCHEDULER_TIMEZONE", "UTC")

    # Phase 5: notifications
    NOTIFICATIONS_ENABLED = os.getenv("NOTIFICATIONS_ENABLED", "false").lower() == "true"
    NOTIFICATION_WEBHOOK_URL = os.getenv("NOTIFICATION_WEBHOOK_URL", "").strip()
    NOTIFICATION_TIMEOUT_SECONDS = int(os.getenv("NOTIFICATION_TIMEOUT_SECONDS", "5"))
    NOTIFY_ON_FAILURE = os.getenv("NOTIFY_ON_FAILURE", "true").lower() == "true"
    NOTIFY_ON_SUMMARY = os.getenv("NOTIFY_ON_SUMMARY", "true").lower() == "true"

    # Phase 5: hardening/auth
    API_AUTH_ENABLED = os.getenv("API_AUTH_ENABLED", "false").lower() == "true"
    API_AUTH_KEY = os.getenv("API_AUTH_KEY", "").strip()

    WEB_AUTH_ENABLED = os.getenv("WEB_AUTH_ENABLED", "false").lower() == "true"
    WEB_AUTH_USERNAME = os.getenv("WEB_AUTH_USERNAME", "admin").strip()
    WEB_AUTH_PASSWORD = os.getenv("WEB_AUTH_PASSWORD", "changeme").strip()

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
