"""
Controlador de autenticacion (MVC - Controller).
Maneja registro manual, login con email/password y login con Google OAuth.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, oauth
from app.models.user import User
from app.repositories import UserRepository

auth_bp = Blueprint("auth", __name__)
user_repo = UserRepository()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = user_repo.get_by_email(email)
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            flash(f"Bienvenido, {user.name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))

        flash("Email o contrasena incorrectos.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if not all([name, email, password, confirm]):
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("auth/register.html")

        if password != confirm:
            flash("Las contrasenas no coinciden.", "danger")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("La contrasena debe tener al menos 8 caracteres.", "danger")
            return render_template("auth/register.html")

        if user_repo.get_by_email(email):
            flash("Ya existe una cuenta con ese email.", "danger")
            return render_template("auth/register.html")

        user = User(name=name, email=email)
        user.set_password(password)
        user_repo.save(user)

        login_user(user)
        flash("Cuenta creada exitosamente. Bienvenido!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html")


@auth_bp.route("/google/login")
def google_login():
    redirect_uri = "http://localhost:5000/auth/google/callback"
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/google/callback")
def google_callback():
    try:
        token    = oauth.google.authorize_access_token()
        userinfo = token.get("userinfo") or oauth.google.userinfo()

        google_id  = userinfo.get("sub")
        email      = userinfo.get("email")
        name       = userinfo.get("name", email)
        avatar_url = userinfo.get("picture")

        user = user_repo.find_or_create_google_user(google_id, email, name, avatar_url)
        login_user(user)
        flash(f"Bienvenido, {user.name}!", "success")
        return redirect(url_for("dashboard.index"))
    except Exception as exc:
        flash(f"Error al iniciar sesion con Google: {exc}", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesion cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
