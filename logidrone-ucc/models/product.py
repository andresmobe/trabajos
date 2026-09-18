"""
Modelo de Producto — Ítem del Inventario (clave del Árbol AVL)
"""

CATEGORIAS = ("Medicamento", "Repuesto", "Documento", "Alimento", "Otro")


class Producto:
    """Producto de urgencia almacenado en el Árbol AVL."""

    def __init__(self, id_prod: int, nombre: str, categoria: str,
                 stock: int, peso_kg: float, precio: float = 0.0):
        self.id = id_prod          # clave única para el AVL
        self.nombre = nombre
        self.categoria = categoria
        self.stock = stock
        self.peso_kg = peso_kg     # peso por unidad en kg
        self.precio = precio

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "stock": self.stock,
            "peso_kg": self.peso_kg,
            "precio": self.precio,
        }

    def __repr__(self):
        return f"Producto({self.id}, '{self.nombre}', stock={self.stock})"
