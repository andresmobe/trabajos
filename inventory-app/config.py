import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    PATRON SINGLETON
    Garantiza que solo exista una instancia de configuracion en toda la app.
    Evita multiples conexiones innecesarias y lecturas repetidas del .env.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
        self.SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:"
            f"{os.getenv('DB_PASSWORD', '')}@"
            f"{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '3306')}/"
            f"{os.getenv('DB_NAME', 'inventory_db')}"
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

        self.MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
        self.MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
        self.MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
        self.MAIL_USERNAME = os.getenv("MAIL_USERNAME")
        self.MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
        self.MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

        self.DEFAULT_MIN_STOCK = int(os.getenv("DEFAULT_MIN_STOCK", 5))

    def as_dict(self):
        """Convierte la config a dict para inicializar Flask."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


def get_config():
    """Punto de acceso global al Singleton."""
    return Config()
