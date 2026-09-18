"""
Lista Doblemente Encadenada (LDE) — Secuencia de Entregas de un Dron
=====================================================================
Cada nodo tiene apuntadores hacia adelante y hacia atrás, lo que permite:
  • Recorrer la ruta de entrega en ambas direcciones.
  • Insertar o eliminar puntos de entrega en O(1) dado el nodo, sin
    desplazar elementos (ventaja frente a arreglos).

Caso de uso: el turista en Taganga cambia su dirección al Centro Histórico
→ se elimina el nodo de Taganga e inserta el nuevo punto sin recrear la lista.
"""


class NodoLDE:
    """Nodo de memoria dinámica con apuntadores anterior y siguiente."""

    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None  # apuntador al próximo destino
        self.anterior = None   # apuntador al destino previo


class ListaDoblementeEncadenada:
    """
    Lista doblemente encadenada que almacena la secuencia de destinos
    asignada a un dron para un viaje de entrega.
    """

    def __init__(self):
        self._cabeza = None
        self._cola = None
        self._tamaño = 0

    # ── Inserción ────────────────────────────────────────────────────────────

    def insertar_al_final(self, dato):
        """Agrega un nuevo destino al final de la ruta — O(1)."""
        nuevo = NodoLDE(dato)
        if self.esta_vacia():
            self._cabeza = self._cola = nuevo
        else:
            nuevo.anterior = self._cola
            self._cola.siguiente = nuevo
            self._cola = nuevo
        self._tamaño += 1

    def insertar_al_inicio(self, dato):
        """Agrega un destino urgente al inicio de la ruta — O(1)."""
        nuevo = NodoLDE(dato)
        if self.esta_vacia():
            self._cabeza = self._cola = nuevo
        else:
            nuevo.siguiente = self._cabeza
            self._cabeza.anterior = nuevo
            self._cabeza = nuevo
        self._tamaño += 1

    def insertar_en_posicion(self, dato, pos):
        """Inserta en la posición indicada (0-indexada) — O(n)."""
        if pos <= 0:
            self.insertar_al_inicio(dato)
            return
        if pos >= self._tamaño:
            self.insertar_al_final(dato)
            return
        nuevo = NodoLDE(dato)
        actual = self._cabeza
        for _ in range(pos - 1):
            actual = actual.siguiente
        nuevo.siguiente = actual.siguiente
        nuevo.anterior = actual
        if actual.siguiente:
            actual.siguiente.anterior = nuevo
        actual.siguiente = nuevo
        self._tamaño += 1

    # ── Eliminación ──────────────────────────────────────────────────────────

    def eliminar_por_valor(self, valor):
        """Elimina la primera ocurrencia del valor — O(n). Retorna True si eliminó."""
        actual = self._cabeza
        while actual:
            if actual.dato == valor:
                if actual.anterior:
                    actual.anterior.siguiente = actual.siguiente
                else:
                    self._cabeza = actual.siguiente
                if actual.siguiente:
                    actual.siguiente.anterior = actual.anterior
                else:
                    self._cola = actual.anterior
                self._tamaño -= 1
                return True
            actual = actual.siguiente
        return False

    def eliminar_primero(self):
        """Extrae el primer elemento (destino ya alcanzado) — O(1)."""
        if self.esta_vacia():
            return None
        dato = self._cabeza.dato
        self._cabeza = self._cabeza.siguiente
        if self._cabeza:
            self._cabeza.anterior = None
        else:
            self._cola = None
        self._tamaño -= 1
        return dato

    # ── Recorridos ───────────────────────────────────────────────────────────

    def recorrer_adelante(self):
        """Recorre cabeza→cola (orden de visita de destinos)."""
        resultado = []
        actual = self._cabeza
        while actual:
            resultado.append(actual.dato)
            actual = actual.siguiente
        return resultado

    def recorrer_atras(self):
        """Recorre cola→cabeza (ruta inversa para retorno al almacén)."""
        resultado = []
        actual = self._cola
        while actual:
            resultado.append(actual.dato)
            actual = actual.anterior
        return resultado

    # ── Utilidades ───────────────────────────────────────────────────────────

    def esta_vacia(self):
        return self._cabeza is None

    @property
    def tamaño(self):
        return self._tamaño

    def limpiar(self):
        self._cabeza = self._cola = None
        self._tamaño = 0

    def __len__(self):
        return self._tamaño

    def __repr__(self):
        return " ↔ ".join(str(x) for x in self.recorrer_adelante())
