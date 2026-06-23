from itsdangerous import BadSignature, SignatureExpired
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth_bp
from app.extensions import db
from app.models.chat_history import ChatHistory
from app.models.user import User
from app.utils.security import generate_reset_token, verify_reset_token


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not full_name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return render_template("auth/register.html")

        user = User(full_name=full_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect(url_for("main.home"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not full_name or not email:
            flash("Name and email are required.", "danger")
            return render_template("auth/profile.html")

        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != current_user.id:
            flash("Email already in use.", "warning")
            return render_template("auth/profile.html")

        current_user.full_name = full_name
        current_user.email = email
        db.session.commit()
        flash("Profile updated.", "success")

    return render_template("auth/profile.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    reset_link = None

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            token = generate_reset_token(user.email)
            reset_link = url_for("auth.reset_password", token=token, _external=False)

        flash(
            "If the email exists, a reset link has been generated.",
            "info",
        )

    return render_template("auth/forgot_password.html", reset_link=reset_link)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = verify_reset_token(
            token,
            max_age_seconds=current_app.config.get("PASSWORD_RESET_MAX_AGE_SECONDS", 1800),
        )
    except (BadSignature, SignatureExpired):
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Invalid reset link.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if not password:
            flash("Password is required.", "danger")
            return render_template("auth/reset_password.html")

        user.set_password(password)
        db.session.commit()
        flash("Password reset successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")


@auth_bp.route("/history")
@login_required
def history():
    records = (
        db.session.query(ChatHistory)
        .filter_by(user_id=current_user.id)
        .order_by(ChatHistory.id.desc())
        .all()
    )
    return render_template("auth/history.html", history=records)
