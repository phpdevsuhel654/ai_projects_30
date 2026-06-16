import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        defaults = {
            "request_id": "-",
            "method": "-",
            "path": "-",
            "status": "-",
            "remote_addr": "-",
        }
        for key, value in defaults.items():
            if not hasattr(record, key):
                setattr(record, key, value)
        return True


def configure_logging(app):
    level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    log_dir = Path(app.config.get("LOG_DIR", "logs"))
    if not log_dir.is_absolute():
        log_dir = Path(app.root_path).parent / log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / app.config.get("LOG_FILE_NAME", "app.log")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | request_id=%(request_id)s | "
        "%(method)s %(path)s status=%(status)s ip=%(remote_addr)s | %(message)s"
    )

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(RequestContextFilter())

    app.logger.handlers.clear()
    app.logger.setLevel(level)
    app.logger.addHandler(file_handler)
    app.logger.propagate = False
