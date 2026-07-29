import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(app) -> None:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=5 * 1024 * 1024, backupCount=3
    )
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, app.config["LOG_LEVEL"], logging.INFO))

    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, app.config["LOG_LEVEL"], logging.INFO))
