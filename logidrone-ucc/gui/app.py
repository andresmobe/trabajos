"""
LogiDrone-UCC — Aplicación Principal (GUI)
==========================================
Panel de control con mapa interactivo, animación de drones en tiempo real
y formularios para gestionar todas las estructuras de datos.

Estructuras activas:
  Cola FIFO      → cola de pedidos pendientes
  Pila LIFO      → historial de mantenimiento por dron
  Lista DE       → secuencia de destinos del viaje
  Árbol AVL      → inventario de productos
  Matriz Dispersa → monitoreo del espacio aéreo
  Grafo + A*     → cálculo de rutas óptimas
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import math

from structures.queue_fifo import ColaFIFO
from structures.avl_tree import ArbolAVL
from structures.sparse_matrix import MatrizDispersa
from structures.graph import GrafoSantaMarta
from models.drone import Dron
from models.order import Pedido
from models.product import Producto
from gui.dialogs import (
    NuevoDronDialog, NuevoPedidoDialog, NuevoProductoDialog,
    MantenimientoDialog, HistorialDronDialog, HistorialGeneralDialog,
    InventarioDialog, BuscarProductoDialog, ActualizarStockDialog,
    DetalleNodoDialog, ColaPedidosDialog, RutaDronDialog, DespacharDialog,
)

# ── Paleta de colores ────────────────────────────────────────────────────────
BG       = "#0d1117"
PANEL    = "#161b22"
CARD     = "#21262d"
BORDER   = "#30363d"
TEXT     = "#c9d1d9"
DIM      = "#8b949e"
ACCENT   = "#238636"
WARNING  = "#d29922"
DANGER   = "#da3633"
INFO     = "#388bfd"
TITLE    = "#f0f6fc"

# ── Colores del mapa ─────────────────────────────────────────────────────────
MAP_BG   = "#0a1628"
SEA_CLR  = "#0d2137"
LAND_CLR = "#0d1f15"
GRID_CLR = "#0f2040"

NODE_CLR = {
    "almacen":  "#06d6a0",
    "entrega":  "#58a6ff",
    "recarga":  "#3fb950",
    "excluido": "#f85149",
}
EDGE_CLR     = "#2d4a6a"
EDGE_HL      = "#ffd700"   # ruta A* resaltada
EXCL_CLR     = "#f8514918" # zona exclusión (semitransparente simulado con overlay)

DRONE_CLR = {
    "disponible":    "#ffd700",
    "en_vuelo":      "#ff7b00",
    "baja_bateria":  "#ff3333",
    "recargando":    "#00ffcc",
    "mantenimiento": "#cc66ff",
}

# ── Dimensiones ──────────────────────────────────────────────────────────────
MAP_W, MAP_H = 800, 460
NR = 16                    # filas de la matriz dispersa
NC = 20                    # columnas de la matriz dispersa
NODE_R   = 16              # radio de los nodos en el canvas
DRONE_R  = 9               # radio del icono de dron
DRONE_SPEED = 3.5          # píxeles por tick de animación
ANIM_MS  = 50              # ms entre frames (≈20 fps)
BAT_COST = 0.12            # % batería consumida por tick de vuelo


class LogiDroneApp:
    """Controlador principal de la aplicación LogiDrone-UCC."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LogiDrone-UCC  —  Operación Bahía Santa Marta")
        self.root.geometry("1220x720")
        self.root.configure(bg=BG)
        self.root.minsize(1100, 660)

        # ── Estructuras de datos del sistema ────────────────────────────────
        self.cola_pedidos: ColaFIFO = ColaFIFO()
        self.inventario:   ArbolAVL = ArbolAVL()
        self.mapa:         GrafoSantaMarta = GrafoSantaMarta()
        self.espacio_aereo: MatrizDispersa = MatrizDispersa(NR, NC)

        self.drones:    dict[str, Dron]   = {}
        self.entregados: list[Pedido]     = []
        self.alertas:   list[str]         = []

        self._contador_drones   = 0
        self._contador_pedidos  = 0
        self._contador_prods    = 100   # IDs de productos empiezan en 100

        # Estado de visualización
        self._nodo_sel = None            # nodo seleccionado al hacer clic
        self._tick: int = 0              # contador para animaciones (pulso)

        self._setup_styles()
        self._build_ui()
        self._load_sample_data()
        self._draw_static_map()
        self._animation_tick()

    # ────────────────────────────────────────────────────────────────────────
    # Estilos ttk
    # ────────────────────────────────────────────────────────────────────────

    def _setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("Dark.Treeview",
                        background=CARD, fieldbackground=CARD,
                        foreground=TEXT, rowheight=24,
                        font=("Segoe UI", 9))
        style.configure("Dark.Treeview.Heading",
                        background=PANEL, foreground=DIM,
                        font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Dark.Treeview",
                  background=[("selected", "#1f3a5f")],
                  foreground=[("selected", TITLE)])

        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=CARD, foreground=DIM,
                        font=("Segoe UI", 9, "bold"),
                        padding=[12, 5])
        style.map("TNotebook.Tab",
                  background=[("selected", PANEL)],
                  foreground=[("selected", TEXT)])

        style.configure("Vertical.TScrollbar",
                        background=CARD, troughcolor=BG,
                        borderwidth=0, arrowcolor=DIM)

    # ────────────────────────────────────────────────────────────────────────
    # Construcción de la UI
    # ────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_left_panel(body)
        self._build_map_panel(body)
        self._build_status_bar()
        self._build_menu()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg="#0a0f1a", height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="✈  LogiDrone-UCC", bg="#0a0f1a", fg=TITLE,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=20, pady=8)
        tk.Label(hdr, text="Operación Bahía Santa Marta", bg="#0a0f1a", fg=DIM,
                 font=("Segoe UI", 11)).pack(side="left", padx=0)

        self.lbl_hora = tk.Label(hdr, text="", bg="#0a0f1a", fg=DIM,
                                 font=("Segoe UI", 10))
        self.lbl_hora.pack(side="right", padx=20)

    def _build_left_panel(self, parent):
        lp = tk.Frame(parent, bg=PANEL, width=295)
        lp.pack(side="left", fill="y", padx=(2, 0), pady=2)
        lp.pack_propagate(False)

        # Notebook
        nb = ttk.Notebook(lp, style="TNotebook")
        nb.pack(fill="both", expand=True, padx=6, pady=6)

        # Tab Drones
        self._tab_drones = tk.Frame(nb, bg=BG)
        nb.add(self._tab_drones, text="Drones")
        self._build_tab_drones()

        # Tab Pedidos
        self._tab_ped = tk.Frame(nb, bg=BG)
        nb.add(self._tab_ped, text="Cola")
        self._build_tab_pedidos()

        # Tab Inventario
        self._tab_inv = tk.Frame(nb, bg=BG)
        nb.add(self._tab_inv, text="AVL")
        self._build_tab_inventario()

        # Tab Espacio Aéreo
        self._tab_mat = tk.Frame(nb, bg=BG)
        nb.add(self._tab_mat, text="Aéreo")
        self._build_tab_matriz()

        # Tab Mantenimientos
        self._tab_mant = tk.Frame(nb, bg=BG)
        nb.add(self._tab_mant, text="Mant.")
        self._build_tab_mantenimientos()

        # Botones de acción
        acts = tk.Frame(lp, bg=PANEL, pady=6)
        acts.pack(fill="x", padx=6)
        self._btn_despachar = tk.Button(
            acts, text="▶  Despachar Dron",
            command=self._cmd_despachar,
            bg=ACCENT, fg=TITLE, font=("Segoe UI", 10, "bold"),
            relief="flat", pady=7, cursor="hand2",
            activebackground="#2ea043", activeforeground=TITLE
        )
        self._btn_despachar.pack(fill="x", pady=(0, 4))

        tk.Button(acts, text="Registrar Mantenimiento",
                  command=self._cmd_mantenimiento,
                  bg=CARD, fg=TEXT, font=("Segoe UI", 9),
                  relief="flat", pady=5, cursor="hand2"
                  ).pack(fill="x")

    def _build_tab_drones(self):
        f = self._tab_drones
        tk.Label(f, text="Flota activa", bg=BG, fg=DIM,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=6, pady=(4, 0))

        cols = ("nombre", "estado", "bat")
        self._tree_drones = ttk.Treeview(f, columns=cols, show="headings",
                                          height=10, style="Dark.Treeview")
        for c, h, w in zip(cols, ("Dron", "Estado", "Bat %"), (110, 90, 50)):
            self._tree_drones.heading(c, text=h)
            self._tree_drones.column(c, width=w, anchor="w" if c == "nombre" else "center")
        self._tree_drones.pack(fill="both", expand=True, padx=4, pady=4)
        self._tree_drones.bind("<Double-1>", self._on_dron_doble_click)

        tk.Button(f, text="+ Nuevo Dron",
                  command=self._cmd_nuevo_dron,
                  bg=CARD, fg=INFO, font=("Segoe UI", 9),
                  relief="flat", pady=4, cursor="hand2"
                  ).pack(fill="x", padx=4, pady=(0, 4))

    def _build_tab_pedidos(self):
        f = self._tab_ped
        self.lbl_cola_info = tk.Label(f, text="Cola FIFO  (0 pendientes)",
                                       bg=BG, fg=DIM, font=("Segoe UI", 8))
        self.lbl_cola_info.pack(anchor="w", padx=6, pady=(4, 0))

        cols = ("id", "destino", "prio")
        self._tree_ped = ttk.Treeview(f, columns=cols, show="headings",
                                       height=10, style="Dark.Treeview")
        for c, h, w in zip(cols, ("Pedido", "Destino", "Prior."), (55, 115, 60)):
            self._tree_ped.heading(c, text=h)
            self._tree_ped.column(c, width=w, anchor="center" if c in ("id","prio") else "w")
        self._tree_ped.pack(fill="both", expand=True, padx=4, pady=4)

        btnf = tk.Frame(f, bg=BG)
        btnf.pack(fill="x", padx=4, pady=(0, 4))
        tk.Button(btnf, text="+ Pedido",
                  command=self._cmd_nuevo_pedido,
                  bg=CARD, fg=INFO, font=("Segoe UI", 9),
                  relief="flat", pady=4, cursor="hand2"
                  ).pack(side="left", fill="x", expand=True, padx=(0, 2))
        tk.Button(btnf, text="Ver Cola",
                  command=self._cmd_ver_cola,
                  bg=CARD, fg=DIM, font=("Segoe UI", 9),
                  relief="flat", pady=4, cursor="hand2"
                  ).pack(side="left", fill="x", expand=True)

    def _build_tab_inventario(self):
        f = self._tab_inv
        self.lbl_inv_info = tk.Label(f, text="Árbol AVL  (0 productos)",
                                      bg=BG, fg=DIM, font=("Segoe UI", 8))
        self.lbl_inv_info.pack(anchor="w", padx=6, pady=(4, 0))

        cols = ("id", "nombre", "stock")
        self._tree_inv = ttk.Treeview(f, columns=cols, show="headings",
                                       height=10, style="Dark.Treeview")
        for c, h, w in zip(cols, ("ID", "Nombre", "Stock"), (40, 140, 50)):
            self._tree_inv.heading(c, text=h)
            self._tree_inv.column(c, width=w, anchor="center" if c in ("id","stock") else "w")
        self._tree_inv.pack(fill="both", expand=True, padx=4, pady=4)

        btnf = tk.Frame(f, bg=BG)
        btnf.pack(fill="x", padx=4, pady=(0, 2))
        tk.Button(btnf, text="+ Nuevo",
                  command=self._cmd_nuevo_producto,
                  bg=CARD, fg=INFO, font=("Segoe UI", 9),
                  relief="flat", pady=4, cursor="hand2"
                  ).pack(side="left", fill="x", expand=True, padx=(0, 2))
        tk.Button(btnf, text="+ Stock",
                  command=self._cmd_actualizar_stock,
                  bg=CARD, fg="#3fb950", font=("Segoe UI", 9),
                  relief="flat", pady=4, cursor="hand2"
                  ).pack(side="left", fill="x", expand=True, padx=(0, 2))
        tk.Button(btnf, text="Buscar",
                  command=self._cmd_buscar_producto,
                  bg=CARD, fg=DIM, font=("Segoe UI", 9),
                  relief="flat", pady=4, cursor="hand2"
                  ).pack(side="left", fill="x", expand=True)
        tk.Button(f, text="Ver Inventario Completo",
                  command=self._cmd_ver_inventario,
                  bg=CARD, fg=DIM, font=("Segoe UI", 9),
                  relief="flat", pady=4, cursor="hand2"
                  ).pack(fill="x", padx=4, pady=(0, 4))

    def _build_tab_mantenimientos(self):
        f = self._tab_mant
        tk.Label(f, text="Último registro por dron (cima de la pila)",
                 bg=BG, fg=DIM, font=("Segoe UI", 8)).pack(anchor="w", padx=6, pady=(4, 0))

        cols = ("dron", "tipo", "fecha")
        self._tree_mant = ttk.Treeview(f, columns=cols, show="headings",
                                        height=8, style="Dark.Treeview")
        for c, h, w in zip(cols, ("Dron", "Último Tipo", "Fecha"), (75, 125, 90)):
            self._tree_mant.heading(c, text=h)
            self._tree_mant.column(c, width=w, anchor="w")
        self._tree_mant.pack(fill="both", expand=True, padx=4, pady=4)

        self.lbl_mant_total = tk.Label(f, text="", bg=BG, fg=DIM,
                                        font=("Segoe UI", 8))
        self.lbl_mant_total.pack(anchor="w", padx=6)

        btnf = tk.Frame(f, bg=BG)
        btnf.pack(fill="x", padx=4, pady=(2, 4))
        tk.Button(btnf, text="+ Registrar",
                  command=self._cmd_mantenimiento,
                  bg=CARD, fg=WARNING, font=("Segoe UI", 9),
                  relief="flat", pady=4, cursor="hand2"
                  ).pack(side="left", fill="x", expand=True, padx=(0, 2))
        tk.Button(btnf, text="Ver Historial",
                  command=self._cmd_historial_general,
                  bg=CARD, fg=INFO, font=("Segoe UI", 9),
                  relief="flat", pady=4, cursor="hand2"
                  ).pack(side="left", fill="x", expand=True)

    def _build_tab_matriz(self):
        f = self._tab_mat
        tk.Label(f, text="Matriz Dispersa 16×20  (espacio aéreo)",
                 bg=BG, fg=DIM, font=("Segoe UI", 8)).pack(anchor="w", padx=6, pady=(4, 0))
        self.txt_matriz = tk.Text(f, bg=CARD, fg="#58a6ff",
                                   font=("Consolas", 7), relief="flat",
                                   state="disabled", width=34)
        self.txt_matriz.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_map_panel(self, parent):
        mp = tk.Frame(parent, bg=BG)
        mp.pack(side="left", fill="both", expand=True, padx=2, pady=2)

        hdr = tk.Frame(mp, bg=PANEL, height=32)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="MAPA AÉREO — SANTA MARTA", bg=PANEL, fg=DIM,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=12, pady=6)
        self.lbl_nodo_info = tk.Label(hdr, text="Haz clic en un nodo para ver detalles",
                                       bg=PANEL, fg=DIM, font=("Segoe UI", 9))
        self.lbl_nodo_info.pack(side="left", padx=10)

        # Leyenda
        ley_f = tk.Frame(hdr, bg=PANEL)
        ley_f.pack(side="right", padx=10)
        for label, color in [("Almacén", "#06d6a0"), ("Entrega", "#58a6ff"),
                              ("Recarga", "#3fb950"), ("Excluido", "#f85149")]:
            tk.Canvas(ley_f, width=10, height=10, bg=color, bd=0,
                      highlightthickness=0).pack(side="left", pady=10)
            tk.Label(ley_f, text=f" {label}  ", bg=PANEL, fg=DIM,
                     font=("Segoe UI", 8)).pack(side="left")

        # Canvas del mapa
        canvas_frame = tk.Frame(mp, bg="#090d14")
        canvas_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.canvas = tk.Canvas(canvas_frame, bg=MAP_BG, bd=0,
                                highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_map_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _build_status_bar(self):
        sb = tk.Frame(self.root, bg="#090d14", height=30)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)

        self.lbl_status = tk.Label(sb, text="Sistema iniciado — LogiDrone-UCC listo.",
                                    bg="#090d14", fg=ACCENT, font=("Segoe UI", 9))
        self.lbl_status.pack(side="left", padx=12, pady=5)

        self.lbl_stats = tk.Label(sb, text="", bg="#090d14", fg=DIM, font=("Segoe UI", 9))
        self.lbl_stats.pack(side="right", padx=12)

    def _build_menu(self):
        menu = tk.Menu(self.root, bg=PANEL, fg=TEXT, activebackground=CARD,
                       activeforeground=TITLE, relief="flat", tearoff=0)
        self.root.configure(menu=menu)

        m_drones = tk.Menu(menu, bg=PANEL, fg=TEXT, tearoff=0)
        menu.add_cascade(label="Drones", menu=m_drones)
        m_drones.add_command(label="Nuevo Dron", command=self._cmd_nuevo_dron)
        m_drones.add_separator()
        m_drones.add_command(label="Registrar Mantenimiento", command=self._cmd_mantenimiento)
        m_drones.add_command(label="Historial General de Mantenimientos", command=self._cmd_historial_general)
        m_drones.add_separator()
        m_drones.add_command(label="Despachar (A*)", command=self._cmd_despachar)

        m_ped = tk.Menu(menu, bg=PANEL, fg=TEXT, tearoff=0)
        menu.add_cascade(label="Pedidos", menu=m_ped)
        m_ped.add_command(label="Nuevo Pedido", command=self._cmd_nuevo_pedido)
        m_ped.add_command(label="Ver Cola FIFO", command=self._cmd_ver_cola)

        m_inv = tk.Menu(menu, bg=PANEL, fg=TEXT, tearoff=0)
        menu.add_cascade(label="Inventario", menu=m_inv)
        m_inv.add_command(label="Agregar Producto nuevo (AVL)", command=self._cmd_nuevo_producto)
        m_inv.add_command(label="Actualizar Stock producto existente", command=self._cmd_actualizar_stock)
        m_inv.add_command(label="Buscar por ID — O(log n)", command=self._cmd_buscar_producto)
        m_inv.add_command(label="Ver Inventario Completo", command=self._cmd_ver_inventario)

        m_sim = tk.Menu(menu, bg=PANEL, fg=TEXT, tearoff=0)
        menu.add_cascade(label="Simulación", menu=m_sim)
        m_sim.add_command(label="Recargar todos los drones", command=self._cmd_recargar_todos)
        m_sim.add_command(label="Ver pedidos entregados", command=self._cmd_ver_entregados)

    # ────────────────────────────────────────────────────────────────────────
    # Datos de ejemplo para la demo
    # ────────────────────────────────────────────────────────────────────────

    def _load_sample_data(self):
        # Drones
        for nombre, bat in [("Cóndor-1", 100.0), ("Cóndor-2", 78.0), ("Gaviota-1", 55.0)]:
            self._agregar_dron_interno(nombre, 5.0, bat)

        # Mantenimientos adicionales para demo
        drones_lista = list(self.drones.values())
        drones_lista[0].registrar_mantenimiento("Revisión de motores", "Ing. Torres", "Pre-temporada")
        drones_lista[0].registrar_mantenimiento("Calibración GPS", "Ing. Torres", "Offset corregido")
        drones_lista[1].registrar_mantenimiento("Limpieza de salitre", "Téc. Pérez", "La Brisa Loca")
        drones_lista[2].registrar_mantenimiento("Reemplazo de hélices", "Téc. Gómez", "Desgaste por sal")

        # Productos (insertados en el AVL)
        prods = [
            (100, "Insulina 10UI",      "Medicamento", 50,  0.10, 85000),
            (101, "Adrenalina 1mg",     "Medicamento", 20,  0.10, 120000),
            (102, "Aspirina 500mg",     "Medicamento", 200, 0.05, 1500),
            (103, "Cargador USB-C",     "Repuesto",    15,  0.40, 35000),
            (104, "Batería dron 5200mAh","Repuesto",   8,   0.85, 180000),
            (105, "Contrato urgente",   "Documento",   5,   0.05, 0),
            (106, "Guía turística SM",  "Documento",   30,  0.20, 8000),
            (107, "Suero oral",         "Medicamento", 80,  0.20, 4500),
        ]
        for id_p, nom, cat, stk, peso, precio in prods:
            p = Producto(id_p, nom, cat, stk, peso, precio)
            self.inventario.insertar(p)
            self._contador_prods = max(self._contador_prods, id_p + 1)

        # Pedidos en cola
        pedidos_demo = [
            (101, 2, 1, "Centro Histórico", "Hotel La Castellana", 3),
            (105, 1, 2, "El Rodadero",      "Resort Playa Blanca",  2),
            (102, 3, 4, "Taganga",          "Hostal Backpacker",    1),
            (100, 2, 4, "Zona Hotelera",    "Clínica Turística",    3),
            (106, 1, 7, "Bahía S. Marta",   "Marina Real",          1),
        ]
        for id_p, cant, dest_id, dest_nom, sol, prio in pedidos_demo:
            self._agregar_pedido_interno(id_p, cant, dest_id, dest_nom, sol, prio)

        self._refresh_all()

    # ────────────────────────────────────────────────────────────────────────
    # Comandos del menú / botones
    # ────────────────────────────────────────────────────────────────────────

    def _cmd_nuevo_dron(self):
        NuevoDronDialog(self.root, self._on_nuevo_dron)

    def _on_nuevo_dron(self, nombre, cap, bat):
        dron = self._agregar_dron_interno(nombre, cap, bat)
        self._add_alert(f"Dron registrado: {dron.nombre} (ID {dron.id})")
        self._refresh_drones()

    def _cmd_nuevo_pedido(self):
        prods = self.inventario.obtener_todos()
        if not prods:
            messagebox.showwarning("Sin inventario",
                                   "Primero agrega productos al inventario (AVL).",
                                   parent=self.root)
            return
        nodos_validos = [n for n in self.mapa.nodos.values() if not n.excluido]
        NuevoPedidoDialog(self.root, prods, nodos_validos, self._on_nuevo_pedido)

    def _on_nuevo_pedido(self, id_p, cant, dest_id, dest_nom, origen_id, origen_nom, sol, prio):
        self._agregar_pedido_interno(id_p, cant, dest_id, dest_nom, sol, prio, origen_id, origen_nom)
        self._add_alert(f"Pedido encolado → {dest_nom}  (cola: {self.cola_pedidos.tamaño})")
        self._refresh_pedidos()

    def _cmd_nuevo_producto(self):
        NuevoProductoDialog(self.root, self._contador_prods, self._on_nuevo_producto)

    def _on_nuevo_producto(self, id_p, nombre, cat, stock, peso, precio):
        p = Producto(id_p, nombre, cat, stock, peso, precio)
        self.inventario.insertar(p)
        self._contador_prods += 1
        self._add_alert(f"Producto [{id_p}] '{nombre}' insertado en AVL (altura={self.inventario.altura_arbol()})")
        self._refresh_inventario()

    def _cmd_mantenimiento(self):
        drones = list(self.drones.values())
        if not drones:
            messagebox.showwarning("Sin drones", "No hay drones registrados.", parent=self.root)
            return
        MantenimientoDialog(self.root, drones, self._on_mantenimiento)

    def _on_mantenimiento(self, id_dron, tipo, tecnico, notas):
        d = self.drones[id_dron]
        d.registrar_mantenimiento(tipo, tecnico, notas)
        self._add_alert(f"{d.nombre}: '{tipo}' apilado en historial.")
        self._refresh_drones()
        self._refresh_mantenimientos()

    def _cmd_historial_general(self):
        drones = list(self.drones.values())
        if not drones:
            messagebox.showwarning("Sin drones", "No hay drones registrados.", parent=self.root)
            return
        HistorialGeneralDialog(self.root, drones)

    def _cmd_despachar(self):
        if self.cola_pedidos.esta_vacia():
            messagebox.showinfo("Cola vacía",
                                "No hay pedidos pendientes en la cola FIFO.",
                                parent=self.root)
            return

        disponibles = [d for d in self.drones.values() if d.esta_disponible()]
        if not disponibles:
            messagebox.showwarning("Sin drones",
                                   "No hay drones disponibles con batería suficiente.",
                                   parent=self.root)
            return

        pedidos_en_cola = self.cola_pedidos.obtener_lista()
        nodos_validos   = [n for n in self.mapa.nodos.values() if not n.excluido]

        DespacharDialog(
            self.root,
            pedidos_en_cola,
            disponibles,
            self._on_despachar_confirm,
        )

    def _on_despachar_confirm(self, pedido: Pedido, dron: Dron):
        # Quitar el pedido elegido de la cola (puede no ser el primero)
        todos = self.cola_pedidos.obtener_lista()
        self.cola_pedidos = ColaFIFO()
        for p in todos:
            if p is not pedido:
                self.cola_pedidos.encolar(p)

        # Usar el nodo de origen definido al crear el pedido
        nodo_origen_id = pedido.origen_id
        dron.nodo_actual = nodo_origen_id

        # Calcular ruta con A*
        ruta, costo = self.mapa.a_estrella(nodo_origen_id, pedido.destino_id)
        if not ruta:
            self.cola_pedidos.encolar(pedido)
            messagebox.showerror("Sin ruta",
                                  f"A* no encontró ruta hacia {pedido.destino_nombre}.",
                                  parent=self.root)
            return

        # Configurar dron para el vuelo
        dron.estado = "en_vuelo"
        dron.pedido_actual = pedido
        dron.route_ids = [n.id for n in ruta]
        dron.route_idx = 1
        nodo_orig = self.mapa.nodos[nodo_origen_id]
        dron.px, dron.py = float(nodo_orig.x), float(nodo_orig.y)
        dron.asignar_ruta(ruta)

        pedido.marcar_en_proceso(dron.id, [n.nombre for n in ruta])

        # Registrar en espacio aéreo (Matriz Dispersa)
        cr = int(dron.py / MAP_H * NR)
        cc = int(dron.px / MAP_W * NC)
        try:
            self.espacio_aereo.insertar(cr, cc, dron.id)
        except IndexError:
            pass

        ruta_str = " → ".join(n.nombre for n in ruta)
        self._add_alert(
            f"✈ {dron.nombre} despachado desde {nodo_orig.nombre}"
            f"  |  destino: {pedido.destino_nombre}"
            f"  |  ruta A* ({costo:.1f} km): {ruta_str}"
        )
        self._refresh_all()

    def _cmd_ver_cola(self):
        ColaPedidosDialog(self.root, self.cola_pedidos)

    def _cmd_actualizar_stock(self):
        prods = self.inventario.obtener_todos()
        if not prods:
            messagebox.showwarning("Sin productos", "Primero agrega productos al inventario.", parent=self.root)
            return
        ActualizarStockDialog(self.root, prods, self._on_actualizar_stock)

    def _on_actualizar_stock(self, id_prod, delta):
        prod = self.inventario.buscar(id_prod)
        if prod:
            prod.stock += delta
            accion = f"+{delta}" if delta >= 0 else str(delta)
            self._add_alert(f"Stock actualizado: [{id_prod}] {prod.nombre}  {accion} → {prod.stock} unidades")
            self._refresh_inventario()

    def _cmd_buscar_producto(self):
        BuscarProductoDialog(self.root, self.inventario)

    def _cmd_ver_inventario(self):
        InventarioDialog(self.root, self.inventario)

    def _cmd_recargar_todos(self):
        for d in self.drones.values():
            if d.estado in ("disponible", "baja_bateria", "recargando"):
                d.bateria = 100.0
                d.estado = "disponible"
                d._registrar("Recarga completa", "Sistema", "Recarga masiva operador")
        self._add_alert("Todos los drones recargados al 100%.")
        self._refresh_drones()

    def _cmd_ver_entregados(self):
        if not self.entregados:
            messagebox.showinfo("Sin entregas", "Aún no hay entregas completadas.", parent=self.root)
            return
        dlg = tk.Toplevel(self.root)
        dlg.title("Pedidos Entregados")
        dlg.configure(bg=BG)
        dlg.geometry("560x400")
        frm = tk.Frame(dlg, bg=BG, padx=16, pady=12)
        frm.pack(fill="both", expand=True)
        tk.Label(frm, text=f"ENTREGAS COMPLETADAS ({len(self.entregados)})",
                 bg=BG, fg=TITLE, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        cols = ("id", "destino", "dron", "fecha")
        tree = ttk.Treeview(frm, columns=cols, show="headings", height=12, style="Dark.Treeview")
        for c, h, w in zip(cols, ("Pedido", "Destino", "Dron", "Hora entrega"), (60, 150, 80, 100)):
            tree.heading(c, text=h); tree.column(c, width=w)
        tree.pack(fill="both", expand=True, pady=6)
        for p in self.entregados:
            tree.insert("", "end", values=(f"P{p.id:03d}", p.destino_nombre,
                                            p.dron_asignado, p.fecha_entrega or "—"))
        tk.Button(frm, text="Cerrar", command=dlg.destroy,
                  bg=CARD, fg=TEXT, relief="flat", pady=5).pack(side="right")

    # ────────────────────────────────────────────────────────────────────────
    # Eventos del mapa
    # ────────────────────────────────────────────────────────────────────────

    def _on_map_click(self, event):
        cx, cy = event.x, event.y
        for nodo in self.mapa.nodos.values():
            nx, ny = self._scale(nodo.x, nodo.y)
            if (cx - nx) ** 2 + (cy - ny) ** 2 <= (NODE_R + 6) ** 2:
                self._nodo_sel = nodo.id
                drones_aqui = [d for d in self.drones.values()
                                if d.nodo_actual == nodo.id and d.estado != "en_vuelo"]
                self.lbl_nodo_info.config(text=f"Nodo: {nodo.nombre} | {nodo.tipo.upper()}")
                DetalleNodoDialog(self.root, nodo, drones_aqui)
                self._draw_static_map()  # re-dibuja resaltando nodo seleccionado
                return

    def _on_canvas_resize(self, event):
        self._draw_static_map()

    def _on_dron_doble_click(self, event):
        sel = self._tree_drones.selection()
        if not sel:
            return
        item = self._tree_drones.item(sel[0])
        id_dron = item["values"][0] if item["values"] else None
        if id_dron and id_dron in self.drones:
            d = self.drones[id_dron]
            # Mostrar menú: historial o ruta LDE
            menu = tk.Menu(self.root, tearoff=0, bg=PANEL, fg=TEXT)
            menu.add_command(label="Ver Historial (Pila LIFO)",
                             command=lambda: HistorialDronDialog(self.root, d))
            menu.add_command(label="Ver Ruta (Lista Doble)",
                             command=lambda: RutaDronDialog(self.root, d))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    # ────────────────────────────────────────────────────────────────────────
    # Animación
    # ────────────────────────────────────────────────────────────────────────

    def _animation_tick(self):
        self._update_clock()
        self._update_drones_animation()
        self._draw_dynamic()
        self._refresh_matrix_display()
        self.root.after(ANIM_MS, self._animation_tick)

    def _update_clock(self):
        self.lbl_hora.config(text=time.strftime("%d/%m/%Y  %H:%M:%S"))

    def _update_drones_animation(self):
        for dron in self.drones.values():
            if dron.estado not in ("en_vuelo", "baja_bateria"):
                continue

            # Recuperación: ruta terminada pero entrega no finalizada (tick anterior falló)
            if not dron.route_ids or dron.route_idx >= len(dron.route_ids):
                self._complete_delivery(dron)
                continue

            nodo_dest = self.mapa.nodos[dron.route_ids[dron.route_idx]]
            tx, ty = float(nodo_dest.x), float(nodo_dest.y)
            dx, dy = tx - dron.px, ty - dron.py
            dist = (dx * dx + dy * dy) ** 0.5

            old_cr = int(dron.py / MAP_H * NR)
            old_cc = int(dron.px / MAP_W * NC)

            if dist < DRONE_SPEED:
                # Llegó al nodo
                dron.px, dron.py = tx, ty
                dron.nodo_actual = dron.route_ids[dron.route_idx]
                dron.route_idx += 1

                new_cr = int(dron.py / MAP_H * NR)
                new_cc = int(dron.px / MAP_W * NC)
                self._move_matrix(dron.id, old_cr, old_cc, new_cr, new_cc)

                if dron.route_idx >= len(dron.route_ids):
                    self._complete_delivery(dron)
                    continue   # no consumir batería después de completar
            else:
                factor = DRONE_SPEED / dist
                dron.px += dx * factor
                dron.py += dy * factor

                new_cr = int(dron.py / MAP_H * NR)
                new_cc = int(dron.px / MAP_W * NC)
                if (new_cr, new_cc) != (old_cr, old_cc):
                    self._move_matrix(dron.id, old_cr, old_cc, new_cr, new_cc)

            # Consumo de batería (solo mientras vuela, no al completar)
            dron.consumir_bateria(BAT_COST)
            if dron.bateria < 20 and dron.estado == "en_vuelo":
                self._add_alert(f"⚠  {dron.nombre}: batería baja ({dron.bateria:.0f}%)")

    def _move_matrix(self, id_dron, old_r, old_c, new_r, new_c):
        try:
            self.espacio_aereo.eliminar(old_r, old_c)
        except Exception:
            pass
        try:
            self.espacio_aereo.insertar(new_r, new_c, id_dron)
        except Exception:
            pass

    def _complete_delivery(self, dron: Dron):
        # Limpiar estado del dron PRIMERO: garantiza que no quede atascado
        # aunque falle cualquier operación posterior.
        dron.estado = "disponible"
        dron.route_ids = []
        dron.route_idx = 0
        self.espacio_aereo.limpiar_dron(dron.id)

        pedido: Pedido = dron.pedido_actual
        dron.pedido_actual = None

        if pedido:
            pedido.marcar_entregado()
            self.entregados.append(pedido)
            prod = self.inventario.buscar(pedido.id_producto)
            if prod:
                prod.stock = max(0, prod.stock - pedido.cantidad)
            self._add_alert(
                f"✓  Entrega completada: P{pedido.id:03d} → {pedido.destino_nombre}"
                f"  por {dron.nombre}"
            )

        self._refresh_all()

    # ────────────────────────────────────────────────────────────────────────
    # Dibujo del mapa
    # ────────────────────────────────────────────────────────────────────────

    def _scale(self, x, y):
        """Convierte coordenadas del grafo (basadas en MAP_W×MAP_H) a las del canvas actual."""
        cw = self.canvas.winfo_width()  or MAP_W
        ch = self.canvas.winfo_height() or MAP_H
        return int(x * cw / MAP_W), int(y * ch / MAP_H)

    def _draw_static_map(self):
        self.canvas.delete("static", "dynamic")
        cw = self.canvas.winfo_width()  or MAP_W
        ch = self.canvas.winfo_height() or MAP_H

        def p(rx, ry):
            return int(rx * cw), int(ry * ch)

        # ── Fondo — Mar Caribe ──────────────────────────────────────────────
        self.canvas.create_rectangle(0, 0, cw, ch, fill="#081525", outline="", tags="static")

        # Cuadrícula sutil (olas)
        for gx in range(0, cw, 40):
            self.canvas.create_line(gx, 0, gx, ch, fill="#0c1e35", width=1, tags="static")
        for gy in range(0, ch, 40):
            self.canvas.create_line(0, gy, cw, gy, fill="#0c1e35", width=1, tags="static")

        # ── Masa terrestre principal ────────────────────────────────────────
        # El mar Caribe queda al OESTE (izquierda).
        # La Bahía de Santa Marta es la gran ensenada que se adentra desde el oeste.
        # Taganga es la pequeña cala al norte.
        land_pts = []
        for rx, ry in [
            (0.31, 0.00),   # norte — comienzo del borde costero
            (1.00, 0.00),   # esquina superior derecha
            (1.00, 1.00),   # esquina inferior derecha
            (0.00, 1.00),   # esquina inferior izquierda
            (0.00, 0.82),   # costa sur, frente al mar
            (0.22, 0.88),   # El Rodadero — saliente sur
            (0.18, 0.78),   # Zona Hotelera — costa
            (0.13, 0.66),   # norte de zona hotelera
            (0.07, 0.57),   # entrada sur de la Bahía
            (0.04, 0.47),   # interior de la Bahía (punto más al oeste)
            (0.09, 0.36),   # salida norte de la Bahía
            (0.16, 0.27),   # costa norte rumbo noreste
            (0.26, 0.19),   # acercándose a Taganga
            (0.27, 0.14),   # base de la península de Taganga
            (0.24, 0.10),   # Taganga — sur de la cala
            (0.27, 0.04),   # Taganga — punta norte
            (0.31, 0.10),   # Taganga — este de la cala
            (0.31, 0.00),   # cierre con el borde norte
        ]:
            land_pts.extend(p(rx, ry))
        self.canvas.create_polygon(land_pts, fill="#0d1f15",
                                   outline="#102a18", width=1, tags="static")

        # ── Bahía de Santa Marta (agua interior más clara) ──────────────────
        bahia_pts = []
        for rx, ry in [
            (0.00, 0.36),
            (0.09, 0.36),
            (0.04, 0.47),
            (0.07, 0.57),
            (0.00, 0.62),
        ]:
            bahia_pts.extend(p(rx, ry))
        self.canvas.create_polygon(bahia_pts, fill="#0b2035",
                                   outline="#0d2d4a", width=1, tags="static")
        bx, by = p(0.035, 0.485)
        self.canvas.create_text(bx, by, text="Bahía\nS. Marta",
                                fill="#1a4060", font=("Segoe UI", 7),
                                justify="center", tags="static")

        # ── Mar Caribe (etiqueta en zona abierta) ───────────────────────────
        mx, my = p(0.05, 0.20)
        self.canvas.create_text(mx, my, text="Mar\nCaribe",
                                fill="#0f2d45", font=("Segoe UI", 8, "italic"),
                                justify="center", tags="static")

        # ── Sierra Nevada (triángulos al este) ──────────────────────────────
        for rx, ry, sz in [(0.78, 0.07, 22), (0.70, 0.09, 16),
                           (0.86, 0.11, 18), (0.65, 0.16, 12)]:
            mx2, my2 = p(rx, ry)
            tri = [mx2 - sz, my2 + sz, mx2, my2 - sz, mx2 + sz, my2 + sz]
            self.canvas.create_polygon(tri, fill="#1a2a1a",
                                       outline="#253525", tags="static")
        snx, sny = p(0.77, 0.22)
        self.canvas.create_text(snx, sny, text="Sierra Nevada",
                                fill="#2a4a2a", font=("Segoe UI", 8, "italic"),
                                tags="static")

        # ── Cerro Ziruma (entre Zona Hotelera y El Rodadero) ────────────────
        zx, zy = self._scale(216, 355)
        ztri = [zx - 13, zy + 10, zx, zy - 12, zx + 13, zy + 10]
        self.canvas.create_polygon(ztri, fill="#1a2d1a", outline="#2a4a2a", tags="static")
        self.canvas.create_text(zx, zy + 16, text="Ziruma",
                                fill="#3a6a3a", font=("Segoe UI", 7), tags="static")

        # ── Zona de exclusión aérea (Aeropuerto Simón Bolívar) ───────────────
        nodo_aero = self.mapa.nodos[8]
        ax, ay = self._scale(nodo_aero.x, nodo_aero.y)
        self.canvas.create_oval(ax - 72, ay - 40, ax + 72, ay + 40,
                                fill="#1a0505", outline="#f85149",
                                width=1, dash=(4, 3), tags="static")
        self.canvas.create_text(ax, ay + 52, text="ZONA EXCLUSIÓN AÉREA",
                                fill="#f85149", font=("Segoe UI", 7, "bold"), tags="static")

        # ── Aristas (rutas aéreas) ───────────────────────────────────────────
        for n1, n2, peso in self.mapa.obtener_aristas():
            x1, y1 = self._scale(n1.x, n1.y)
            x2, y2 = self._scale(n2.x, n2.y)
            self.canvas.create_line(x1, y1, x2, y2, fill=EDGE_CLR, width=1, tags="static")
            emx, emy = (x1 + x2) // 2, (y1 + y2) // 2
            self.canvas.create_text(emx, emy - 6, text=f"{peso:.1f}",
                                    fill="#3a5a7a", font=("Segoe UI", 7), tags="static")

        # ── Nodos ────────────────────────────────────────────────────────────
        for nodo in self.mapa.nodos.values():
            nx, ny = self._scale(nodo.x, nodo.y)
            clr = NODE_CLR.get(nodo.tipo, TEXT)
            sel = (nodo.id == self._nodo_sel)
            outline_clr = TITLE if sel else "#0d1117"
            outline_w   = 3 if sel else 1
            self.canvas.create_oval(nx - NODE_R, ny - NODE_R,
                                    nx + NODE_R, ny + NODE_R,
                                    fill=clr, outline=outline_clr,
                                    width=outline_w, tags="static")
            icon = {"almacen": "🏭", "recarga": "⚡", "excluido": "✕"}.get(nodo.tipo, "●")
            self.canvas.create_text(nx, ny, text=icon,
                                    fill=BG if nodo.tipo != "excluido" else TITLE,
                                    font=("Segoe UI", 9, "bold"), tags="static")
            self.canvas.create_text(nx, ny + NODE_R + 9, text=nodo.nombre,
                                    fill=clr, font=("Segoe UI", 8, "bold"), tags="static")

        # ── Título ───────────────────────────────────────────────────────────
        self.canvas.create_text(10, 10, text="Santa Marta, Colombia",
                                anchor="nw", fill="#1a4a7a",
                                font=("Segoe UI", 9, "bold"), tags="static")

    def _draw_dynamic(self):
        self.canvas.delete("dynamic")
        self._tick += 1

        for dron in self.drones.values():
            if dron.estado not in ("en_vuelo", "baja_bateria"):
                continue
            if not dron.route_ids:
                continue

            clr = DRONE_CLR.get(dron.estado, "#ffd700")

            # ── Segmentos de la ruta ─────────────────────────────────────────
            for i in range(len(dron.route_ids) - 1):
                n1 = self.mapa.nodos[dron.route_ids[i]]
                n2 = self.mapa.nodos[dron.route_ids[i + 1]]
                x1, y1 = self._scale(n1.x, n1.y)
                x2, y2 = self._scale(n2.x, n2.y)

                if i < dron.route_idx - 1:
                    # Tramo ya recorrido — verde tenue, punteado
                    self.canvas.create_line(x1, y1, x2, y2,
                                             fill="#2a5a3a", width=2,
                                             dash=(5, 4), tags="dynamic")
                else:
                    # Tramo pendiente — color del dron, sólido
                    self.canvas.create_line(x1, y1, x2, y2,
                                             fill=clr, width=3, tags="dynamic")

            # ── Marcadores en nodos intermedios de la ruta ───────────────────
            for i, nid in enumerate(dron.route_ids):
                if i == 0 or i == len(dron.route_ids) - 1:
                    continue          # origen y destino ya se dibujan como nodos
                n = self.mapa.nodos[nid]
                wx, wy = self._scale(n.x, n.y)
                done = i < dron.route_idx
                self.canvas.create_oval(wx - 5, wy - 5, wx + 5, wy + 5,
                                         fill="#2a5a3a" if done else clr,
                                         outline=BG, width=1, tags="dynamic")

            # ── Anillo pulsante en el nodo destino ───────────────────────────
            dest = self.mapa.nodos[dron.route_ids[-1]]
            dnx, dny = self._scale(dest.x, dest.y)
            pulse = NODE_R + 5 + int(5 * abs(math.sin(self._tick * 0.12)))
            self.canvas.create_oval(dnx - pulse, dny - pulse,
                                     dnx + pulse, dny + pulse,
                                     outline=clr, width=2, fill="", tags="dynamic")
            self.canvas.create_text(dnx, dny + NODE_R + 20,
                                     text="DESTINO", fill=clr,
                                     font=("Segoe UI", 7, "bold"), tags="dynamic")

            # ── Línea punteada: posición actual → próximo nodo ───────────────
            if dron.route_idx < len(dron.route_ids):
                next_n = self.mapa.nodos[dron.route_ids[dron.route_idx]]
                nx2, ny2 = self._scale(int(next_n.x), int(next_n.y))
                cx, cy = self._scale(int(dron.px), int(dron.py))
                self.canvas.create_line(cx, cy, nx2, ny2,
                                         fill=clr, width=2,
                                         dash=(3, 2), tags="dynamic")

            # ── Icono del dron ────────────────────────────────────────────────
            dx, dy = self._scale(int(dron.px), int(dron.py))
            # Sombra
            self.canvas.create_oval(dx - DRONE_R - 1, dy - DRONE_R - 1,
                                     dx + DRONE_R + 1, dy + DRONE_R + 1,
                                     fill="#000000", outline="", tags="dynamic")
            # Cuerpo
            self.canvas.create_oval(dx - DRONE_R, dy - DRONE_R,
                                     dx + DRONE_R, dy + DRONE_R,
                                     fill=clr, outline=TITLE, width=1, tags="dynamic")
            self.canvas.create_text(dx, dy, text="✈", fill=BG,
                                     font=("Segoe UI", 8, "bold"), tags="dynamic")
            # Nombre
            self.canvas.create_text(dx, dy - DRONE_R - 8, text=dron.nombre,
                                     fill=clr, font=("Segoe UI", 7, "bold"), tags="dynamic")

            # ── Barra de batería ──────────────────────────────────────────────
            bar_w = 30
            bx = dx - bar_w // 2
            by = dy + DRONE_R + 4
            self.canvas.create_rectangle(bx, by, bx + bar_w, by + 5,
                                          fill="#1a1a2a", outline="", tags="dynamic")
            fill_w = int(bar_w * dron.bateria / 100)
            bat_clr = "#3fb950" if dron.bateria > 50 else WARNING if dron.bateria > 20 else DANGER
            self.canvas.create_rectangle(bx, by, bx + fill_w, by + 5,
                                          fill=bat_clr, outline="", tags="dynamic")
            self.canvas.create_text(dx, by + 12, text=f"{dron.bateria:.0f}%",
                                     fill=bat_clr, font=("Segoe UI", 7), tags="dynamic")

    # ────────────────────────────────────────────────────────────────────────
    # Refresh de paneles
    # ────────────────────────────────────────────────────────────────────────

    def _refresh_all(self):
        self._refresh_drones()
        self._refresh_pedidos()
        self._refresh_inventario()
        self._refresh_mantenimientos()
        self._refresh_stats()

    def _refresh_mantenimientos(self):
        for item in self._tree_mant.get_children():
            self._tree_mant.delete(item)
        total_registros = 0
        for d in self.drones.values():
            ult = d.ultimo_mantenimiento()
            total_registros += d.historial.tamaño
            if ult:
                self._tree_mant.insert("", "end",
                                        values=(d.nombre, ult["tipo"], ult["fecha"]))
            else:
                self._tree_mant.insert("", "end",
                                        values=(d.nombre, "Sin registros", "—"),
                                        tags=("dim",))
        self._tree_mant.tag_configure("dim", foreground=DIM)
        nd = len(self.drones)
        self.lbl_mant_total.config(
            text=f"{nd} dron{'es' if nd != 1 else ''}  |  {total_registros} registros totales"
        )

    def _refresh_drones(self):
        for item in self._tree_drones.get_children():
            self._tree_drones.delete(item)
        for d in self.drones.values():
            bat = d.bateria
            tag = "danger" if bat < 20 else "warn" if bat < 50 else "ok"
            self._tree_drones.insert("", "end",
                                      values=(d.id, d.estado, f"{bat:.0f}%"),
                                      tags=(tag,))
        self._tree_drones.tag_configure("ok",     foreground="#3fb950")
        self._tree_drones.tag_configure("warn",   foreground=WARNING)
        self._tree_drones.tag_configure("danger", foreground=DANGER)

    def _refresh_pedidos(self):
        for item in self._tree_ped.get_children():
            self._tree_ped.delete(item)
        prio_txt = {1: "Normal", 2: "Urgente", 3: "Crítico"}
        for i, p in enumerate(self.cola_pedidos.obtener_lista()):
            tag = "frente" if i == 0 else ""
            self._tree_ped.insert("", "end",
                                   values=(f"P{p.id:03d}", p.destino_nombre,
                                           prio_txt.get(p.prioridad, "?")),
                                   tags=(tag,))
        self._tree_ped.tag_configure("frente", foreground="#3fb950")
        n = self.cola_pedidos.tamaño
        self.lbl_cola_info.config(text=f"Cola FIFO  ({n} pendiente{'s' if n != 1 else ''})")

    def _refresh_inventario(self):
        for item in self._tree_inv.get_children():
            self._tree_inv.delete(item)
        for p in self.inventario.obtener_todos():
            tag = "low" if p.stock <= 5 else ""
            self._tree_inv.insert("", "end",
                                   values=(p.id, p.nombre, p.stock),
                                   tags=(tag,))
        self._tree_inv.tag_configure("low", foreground=DANGER)
        n = self.inventario.tamaño
        self.lbl_inv_info.config(
            text=f"Árbol AVL  ({n} producto{'s' if n != 1 else ''}, h={self.inventario.altura_arbol()})"
        )

    def _refresh_matrix_display(self):
        ocupados = self.espacio_aereo.obtener_ocupados()
        self.txt_matriz.config(state="normal")
        self.txt_matriz.delete("1.0", "end")
        if not ocupados:
            self.txt_matriz.insert("end", "Espacio aéreo despejado.\nNingún dron en tránsito.\n\n"
                                          f"Grilla: {NR}×{NC} = {NR*NC} celdas\n"
                                          f"Ocupadas: 0  (ahorro de memoria)")
        else:
            self.txt_matriz.insert("end",
                                    f"Celdas ocupadas: {len(ocupados)}/{NR*NC}\n"
                                    f"(solo se almacenan las no-nulas)\n\n")
            for f, c, v in ocupados:
                self.txt_matriz.insert("end", f"  ({f:02d},{c:02d}) → {v}\n")
        self.txt_matriz.config(state="disabled")

    def _refresh_stats(self):
        disp = sum(1 for d in self.drones.values() if d.esta_disponible())
        vuelo = sum(1 for d in self.drones.values() if d.estado == "en_vuelo")
        self.lbl_stats.config(
            text=f"Drones: {len(self.drones)} total  |  {disp} disponibles  |  {vuelo} en vuelo  "
                 f"|  Entregas: {len(self.entregados)}"
        )

    def _add_alert(self, msg: str):
        self.alertas.insert(0, msg)
        self.alertas = self.alertas[:50]
        self.lbl_status.config(text=msg[:120])
        self._refresh_stats()

    # ────────────────────────────────────────────────────────────────────────
    # Internos de gestión de datos
    # ────────────────────────────────────────────────────────────────────────

    def _agregar_dron_interno(self, nombre, cap, bat) -> Dron:
        self._contador_drones += 1
        id_dron = f"D{self._contador_drones:03d}"
        dron = Dron(id_dron, nombre, cap)
        dron.bateria = bat
        # Posición inicial: nodo 0 (Almacén)
        nodo0 = self.mapa.nodos[0]
        dron.px, dron.py = float(nodo0.x), float(nodo0.y)
        self.drones[id_dron] = dron
        return dron

    def _agregar_pedido_interno(self, id_p, cant, dest_id, dest_nom, sol, prio,
                               origen_id=0, origen_nom="Almacén Central"):
        self._contador_pedidos += 1
        pedido = Pedido(self._contador_pedidos, id_p, cant, dest_id, dest_nom,
                        sol, prio, origen_id, origen_nom)
        self.cola_pedidos.encolar(pedido)

    # ────────────────────────────────────────────────────────────────────────
    # Punto de entrada
    # ────────────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()
