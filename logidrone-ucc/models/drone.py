"""
Modelo de Dron — Entidad operativa de LogiDrone-UCC
=====================================================
Cada dron integra:
  • PilaLIFO   → historial de mantenimiento (último evento en la cima)
  • ListaDE    → secuencia de destinos del viaje actual (navegación bidireccional)
  • posición   → coordenadas píxel en el canvas para la animación
"""

import time
from structures.stack_lifo import PilaLIFO
from structures.doubly_linked_list import ListaDoblementeEncadenada

ESTADOS = ("disponible", "en_vuelo", "recargando", "mantenimiento", "baja_bateria")


class Dron:

    def __init__(self, id_dron: str, nombre: str, capacidad_kg: float = 5.0):
        self.id = id_dron
        self.nombre = nombre
        self.capacidad_kg = capacidad_kg
        self.bateria = 100.0
        self.estado = "disponible"
        self.nodo_actual = 0          # ID del nodo donde está (0 = Almacén)

        # Estructuras de datos propias
        self.historial = PilaLIFO()           # mantenimiento (LIFO)
        self.ruta_entrega = ListaDoblementeEncadenada()  # viaje actual (LDE)

        # Estado de animación en el canvas
        self.px: float = 0.0          # posición píxel X en el canvas
        self.py: float = 0.0          # posición píxel Y en el canvas
        self.route_ids: list = []     # IDs de nodos en la ruta A* actual
        self.route_idx: int = 0       # índice del próximo nodo destino
        self.pedido_actual = None     # objeto Pedido en curso

        # Registro de alta
        self._registrar("Alta del sistema", "Sistema",
                        f"Dron {nombre} registrado. Capacidad {capacidad_kg} kg.")

    # ── Mantenimiento (Pila) ─────────────────────────────────────────────────

    def registrar_mantenimiento(self, tipo: str, tecnico: str, notas: str = ""):
        """Apila un nuevo evento de mantenimiento — O(1)."""
        self._registrar(tipo, tecnico, notas)
        if tipo in ("Cambio de batería", "Recarga completa"):
            self.bateria = 100.0
            self.estado = "disponible"
        elif tipo == "Mantenimiento preventivo":
            self.estado = "mantenimiento"

    def ultimo_mantenimiento(self):
        """Consulta el evento más reciente sin extraerlo — O(1)."""
        return self.historial.ver_cima()

    def _registrar(self, tipo, tecnico, notas):
        self.historial.apilar({
            "tipo": tipo,
            "fecha": time.strftime("%d/%m/%Y %H:%M"),
            "tecnico": tecnico,
            "notas": notas,
        })

    # ── Ruta de entrega (Lista Doblemente Encadenada) ─────────────────────────

    def asignar_ruta(self, nodos_grafo: list):
        """
        Carga la ruta A* en la LDE del dron.
        nodos_grafo: lista de NodoGrafo en orden de visita.
        """
        self.ruta_entrega.limpiar()
        for n in nodos_grafo:
            self.ruta_entrega.insertar_al_final(n.nombre)

    def cambiar_destino(self, destino_viejo: str, destino_nuevo: str):
        """Actualiza un punto de la ruta sin recrear la LDE completa — O(n)."""
        if self.ruta_entrega.eliminar_por_valor(destino_viejo):
            # Inserta el nuevo destino al final (simplificación)
            self.ruta_entrega.insertar_al_final(destino_nuevo)
            return True
        return False

    # ── Batería / Estado ─────────────────────────────────────────────────────

    def consumir_bateria(self, cantidad: float):
        """Reduce la batería; cambia estado a 'baja_bateria' si cae < 20%."""
        self.bateria = max(0.0, self.bateria - cantidad)
        if self.bateria < 20.0 and self.estado == "en_vuelo":
            self.estado = "baja_bateria"

    def esta_disponible(self) -> bool:
        return self.estado == "disponible" and self.bateria > 20.0

    # ── Serialización ────────────────────────────────────────────────────────

    def to_dict(self):
        ult = self.ultimo_mantenimiento()
        return {
            "id": self.id,
            "nombre": self.nombre,
            "estado": self.estado,
            "bateria": round(self.bateria, 1),
            "capacidad_kg": self.capacidad_kg,
            "nodo": self.nodo_actual,
            "ultimo_mant": ult["tipo"] if ult else "N/A",
        }

    def __repr__(self):
        return f"Dron({self.id}, '{self.nombre}', {self.estado}, bat={self.bateria:.0f}%)"
