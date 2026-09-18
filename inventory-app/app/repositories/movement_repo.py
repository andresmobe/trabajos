from datetime import datetime, timedelta
from app.repositories.base_repo import BaseRepository
from app.models.movement import StockMovement
from app.models.product import Product
from app.extensions import db


class MovementRepository(BaseRepository):
    def __init__(self):
        super().__init__(StockMovement)

    def get_by_product(self, product_id: int):
        return (
            StockMovement.query
            .filter_by(product_id=product_id)
            .order_by(StockMovement.created_at.desc())
            .all()
        )

    def get_recent(self, days: int = 30, user_id=None):
        since = datetime.utcnow() - timedelta(days=days)
        q = StockMovement.query.filter(StockMovement.created_at >= since)
        if user_id:
            q = q.join(Product, Product.id == StockMovement.product_id)\
                 .filter(Product.created_by == user_id)
        return q.order_by(StockMovement.created_at.desc()).all()

    def get_exits_summary(self, days: int = 30, user_id=None):
        since = datetime.utcnow() - timedelta(days=days)
        q = (
            db.session.query(
                StockMovement.product_id,
                db.func.sum(StockMovement.quantity).label("total")
            )
            .filter(StockMovement.movement_type == "exit")
            .filter(StockMovement.created_at >= since)
        )
        if user_id:
            q = q.join(Product, Product.id == StockMovement.product_id)\
                 .filter(Product.created_by == user_id)
        return (
            q.group_by(StockMovement.product_id)
             .order_by(db.desc("total"))
             .all()
        )
