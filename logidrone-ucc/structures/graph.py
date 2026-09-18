"""
Grafo + Algoritmo A* — Mapa Aéreo de Santa Marta
=================================================
Los nodos representan puntos clave (almacén, zonas de entrega, recargas).
Las aristas son rutas aéreas con su distancia en kilómetros.

A* (Hart, Nilsson y Raphael, 1968):
  f(n) = g(n) + h(n)
    g(n) = costo acumulado real desde el origen
    h(n) = heurística admisible (distancia euclidiana al destino)
  Garantiza la ruta ÓPTIMA más rápida que Dijkstra cuando h es admisible.
  Evita automáticamente los nodos marcados como 'excluido' (cono del
  Aeropuerto Internacional Simón Bolívar).
"""

import heapq
import math


class NodoGrafo:
    """Nodo del grafo: punto geográfico con posición en el canvas."""

    def __init__(self, id_nodo, nombre, x, y, tipo="entrega"):
        self.id = id_nodo
        self.nombre = nombre
        self.x = x                 # posición en el canvas (píxeles)
        self.y = y
        self.tipo = tipo           # almacen | entrega | recarga | excluido
        self.excluido = (tipo == "excluido")
        self.vecinos = []          # lista de (NodoGrafo, peso_km)

    def agregar_vecino(self, nodo, peso):
        self.vecinos.append((nodo, peso))

    def distancia_a(self, otro):
        """Distancia euclidiana en píxeles (heurística para A*)."""
        return math.hypot(self.x - otro.x, self.y - otro.y)

    def __lt__(self, otro):
        return self.id < otro.id

    def __repr__(self):
        return f"Nodo({self.id}, '{self.nombre}', tipo={self.tipo})"


