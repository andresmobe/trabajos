"""
Capa de servicio que orquesta las operaciones de inventario.
Coordina Repository + Observer: registra movimientos y dispara alertas.
"""
from app.extensions import db
from app.models.movement import StockMovement
from app.observers import stock_subject


class InventoryService:
    """
    Centraliza la logica de negocio de movimientos de stock.
    Usa ProductRepository y MovementRepository (Repository pattern)
    y notifica a stock_subject (Observer pattern) tras cada operacion.
    """

    def register_movement(
        self,
        product,
        user_id: int,
        movement_type: str,
        quantity: int,
        unit_price=None,
        notes: str = None,
    ) -> StockMovement:
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")

        if movement_type == "exit" and quantity > product.quantity:
            raise ValueError(
                f"Stock insuficiente. Disponible: {product.quantity}, solicitado: {quantity}."
            )

        quantity_before = product.quantity
        delta = quantity if movement_type == "entry" else -quantity
        product.quantity += delta
        quantity_after = product.quantity

        movement = StockMovement(
            product_id=product.id,
            user_id=user_id,
            movement_type=movement_type,
            quantity=quantity,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            unit_price=unit_price,
            notes=notes,
        )
        db.session.add(movement)
        db.session.commit()

        # Observer: notifica si el stock quedo bajo el minimo
        stock_subject.check_and_notify(product)

        return movement
