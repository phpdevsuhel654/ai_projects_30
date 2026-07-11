from flask import Blueprint, render_template
from sqlalchemy import text

from database.db import SessionLocal

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    return render_template("index.html", title="Spam Email Detector")


@home_bp.route("/health")
def health():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ready"}
    finally:
        db.close()
