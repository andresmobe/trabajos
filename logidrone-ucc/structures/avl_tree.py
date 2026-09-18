"""
Árbol AVL — Inventario de Productos de Urgencia
================================================
Árbol de búsqueda binaria auto-balanceado (Adelson-Velsky y Landis, 1962).
El factor de balance de cada nodo se mantiene entre -1 y 1 mediante
rotaciones automáticas. Garantiza:
  búsqueda  → O(log n)
  inserción → O(log n)
  eliminación → O(log n)

Esto es crítico bajo la alta demanda del mediodía en temporada turística.
"""


class NodoAVL:
    """Nodo de memoria dinámica del árbol AVL."""

    def __init__(self, producto):
        self.producto = producto
        self.clave = producto.id       # clave de comparación (ID único)
        self.izq = None                # sub-árbol izquierdo
        self.der = None                # sub-árbol derecho
        self.altura = 1                # altura del sub-árbol enraizado aquí


class ArbolAVL:
    """
    Árbol AVL de inventario. Clave = ID del producto (entero).
    Las rotaciones se realizan automáticamente para mantener el balance.
    """

    def __init__(self):
        self._raiz = None
        self._cantidad = 0

    # ── Helpers de altura y balance ──────────────────────────────────────────

    @staticmethod
    def _altura(n):
        return n.altura if n else 0

    def _factor_balance(self, n):
        return self._altura(n.izq) - self._altura(n.der) if n else 0

    def _actualizar_altura(self, n):
        n.altura = 1 + max(self._altura(n.izq), self._altura(n.der))

    # ── Rotaciones ───────────────────────────────────────────────────────────

    def _rotar_derecha(self, z):
        """Rotación simple derecha: corrige desbalance Izquierda-Izquierda."""
        y = z.izq
        t3 = y.der
        y.der = z
        z.izq = t3
        self._actualizar_altura(z)
        self._actualizar_altura(y)
        return y

    def _rotar_izquierda(self, z):
        """Rotación simple izquierda: corrige desbalance Derecha-Derecha."""
        y = z.der
        t2 = y.izq
        y.izq = z
        z.der = t2
        self._actualizar_altura(z)
        self._actualizar_altura(y)
        return y

    def _rebalancear(self, nodo, clave):
        """Aplica la rotación necesaria según el factor de balance."""
        self._actualizar_altura(nodo)
        fb = self._factor_balance(nodo)

        # Izquierda-Izquierda
        if fb > 1 and clave < nodo.izq.clave:
            return self._rotar_derecha(nodo)
        # Derecha-Derecha
        if fb < -1 and clave > nodo.der.clave:
            return self._rotar_izquierda(nodo)
        # Izquierda-Derecha
        if fb > 1 and clave > nodo.izq.clave:
            nodo.izq = self._rotar_izquierda(nodo.izq)
            return self._rotar_derecha(nodo)
        # Derecha-Izquierda
        if fb < -1 and clave < nodo.der.clave:
            nodo.der = self._rotar_derecha(nodo.der)
            return self._rotar_izquierda(nodo)
        return nodo

    # ── Inserción ────────────────────────────────────────────────────────────

    def _insertar(self, nodo, producto):
        if not nodo:
            return NodoAVL(producto)
        if producto.id < nodo.clave:
            nodo.izq = self._insertar(nodo.izq, producto)
        elif producto.id > nodo.clave:
            nodo.der = self._insertar(nodo.der, producto)
        else:
            nodo.producto = producto   # actualizar si ya existe
            return nodo
        return self._rebalancear(nodo, producto.id)

    def insertar(self, producto):
        """Inserta o actualiza un producto en el árbol — O(log n)."""
        prev = self._cantidad
        self._raiz = self._insertar(self._raiz, producto)
        # Si la clave ya existía, _insertar actualiza sin aumentar conteo
        if self._buscar(self._raiz, producto.id):
            # Contamos solo si era nuevo
            pass
        self._cantidad = self._contar(self._raiz)

    # ── Búsqueda ─────────────────────────────────────────────────────────────

    def _buscar(self, nodo, id_prod):
        if not nodo:
            return None
        if id_prod == nodo.clave:
            return nodo.producto
        elif id_prod < nodo.clave:
            return self._buscar(nodo.izq, id_prod)
        else:
            return self._buscar(nodo.der, id_prod)

    def buscar(self, id_prod):
        """Busca un producto por ID — O(log n). Retorna el producto o None."""
        return self._buscar(self._raiz, id_prod)

    # ── Eliminación ──────────────────────────────────────────────────────────

    @staticmethod
    def _minimo(nodo):
        while nodo.izq:
            nodo = nodo.izq
        return nodo

    def _eliminar(self, nodo, id_prod):
        if not nodo:
            return nodo
        if id_prod < nodo.clave:
            nodo.izq = self._eliminar(nodo.izq, id_prod)
        elif id_prod > nodo.clave:
            nodo.der = self._eliminar(nodo.der, id_prod)
        else:
            if not nodo.izq or not nodo.der:
                nodo = nodo.izq or nodo.der
            else:
                sucesor = self._minimo(nodo.der)
                nodo.clave = sucesor.clave
                nodo.producto = sucesor.producto
                nodo.der = self._eliminar(nodo.der, sucesor.clave)
        if not nodo:
            return nodo
        self._actualizar_altura(nodo)
        fb = self._factor_balance(nodo)
        if fb > 1 and self._factor_balance(nodo.izq) >= 0:
            return self._rotar_derecha(nodo)
        if fb > 1 and self._factor_balance(nodo.izq) < 0:
            nodo.izq = self._rotar_izquierda(nodo.izq)
            return self._rotar_derecha(nodo)
        if fb < -1 and self._factor_balance(nodo.der) <= 0:
            return self._rotar_izquierda(nodo)
        if fb < -1 and self._factor_balance(nodo.der) > 0:
            nodo.der = self._rotar_derecha(nodo.der)
            return self._rotar_izquierda(nodo)
        return nodo

    def eliminar(self, id_prod):
        """Elimina un producto por ID y rebalancea — O(log n)."""
        self._raiz = self._eliminar(self._raiz, id_prod)
        self._cantidad = self._contar(self._raiz)

    # ── Recorridos ───────────────────────────────────────────────────────────

    def _inorden(self, nodo, resultado):
        if nodo:
            self._inorden(nodo.izq, resultado)
            resultado.append(nodo.producto)
            self._inorden(nodo.der, resultado)

    def obtener_todos(self):
        """Recorrido en-orden: retorna productos ordenados por ID — O(n)."""
        resultado = []
        self._inorden(self._raiz, resultado)
        return resultado

    def _contar(self, nodo):
        return 0 if not nodo else 1 + self._contar(nodo.izq) + self._contar(nodo.der)

    # ── Información del árbol ─────────────────────────────────────────────────

    def altura_arbol(self):
        return self._altura(self._raiz)

    @property
    def tamaño(self):
        return self._contar(self._raiz)

    def obtener_estructura(self):
        """Retorna representación por niveles para visualizar en la GUI."""
        if not self._raiz:
            return []
        from collections import deque
        niveles = []
        cola = deque([(self._raiz, 0)])
        while cola:
            nodo, nivel = cola.popleft()
            if nivel == len(niveles):
                niveles.append([])
            niveles[nivel].append(f"[{nodo.clave}] fb={self._factor_balance(nodo):+d}")
            if nodo.izq:
                cola.append((nodo.izq, nivel + 1))
            if nodo.der:
                cola.append((nodo.der, nivel + 1))
        return niveles

    def __repr__(self):
        return f"ArbolAVL({self.tamaño} productos, altura={self.altura_arbol()})"
