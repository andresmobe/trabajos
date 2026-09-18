"""
Cola FIFO (First In, First Out) — Gestión de Solicitudes de Envío
=====================================================================
Asegura que los pedidos se procesen en el mismo orden en que llegaron.
Implementada con nodos enlazados para gestión dinámica de memoria.

Operaciones clave:
  encolar(dato)  → O(1)  inserta al final
  desencolar()   → O(1)  extrae del frente
  ver_frente()   → O(1)  consulta sin extraer
"""


class NodoCola:
    """Nodo de memoria dinámica para la cola."""

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None  # apuntador al próximo nodo


class ColaFIFO:
    """
    Cola de pedidos FIFO implementada con apuntadores.
    Garantiza que el primer pedido en entrar sea el primero en despacharse.
    """

    def __init__(self):
        self._frente = None   # apuntador al primer elemento
        self._final = None    # apuntador al último elemento
        self._tamaño = 0

    # ── Operaciones principales ──────────────────────────────────────────────

    def encolar(self, dato):
        """Inserta un pedido al final de la cola — O(1)."""
        nuevo = NodoCola(dato)
        if self.esta_vacia():
            self._frente = nuevo
            self._final = nuevo
        else:
            self._final.siguiente = nuevo
            self._final = nuevo
        self._tamaño += 1

    def desencolar(self):
        """Extrae y retorna el pedido del frente — O(1). Retorna None si vacía."""
        if self.esta_vacia():
            return None
        dato = self._frente.dato
        self._frente = self._frente.siguiente
        if self._frente is None:
            self._final = None
        self._tamaño -= 1
        return dato

    def ver_frente(self):
        """Consulta el pedido del frente sin extraerlo — O(1)."""
        return self._frente.dato if not self.esta_vacia() else None

    # ── Utilidades ───────────────────────────────────────────────────────────

    def esta_vacia(self):
        return self._frente is None

    @property
    def tamaño(self):
        return self._tamaño

    def obtener_lista(self):
        """Retorna todos los elementos como lista (para visualización en GUI)."""
        resultado = []
        actual = self._frente
        while actual:
            resultado.append(actual.dato)
            actual = actual.siguiente
        return resultado

    def __len__(self):
        return self._tamaño

    def __repr__(self):
        return f"ColaFIFO({self._tamaño} elementos)"
