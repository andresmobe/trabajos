"""
Pila LIFO (Last In, First Out) — Historial de Mantenimiento de Drones
======================================================================
Cada dron posee su propia pila. La operación de mantenimiento más reciente
("Limpieza de salitre", "Cambio de batería", etc.) siempre está en la cima.
Implementada con nodos enlazados para gestión dinámica de memoria.

Operaciones clave:
  apilar(dato)    → O(1)  registra nueva operación
  desapilar()     → O(1)  extrae la más reciente
  ver_cima()      → O(1)  consulta sin extraer
"""


class NodoPila:
    """Nodo de memoria dinámica para la pila."""

    def __init__(self, dato):
        self.dato = dato
        self.anterior = None  # apuntador al nodo inferior en la pila


class PilaLIFO:
    """
    Pila de historial de mantenimiento de un dron.
    El último registro apilado refleja el estado más reciente del dron.
    """

    def __init__(self):
        self._cima = None
        self._tamaño = 0

    # ── Operaciones principales ──────────────────────────────────────────────

    def apilar(self, registro):
        """Apila un nuevo registro de mantenimiento — O(1)."""
        nuevo = NodoPila(registro)
        nuevo.anterior = self._cima
        self._cima = nuevo
        self._tamaño += 1

    def desapilar(self):
        """Extrae y retorna el registro más reciente — O(1). Retorna None si vacía."""
        if self.esta_vacia():
            return None
        dato = self._cima.dato
        self._cima = self._cima.anterior
        self._tamaño -= 1
        return dato

    def ver_cima(self):
        """Consulta el registro más reciente sin extraerlo — O(1)."""
        return self._cima.dato if not self.esta_vacia() else None

    # ── Utilidades ───────────────────────────────────────────────────────────

    def esta_vacia(self):
        return self._cima is None

    @property
    def tamaño(self):
        return self._tamaño

    def obtener_lista(self):
        """Retorna todos los registros (cima→fondo) como lista para la GUI."""
        resultado = []
        actual = self._cima
        while actual:
            resultado.append(actual.dato)
            actual = actual.anterior
        return resultado

    def __len__(self):
        return self._tamaño

    def __repr__(self):
        top = self._cima.dato if self._cima else "vacía"
        return f"PilaLIFO(cima={top!r}, {self._tamaño} registros)"