class GrafoSantaMarta:
    """
    Grafo no-dirigido que modela el espacio aéreo sobre Santa Marta.
    Inicializado con la topología real de la ciudad.
    """

    # Posiciones en el canvas 800×460 — geografía real de Santa Marta
    # Oeste (izquierda) = Mar Caribe / Bahía  |  Este (derecha) = Sierra Nevada
    _NODOS_CONFIG = [
        #  id   nombre                    x    y    tipo
        (0,  "Almacén Central",          455, 255, "almacen"),  # zona industrial, interior
        (1,  "Centro Histórico",         292, 228, "entrega"),  # ciudad amurallada, frente al mar
        (2,  "El Rodadero",              210, 390, "entrega"),  # playa turística al sur
        (3,  "Taganga",                  232,  90, "entrega"),  # pueblo pesquero al norte
        (4,  "Zona Hotelera",            222, 320, "entrega"),  # franja hotelera costera
        (5,  "Recarga Norte",            182, 158, "recarga"),  # zona norte, cerca Taganga
        (6,  "Recarga Sur",              325, 415, "recarga"),  # sur, cerca El Rodadero
        (7,  "Puerto / Bahía",           130, 218, "entrega"),  # muelle principal, Bahía
        (8,  "Aeropuerto*",              598,  68, "excluido"), # Simón Bolívar, NE excluido
    ]

    # Aristas: (id_a, id_b, distancia_km) — rutas aéreas reales aproximadas
    _ARISTAS_CONFIG = [
        (0, 1, 3.5),   # Almacén ↔ Centro Histórico
        (0, 5, 6.8),   # Almacén ↔ Recarga Norte
        (0, 6, 5.0),   # Almacén ↔ Recarga Sur
        (1, 7, 1.8),   # Centro ↔ Puerto / Bahía
        (1, 3, 4.2),   # Centro ↔ Taganga
        (1, 4, 3.2),   # Centro ↔ Zona Hotelera
        (1, 2, 6.0),   # Centro ↔ El Rodadero
        (1, 5, 3.8),   # Centro ↔ Recarga Norte
        (2, 4, 2.8),   # El Rodadero ↔ Zona Hotelera
        (2, 6, 3.5),   # El Rodadero ↔ Recarga Sur
        (3, 5, 2.2),   # Taganga ↔ Recarga Norte
        (3, 7, 4.8),   # Taganga ↔ Puerto / Bahía
        (4, 7, 3.0),   # Zona Hotelera ↔ Puerto / Bahía
    ]

    def __init__(self):
        self.nodos: dict[int, NodoGrafo] = {}
        self._inicializar()

    def _inicializar(self):
        for id_n, nombre, x, y, tipo in self._NODOS_CONFIG:
            self.nodos[id_n] = NodoGrafo(id_n, nombre, x, y, tipo)

        aristas_vistas = set()
        for a, b, peso in self._ARISTAS_CONFIG:
            par = (min(a, b), max(a, b))
            if par in aristas_vistas:
                continue
            aristas_vistas.add(par)
            na = self.nodos[a]
            nb = self.nodos[b]
            na.agregar_vecino(nb, peso)
            nb.agregar_vecino(na, peso)

    # ── A* ───────────────────────────────────────────────────────────────────

    def a_estrella(self, id_origen: int, id_destino: int):
        """
        Algoritmo A* — encuentra la ruta óptima evitando zonas excluidas.

        Returns:
            (ruta: list[NodoGrafo], costo_km: float)
            Si no existe ruta retorna ([], inf).
        """
        if id_origen not in self.nodos or id_destino not in self.nodos:
            return [], float("inf")
        if id_origen == id_destino:
            return [self.nodos[id_origen]], 0.0

        origen = self.nodos[id_origen]
        destino = self.nodos[id_destino]

        # g[n] = costo real acumulado hasta n
        g = {id_origen: 0.0}
        # h(n) = distancia euclidiana al destino (admisible, no sobreestima)
        h = lambda n: n.distancia_a(destino) * 0.008  # px → km aprox
        # f(n) = g(n) + h(n)
        contador = 0  # desempate en la cola de prioridad
        cola = [(h(origen), contador, origen)]
        padre = {id_origen: None}
        visitados = set()

        while cola:
            _, _, actual = heapq.heappop(cola)

            if actual.id in visitados:
                continue
            visitados.add(actual.id)

            if actual.id == id_destino:
                return self._reconstruir_ruta(padre, id_destino), g[id_destino]

            for vecino, peso in actual.vecinos:
                if vecino.excluido or vecino.id in visitados:
                    continue
                g_nuevo = g[actual.id] + peso
                if vecino.id not in g or g_nuevo < g[vecino.id]:
                    g[vecino.id] = g_nuevo
                    padre[vecino.id] = actual.id
                    f = g_nuevo + h(vecino)
                    contador += 1
                    heapq.heappush(cola, (f, contador, vecino))

        return [], float("inf")  # no hay ruta disponible

    def _reconstruir_ruta(self, padre, id_actual):
        ruta = []
        while id_actual is not None:
            ruta.append(self.nodos[id_actual])
            id_actual = padre[id_actual]
        ruta.reverse()
        return ruta

    # ── Utilidades ───────────────────────────────────────────────────────────

    def agregar_nodo(self, id_n, nombre, x, y, tipo="entrega"):
        self.nodos[id_n] = NodoGrafo(id_n, nombre, x, y, tipo)

    def agregar_arista(self, id_a, id_b, peso):
        if id_a in self.nodos and id_b in self.nodos:
            self.nodos[id_a].agregar_vecino(self.nodos[id_b], peso)
            self.nodos[id_b].agregar_vecino(self.nodos[id_a], peso)

    def obtener_aristas(self):
        """Retorna lista de (NodoGrafo, NodoGrafo, peso) sin duplicados."""
        vistas = set()
        aristas = []
        for nodo in self.nodos.values():
            for vecino, peso in nodo.vecinos:
                par = (min(nodo.id, vecino.id), max(nodo.id, vecino.id))
                if par not in vistas:
                    vistas.add(par)
                    aristas.append((nodo, vecino, peso))
        return aristas

    def __repr__(self):
        return (
            f"GrafoSantaMarta({len(self.nodos)} nodos, "
            f"{len(self.obtener_aristas())} aristas)"
        )
