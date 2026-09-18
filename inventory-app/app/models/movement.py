from datetime import datetime
from app.extensions import db


class StockMovement(db.Model):
    """
    Registra cada entrada o salida de producto del inventario.
    Guarda el stock antes y despues para tener historial completo.
    """
    __tablename__ = "stock_movements"

    id              = db.Column(db.Integer, primary_key=True)
    product_id      = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    movement_type   = db.Column(db.Enum("entry", "exit"), nullable=False)
    quantity        = db.Column(db.Integer, nullable=False)
    quantity_before = db.Column(db.Integer, nullable=False)
    quantity_after  = db.Column(db.Integer, nullable=False)
    unit_price      = db.Column(db.Numeric(10, 2), nullable=True)
    notes           = db.Column(db.Text, nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_entry(self) -> bool:
        return self.movement_type == "entry"

    @property
    def total_value(self) -> float:
        if self.unit_price:
            return float(self.unit_price * self.quantity)
        return 0.0

    def __repr__(self):
        return f"<Movement {self.movement_type} qty={self.quantity} product_id={self.product_id}>"
