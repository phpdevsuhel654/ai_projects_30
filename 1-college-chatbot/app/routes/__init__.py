from flask import Blueprint


main_bp = Blueprint("main", __name__)

from app.routes import main_routes  # noqa: E402,F401
