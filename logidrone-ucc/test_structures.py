# -*- coding: utf-8 -*-
"""Prueba rápida de todas las estructuras de datos."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from structures.queue_fifo import ColaFIFO
from structures.stack_lifo import PilaLIFO
from structures.doubly_linked_list import ListaDoblementeEncadenada
from structures.avl_tree import ArbolAVL
from structures.sparse_matrix import MatrizDispersa
from structures.graph import GrafoSantaMarta
from models.drone import Dron
from models.order import Pedido
from models.product import Producto

def ok(name):
    print(f"  [OK] {name}")

print("=== LogiDrone-UCC — Test de Estructuras ===\n")

# 1. Cola FIFO
cola = ColaFIFO()
cola.encolar("A"); cola.encolar("B"); cola.encolar("C")
assert cola.desencolar() == "A"
assert cola.ver_frente() == "B"
assert len(cola) == 2
ok("Cola FIFO")

# 2. Pila LIFO
pila = PilaLIFO()
pila.apilar({"tipo": "Limpieza"}); pila.apilar({"tipo": "Recarga"})
assert pila.ver_cima()["tipo"] == "Recarga"
assert pila.desapilar()["tipo"] == "Recarga"
assert pila.ver_cima()["tipo"] == "Limpieza"
ok("Pila LIFO")

# 3. Lista Doblemente Encadenada
lde = ListaDoblementeEncadenada()
for x in ["Almacen", "Centro", "Taganga"]:
    lde.insertar_al_final(x)
assert lde.recorrer_adelante() == ["Almacen", "Centro", "Taganga"]
assert lde.recorrer_atras() == ["Taganga", "Centro", "Almacen"]
lde.eliminar_por_valor("Centro")
assert lde.recorrer_adelante() == ["Almacen", "Taganga"]
ok("Lista Doblemente Encadenada")

# 4. Arbol AVL
avl = ArbolAVL()
for i in [5, 3, 7, 1, 4, 6, 8]:
    avl.insertar(Producto(i, f"Prod{i}", "Medicamento", 10, 0.1))
assert avl.buscar(4) is not None
assert avl.buscar(99) is None
assert avl.altura_arbol() <= 4
todos = avl.obtener_todos()
ids = [p.id for p in todos]
assert ids == sorted(ids), "AVL inorden debe ser ordenado"
avl.eliminar(3)
assert avl.buscar(3) is None
ok(f"Arbol AVL (h={avl.altura_arbol()}, n={avl.tamaño})")

# 5. Matriz Dispersa
mat = MatrizDispersa(16, 20)
mat.insertar(3, 5, "D001")
mat.insertar(7, 12, "D002")
assert mat.obtener(3, 5) == "D001"
assert mat.esta_ocupada(7, 12)
assert mat.elementos == 2
mat.eliminar(3, 5)
assert mat.obtener(3, 5) is None
assert mat.elementos == 1
ok("Matriz Dispersa")

# 6. Grafo + A*
grafo = GrafoSantaMarta()
ruta, costo = grafo.a_estrella(0, 2)  # Almacen -> El Rodadero
assert len(ruta) > 0
assert costo < float("inf")
assert ruta[0].id == 0
assert ruta[-1].id == 2
ruta_names = " -> ".join(n.nombre for n in ruta)
# Verificar que NO pasa por el nodo excluido (aeropuerto = id 8)
ids_ruta = [n.id for n in ruta]
assert 8 not in ids_ruta, "A* no debe pasar por zona excluida"
ok(f"Grafo + A* ({ruta_names}, {costo:.1f} km)")

# 7. Modelos integrados con estructuras
dron = Dron("D001", "Condor-1", 5.0)
dron.registrar_mantenimiento("Limpieza de salitre", "Tec. Perez", "Post-vuelo")
assert dron.historial.ver_cima()["tipo"] == "Limpieza de salitre"
ruta_obj, _ = grafo.a_estrella(0, 3)
dron.asignar_ruta(ruta_obj)
nombres = dron.ruta_entrega.recorrer_adelante()
assert nombres[0] == "Almacén Central"
ok("Modelo Dron (Pila + LDE)")

pedido = Pedido(1, 101, 2, 3, "Taganga", "Juan", 2)
assert pedido.estado == "pendiente"
pedido.marcar_en_proceso("D001", nombres)
assert pedido.estado == "en_proceso"
ok("Modelo Pedido")

print()
print("=== TODAS LAS PRUEBAS PASARON CORRECTAMENTE ===")
