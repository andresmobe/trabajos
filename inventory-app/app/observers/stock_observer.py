"""
PATRON OBSERVER
Permite que multiples observadores reaccionen cuando el stock
de un producto cae por debajo del minimo, sin acoplar la logica
de negocio con la logica de notificacion.

Sujeto  -> StockSubject   (notifica cambios)
Observadores -> ScreenAlertObserver, EmailAlertObserver
"""
from abc import ABC, abstractmethod


# --- Interfaz base para todos los observadores ---

class StockObserver(ABC):
    @abstractmethod
    def update(self, product) -> None:
        """Se ejecuta cuando el sujeto notifica un cambio de stock."""


# --- Sujeto (Subject) ---

class StockSubject:
    """
    Gestiona la lista de observadores y los notifica
    cada vez que un producto alcanza stock bajo.
    """
    def __init__(self):
        self._observers: list[StockObserver] = []

    def attach(self, observer: StockObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: StockObserver) -> None:
        self._observers.remove(observer)

    def notify(self, product) -> None:
        """Llama a update() en cada observador registrado."""
        for observer in self._observers:
            observer.update(product)

    def check_and_notify(self, product) -> None:
        """Verifica si el producto tiene stock bajo y notifica si es necesario."""
        if product.is_low_stock:
            self.notify(product)


# Instancia global del sujeto (reutilizada en toda la app)
stock_subject = StockSubject()
