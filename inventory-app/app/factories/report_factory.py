"""
PATRON FACTORY METHOD
Crea objetos de reporte sin exponer la logica de construccion.
Agregar un nuevo tipo de reporte solo requiere una nueva clase
y una linea en el diccionario de ReportFactory.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from app.extensions import db
from app.models.movement import StockMovement
from app.models.product import Product


# --- Interfaz base ---

class BaseReport(ABC):
    @abstractmethod
    def generate(self, days: int = 30, user_id=None) -> dict:
        """Retorna los datos del reporte como diccionario."""


# --- Implementaciones concretas ---

class MovementReport(BaseReport):
    def generate(self, days: int = 30, user_id=None) -> dict:
        since = datetime.utcnow() - timedelta(days=days)
        q = StockMovement.query.filter(StockMovement.created_at >= since)
        if user_id:
            q = q.join(Product, Product.id == StockMovement.product_id)\
                 .filter(Product.created_by == user_id)
        movements = q.order_by(StockMovement.created_at.desc()).all()
        return {
            "title": f"Movimientos de inventario (ultimos {days} dias)",
            "days": days,
            "total": len(movements),
            "data": movements,
        }


class PopularProductsReport(BaseReport):
    def generate(self, days: int = 30, user_id=None) -> dict:
        since = datetime.utcnow() - timedelta(days=days)
        q = (
            db.session.query(
                Product.name,
                db.func.sum(StockMovement.quantity).label("total_sold")
            )
            .join(Product, Product.id == StockMovement.product_id)
            .filter(StockMovement.movement_type == "exit")
            .filter(StockMovement.created_at >= since)
        )
        if user_id:
            q = q.filter(Product.created_by == user_id)
        rows = (
            q.group_by(Product.id, Product.name)
             .order_by(db.desc("total_sold"))
             .limit(10)
             .all()
        )
        return {
            "title": f"Productos mas vendidos (ultimos {days} dias)",
            "days": days,
            "data": [{"name": r.name, "total_sold": int(r.total_sold)} for r in rows],
        }


class LowStockReport(BaseReport):
    def generate(self, days: int = 30, user_id=None) -> dict:
        q = Product.query.filter(
            Product.is_active == True,
            Product.quantity <= Product.min_stock
        )
        if user_id:
            q = q.filter(Product.created_by == user_id)
        products = q.order_by(Product.quantity.asc()).all()
        return {
            "title": "Productos con stock bajo",
            "data": products,
            "total": len(products),
        }


# --- Factory ---

class ReportFactory:
    _registry = {
        "movements": MovementReport,
        "popular":   PopularProductsReport,
        "low_stock": LowStockReport,
    }

    @classmethod
    def create(cls, report_type: str) -> BaseReport:
        klass = cls._registry.get(report_type)
        if not klass:
            raise ValueError(f"Tipo de reporte desconocido: '{report_type}'")
        return klass()

    @classmethod
    def available_types(cls) -> list:
        return list(cls._registry.keys())
