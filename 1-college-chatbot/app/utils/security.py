from itsdangerous import URLSafeTimedSerializer
from flask import current_app


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="password-reset-salt")


def verify_reset_token(token, max_age_seconds):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.loads(
        token,
        salt="password-reset-salt",
        max_age=max_age_seconds,
    )
