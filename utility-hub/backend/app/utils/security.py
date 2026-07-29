from __future__ import annotations

import secrets
from functools import wraps

from flask import current_app, jsonify, redirect, request, session, url_for


def _extract_bearer_token(auth_header: str) -> str | None:
    if not auth_header:
        return None
    parts = auth_header.split(" ", 1)
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1].strip()


def is_api_request_authorized() -> bool:
    if not current_app.config.get("API_AUTH_ENABLED", False):
        return True

    configured_key = current_app.config.get("API_AUTH_KEY", "")
    if not configured_key:
        return False

    token = request.headers.get("X-API-Key", "").strip() or _extract_bearer_token(
        request.headers.get("Authorization", "")
    )
    if not token:
        return False

    return secrets.compare_digest(token, configured_key)


def enforce_api_auth():
    if not is_api_request_authorized():
        return jsonify({"error": "unauthorized"}), 401
    return None


def web_login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_app.config.get("WEB_AUTH_ENABLED", False):
            return view_func(*args, **kwargs)

        if session.get("web_user_authenticated"):
            return view_func(*args, **kwargs)

        return redirect(url_for("web.login_page", next=request.path))

    return wrapped


def register_security_headers(app):
    @app.after_request
    def _apply_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers[
            "Content-Security-Policy"
        ] = "default-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none';"
        return response
