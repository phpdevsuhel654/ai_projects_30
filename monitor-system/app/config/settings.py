import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    _RAW_DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "database" / "monitor_system.db"))
    _DB_PATH_OBJ = Path(_RAW_DATABASE_PATH)
    if not _DB_PATH_OBJ.is_absolute():
        _DB_PATH_OBJ = BASE_DIR / _DB_PATH_OBJ
    _DB_PATH_OBJ.parent.mkdir(parents=True, exist_ok=True)

    DATABASE_PATH = str(_DB_PATH_OBJ)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

    _RAW_LOGS_DIR = os.getenv("LOGS_DIR", str(BASE_DIR / "logs"))
    _LOGS_DIR_OBJ = Path(_RAW_LOGS_DIR)
    if not _LOGS_DIR_OBJ.is_absolute():
        _LOGS_DIR_OBJ = BASE_DIR / _LOGS_DIR_OBJ
    _LOGS_DIR_OBJ.mkdir(parents=True, exist_ok=True)

    LOGS_DIR = str(_LOGS_DIR_OBJ)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 2097152))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))
    APP_LOG_FILE = os.getenv("APP_LOG_FILE", str(_LOGS_DIR_OBJ / "app.log"))
    ERROR_LOG_FILE = os.getenv("ERROR_LOG_FILE", str(_LOGS_DIR_OBJ / "error.log"))

    # Address API defaults (can be changed later)
    ADDRESS_PROVIDER = os.getenv("ADDRESS_PROVIDER", "nominatim")
    NOMINATIM_BASE_URL = os.getenv("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org")

    MONITORING_SCHEDULER_ENABLED = os.getenv("MONITORING_SCHEDULER_ENABLED", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    MONITORING_SCHEDULER_CRON = os.getenv("MONITORING_SCHEDULER_CRON", "0 2 22-28 * sun")
    MONITORING_SCHEDULER_TIMEZONE = os.getenv("MONITORING_SCHEDULER_TIMEZONE", "UTC")
    AUTO_CREATE_DB_ON_START = os.getenv("AUTO_CREATE_DB_ON_START", "true").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config(config_name: str | None = None):
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    return CONFIG_MAP.get(config_name, DevelopmentConfig)
