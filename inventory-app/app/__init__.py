from flask import Flask
from config import get_config
from app.extensions import db, login_manager, mail, oauth
from app.observers import (
    stock_subject,
    DatabaseAlertObserver,
    EmailAlertObserver,
)


def create_app() -> Flask:
    """
    Application Factory de Flask.
    Crea y configura la app; registra blueprints y extensiones.
    """
    app = Flask(__name__)

    # --- Configuracion (Singleton) ---
    cfg = get_config()
    app.config.update(cfg.as_dict())

    # --- Extensiones ---
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesion para acceder."
    login_manager.login_message_category = "warning"

    # --- Cargar usuario para Flask-Login ---
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Google OAuth ---
    oauth.register(
        name="google",
        client_id=app.config.get("GOOGLE_CLIENT_ID"),
        client_secret=app.config.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    # --- Registrar observadores de stock (Observer + Strategy) ---
    stock_subject.attach(DatabaseAlertObserver())
    stock_subject.attach(EmailAlertObserver(mail, app.config.get("MAIL_DEFAULT_SENDER", "")))

    # --- Blueprints (MVC - Controladores) ---
    from app.controllers.auth import auth_bp
    from app.controllers.products import products_bp
    from app.controllers.movements import movements_bp
    from app.controllers.reports import reports_bp
    from app.controllers.dashboard import dashboard_bp
    from app.controllers.categories import categories_bp

    app.register_blueprint(auth_bp,        url_prefix="/auth")
    app.register_blueprint(products_bp,    url_prefix="/products")
    app.register_blueprint(movements_bp,   url_prefix="/movements")
    app.register_blueprint(reports_bp,     url_prefix="/reports")
    app.register_blueprint(categories_bp,  url_prefix="/categories")
    app.register_blueprint(dashboard_bp,   url_prefix="/")

    # --- Inyectar 'now' en todos los templates (usado en el footer) ---
    from datetime import datetime

    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow()}

    # --- Crear tablas si no existen ---
    with app.app_context():
        db.create_all()

    return app
