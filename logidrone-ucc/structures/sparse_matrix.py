"""
Matriz Dispersa — Grilla de Monitoreo del Espacio Aéreo
=========================================================
Modela una cuadrícula geográfica sobre la Bahía de Santa Marta.
Cada celda (fila, columna) representa un sector del espacio aéreo.
Solo se almacenan las celdas OCUPADAS, ahorrando memoria frente a una
matriz densa (la mayor parte del cielo estará vacía).

Estructura interna: listas enlazadas por fila y por columna (Cruz Ortogonal).
  insertar(f, c, id_dron)  → registra un dron en esa coordenada
  eliminar(f, c)           → libera la celda cuando el dron se mueve
  obtener(f, c)            → consulta qué dron ocupa la celda
  esta_ocupada(f, c)       → True si hay colisión potencial
"""


class NodoMatriz:
    """Nodo de memoria dinámica que vive a la vez en una lista-fila y una lista-columna."""

    def __init__(self, fila, col, valor):
        self.fila = fila
        self.col = col
        self.valor = valor          # ID del dron que ocupa esta celda
        self.sig_fila = None        # siguiente nodo en la misma fila
        self.sig_col = None         # siguiente nodo en la misma columna


class MatrizDispersa:
    """
    Matriz dispersa de monitoreo aéreo usando listas enlazadas cruzadas.
    Dimensiones: filas × columnas representan la cuadrícula geográfica.
    """

    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        # Cabeceras de fila y columna — apuntan al primer nodo no-nulo de cada línea
        self._cab_filas = [None] * filas
        self._cab_cols = [None] * columnas
        self._elementos = 0

    # ── Operaciones principales ──────────────────────────────────────────────

    def insertar(self, fila, col, valor):
        """Registra un dron en (fila, col) — O(columnas + filas)."""
        self._validar(fila, col)
        existente = self._buscar_nodo(fila, col)
        if existente:
            existente.valor = valor
            return

        nuevo = NodoMatriz(fila, col, valor)

        # Insertar ordenado en la lista de la fila
        if not self._cab_filas[fila] or col < self._cab_filas[fila].col:
            nuevo.sig_fila = self._cab_filas[fila]
            self._cab_filas[fila] = nuevo
        else:
            act = self._cab_filas[fila]
            while act.sig_fila and act.sig_fila.col < col:
                act = act.sig_fila
            nuevo.sig_fila = act.sig_fila
            act.sig_fila = nuevo

        # Insertar ordenado en la lista de la columna
        if not self._cab_cols[col] or fila < self._cab_cols[col].fila:
            nuevo.sig_col = self._cab_cols[col]
            self._cab_cols[col] = nuevo
        else:
            act = self._cab_cols[col]
            while act.sig_col and act.sig_col.fila < fila:
                act = act.sig_col
            nuevo.sig_col = act.sig_col
            act.sig_col = nuevo

        self._elementos += 1

    def eliminar(self, fila, col):
        """Libera la celda (fila, col) — O(columnas + filas)."""
        self._validar(fila, col)

        # Quitar de la lista de la fila
        if not self._cab_filas[fila]:
            return False
        if self._cab_filas[fila].col == col:
            self._cab_filas[fila] = self._cab_filas[fila].sig_fila
        else:
            act = self._cab_filas[fila]
            while act.sig_fila and act.sig_fila.col != col:
                act = act.sig_fila
            if not act.sig_fila:
                return False
            act.sig_fila = act.sig_fila.sig_fila

        # Quitar de la lista de la columna
        if not self._cab_cols[col]:
            self._elementos -= 1
            return True
        if self._cab_cols[col].fila == fila:
            self._cab_cols[col] = self._cab_cols[col].sig_col
        else:
            act = self._cab_cols[col]
            while act.sig_col and act.sig_col.fila != fila:
                act = act.sig_col
            if act.sig_col:
                act.sig_col = act.sig_col.sig_col

        self._elementos -= 1
        return True

    def obtener(self, fila, col):
        """Retorna el ID del dron en (fila, col) o None si está vacía."""
        nodo = self._buscar_nodo(fila, col)
        return nodo.valor if nodo else None

    def esta_ocupada(self, fila, col):
        """True si la celda está ocupada (riesgo de colisión)."""
        return self._buscar_nodo(fila, col) is not None

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _buscar_nodo(self, fila, col):
        act = self._cab_filas[fila]
        while act:
            if act.col == col:
                return act
            act = act.sig_fila
        return None

    def _validar(self, fila, col):
        if not (0 <= fila < self.filas and 0 <= col < self.columnas):
            raise IndexError(
                f"Coordenada ({fila},{col}) fuera del espacio aéreo "
                f"({self.filas}x{self.columnas})"
            )

    # ── Consultas globales ────────────────────────────────────────────────────

    def obtener_ocupados(self):
        """Lista de (fila, col, valor) de todas las celdas ocupadas."""
        resultado = []
        for f in range(self.filas):
            act = self._cab_filas[f]
            while act:
                resultado.append((act.fila, act.col, act.valor))
                act = act.sig_fila
        return resultado

    def limpiar_dron(self, id_dron):
        """Elimina todas las celdas ocupadas por un dron específico."""
        celdas = [(f, c) for f, c, v in self.obtener_ocupados() if v == id_dron]
        for f, c in celdas:
            self.eliminar(f, c)

    @property
    def elementos(self):
        return self._elementos

    def __repr__(self):
        return (
            f"MatrizDispersa({self.filas}x{self.columnas}, "
            f"{self._elementos} celdas ocupadas)"
        )
