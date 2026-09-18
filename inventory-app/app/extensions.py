"""
Instancias compartidas de extensiones Flask.
Se inicializan aqui para evitar imports circulares.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth

db           = SQLAlchemy()
login_manager = LoginManager()
mail         = Mail()
oauth        = OAuth()
