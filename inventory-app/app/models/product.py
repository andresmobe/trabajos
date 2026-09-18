from datetime import datetime
from app.extensions import db


class Product(db.Model):
    """
    Modelo de producto.
    El campo min_stock es el umbral que dispara el Observer de alertas.
    """
    __tablename__ = "products"

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(255), nullable=False)
    description    = db.Column(db.Text, nullable=True)
    sku            = db.Column(db.String(100), unique=True, nullable=True)
    quantity       = db.Column(db.Integer, nullable=False, default=0)
    min_stock      = db.Column(db.Integer, nullable=False, default=5)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_price     = db.Column(db.Numeric(10, 2), nullable=False)
    category_id    = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_by     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    is_active      = db.Column(db.Boolean, default=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    movements = db.relationship("StockMovement", backref="product", lazy="dynamic")
    alerts    = db.relationship("StockAlert", backref="product", lazy="dynamic")

    @property
    def is_low_stock(self) -> bool:
        """True cuando el stock esta por debajo del umbral minimo."""
        return self.quantity <= self.min_stock

    @property
    def profit_margin(self) -> float:
        """Margen de ganancia en porcentaje."""
        if self.purchase_price == 0:
            return 0.0
        return float((self.sale_price - self.purchase_price) / self.purchase_price * 100)

    def __repr__(self):
        return f"<Product {self.name} qty={self.quantity}>"
