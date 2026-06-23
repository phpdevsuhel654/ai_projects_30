from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))

        if current_user.role != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("main.home"))

        return view_func(*args, **kwargs)

    return wrapper
