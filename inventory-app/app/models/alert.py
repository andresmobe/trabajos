from datetime import datetime
from app.extensions import db


class StockAlert(db.Model):
    """
    Alerta generada automaticamente por el Observer cuando
    el stock de un producto cae por debajo de min_stock.
    """
    __tablename__ = "stock_alerts"

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    min_stock  = db.Column(db.Integer, nullable=False)
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<StockAlert product_id={self.product_id} qty={self.quantity}>"
