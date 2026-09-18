"""
PATRON STRATEGY (dentro del Observer)
Define diferentes estrategias de alerta intercambiables:
- ScreenAlertObserver  -> muestra flash message en pantalla
- EmailAlertObserver   -> envia correo electronico
- DatabaseAlertObserver -> guarda la alerta en la BD

Agregar una nueva estrategia solo requiere crear una clase nueva
sin modificar el codigo existente (principio Open/Closed).
"""
from app.observers.stock_observer import StockObserver


class ScreenAlertObserver(StockObserver):
    """
    Estrategia 1: guarda la alerta en la sesion Flask
    para mostrarla como flash message en el proximo request.
    """
    def __init__(self, flash_messages: list):
        # Lista mutable compartida donde se acumulan los mensajes
        self._messages = flash_messages

    def update(self, product) -> None:
        msg = (
            f"Stock bajo: '{product.name}' tiene {product.quantity} unidades "
            f"(minimo: {product.min_stock})"
        )
        self._messages.append({"type": "warning", "text": msg})


class EmailAlertObserver(StockObserver):
    """
    Estrategia 2: envia un correo al administrador usando Flask-Mail.
    """
    def __init__(self, mail_instance, recipient: str):
        self._mail = mail_instance
        self._recipient = recipient

    def update(self, product) -> None:
        from flask_mail import Message
        subject = f"[Inventario] Stock bajo: {product.name}"
        body = (
            f"El producto '{product.name}' (SKU: {product.sku}) "
            f"tiene {product.quantity} unidades disponibles.\n"
            f"El stock minimo configurado es {product.min_stock}.\n\n"
            f"Por favor realice una reposicion a la brevedad."
        )
        msg = Message(subject=subject, recipients=[self._recipient], body=body)
        try:
            self._mail.send(msg)
        except Exception:
            # Si falla el correo no debe interrumpir la operacion principal
            pass


class DatabaseAlertObserver(StockObserver):
    """
    Estrategia 3: persiste la alerta en la tabla stock_alerts.
    Permite consultar el historial de alertas desde el dashboard.
    """
    def update(self, product) -> None:
        from app.extensions import db
        from app.models.alert import StockAlert

        alert = StockAlert(
            product_id=product.id,
            quantity=product.quantity,
            min_stock=product.min_stock,
        )
        db.session.add(alert)
        db.session.commit()
