from __future__ import annotations

import json
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from uuid import uuid4

from flask import Flask, g, request
from werkzeug.exceptions import HTTPException


def setup_logging(app: Flask) -> None:
    level_name = str(app.config.get("LOG_LEVEL", "INFO")).upper()
    log_level = getattr(logging, level_name, logging.INFO)

    logs_dir = Path(app.config.get("LOGS_DIR", "logs"))
    logs_dir.mkdir(parents=True, exist_ok=True)

    app_log_path = Path(app.config.get("APP_LOG_FILE", str(logs_dir / "app.log")))
    error_log_path = Path(app.config.get("ERROR_LOG_FILE", str(logs_dir / "error.log")))

    app.logger.handlers.clear()
    app.logger.setLevel(log_level)
    app.logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    app_handler = RotatingFileHandler(
        app_log_path,
        maxBytes=int(app.config.get("LOG_MAX_BYTES", 2 * 1024 * 1024)),
        backupCount=int(app.config.get("LOG_BACKUP_COUNT", 5)),
        encoding="utf-8",
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(log_level)

    error_handler = RotatingFileHandler(
        error_log_path,
        maxBytes=int(app.config.get("LOG_MAX_BYTES", 2 * 1024 * 1024)),
        backupCount=int(app.config.get("LOG_BACKUP_COUNT", 5)),
        encoding="utf-8",
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    app.logger.addHandler(app_handler)
    app.logger.addHandler(error_handler)


def register_request_logging(app: Flask) -> None:
    @app.before_request
    def before_request_logging() -> None:
        g.request_id = request.headers.get("X-Request-ID") or str(uuid4())
        g.request_start = time.perf_counter()

    @app.after_request
    def after_request_logging(response):
        request_id = getattr(g, "request_id", str(uuid4()))
        started = getattr(g, "request_start", None)
        duration_ms = 0
        if started is not None:
            duration_ms = int((time.perf_counter() - started) * 1000)

        response.headers["X-Request-ID"] = request_id

        payload = {
            "request_id": request_id,
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "remote_addr": request.remote_addr,
        }
        app.logger.info("request_complete %s", json.dumps(payload, ensure_ascii=True))
        return response

    @app.errorhandler(Exception)
    def log_unhandled_exception(exc: Exception):
        if isinstance(exc, HTTPException):
            return exc

        request_id = getattr(g, "request_id", str(uuid4()))
        app.logger.exception(
            "unhandled_exception request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.path,
        )
        return {
            "error": "Internal server error",
            "request_id": request_id,
        }, 500
