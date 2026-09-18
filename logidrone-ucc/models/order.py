"""
Modelo de Pedido — Solicitud de Entrega (elemento de la Cola FIFO)
"""

import time

PRIORIDADES = {1: "Normal", 2: "Urgente", 3: "Crítico"}


class Pedido:
    """Solicitud de entrega que vive en la Cola FIFO hasta ser despachada."""

    def __init__(self, id_pedido: int, id_producto: int, cantidad: int,
                 destino_id: int, destino_nombre: str,
                 solicitante: str = "", prioridad: int = 1,
                 origen_id: int = 0, origen_nombre: str = "Almacén Central"):
        self.id = id_pedido
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.destino_id = destino_id
        self.destino_nombre = destino_nombre
        self.origen_id = origen_id
        self.origen_nombre = origen_nombre
        self.solicitante = solicitante
        self.prioridad = prioridad
        self.estado = "pendiente"   # pendiente | en_proceso | entregado | cancelado
        self.fecha_creacion = time.strftime("%d/%m %H:%M")
        self.fecha_entrega = None
        self.dron_asignado = None
        self.ruta_calculada = []    # lista de nombres de nodo (para mostrar en GUI)

    def marcar_en_proceso(self, id_dron: str, ruta: list):
        self.estado = "en_proceso"
        self.dron_asignado = id_dron
        self.ruta_calculada = ruta

    def marcar_entregado(self):
        self.estado = "entregado"
        self.fecha_entrega = time.strftime("%d/%m %H:%M")

    def to_dict(self):
        return {
            "id": f"P{self.id:03d}",
            "producto_id": self.id_producto,
            "cantidad": self.cantidad,
            "destino": self.destino_nombre,
            "solicitante": self.solicitante,
            "prioridad": PRIORIDADES.get(self.prioridad, "Normal"),
            "estado": self.estado,
            "fecha": self.fecha_creacion,
            "dron": self.dron_asignado or "—",
        }

    def __repr__(self):
        return (
            f"Pedido(P{self.id:03d}, dest='{self.destino_nombre}', "
            f"prio={self.prioridad}, estado={self.estado})"
        )
