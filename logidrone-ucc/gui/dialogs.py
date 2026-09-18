"""
Ventanas de diálogo (formularios) de LogiDrone-UCC
====================================================
Todos los diálogos son Toplevel modales sobre la ventana principal.
"""

import tkinter as tk
from tkinter import ttk, messagebox

# ── Paleta de colores (debe coincidir con app.py) ────────────────────────────
BG      = "#0d1117"
PANEL   = "#161b22"
CARD    = "#21262d"
BORDER  = "#30363d"
TEXT    = "#c9d1d9"
DIM     = "#8b949e"
ACCENT  = "#238636"
WARNING = "#d29922"
DANGER  = "#da3633"
INFO    = "#388bfd"
TITLE   = "#f0f6fc"


def _make_dialog(parent, titulo, w=440, h=380):
    """Crea y centra un Toplevel con estilo oscuro."""
    dlg = tk.Toplevel(parent)
    dlg.title(titulo)
    dlg.configure(bg=BG)
    dlg.resizable(False, False)
    dlg.grab_set()
    px = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
    py = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
    dlg.geometry(f"{w}x{h}+{px}+{py}")
    return dlg


def _label(parent, texto, bold=False, dim=False, size=10):
    color = DIM if dim else TEXT
    font = ("Segoe UI", size, "bold" if bold else "normal")
    return tk.Label(parent, text=texto, bg=BG, fg=color, font=font, anchor="w")


def _entry(parent, width=32, show=None):
    e = tk.Entry(parent, width=width, bg=CARD, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=("Segoe UI", 10),
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=INFO)
    if show:
        e.config(show=show)
    return e


def _combo(parent, valores, width=30):
    c = ttk.Combobox(parent, values=valores, width=width, state="readonly",
                     font=("Segoe UI", 10))
    if valores:
        c.current(0)
    return c


def _btn(parent, texto, comando, color=ACCENT):
    return tk.Button(parent, text=texto, command=comando,
                     bg=color, fg=TITLE, font=("Segoe UI", 10, "bold"),
                     relief="flat", padx=14, pady=6, cursor="hand2",
                     activebackground=color, activeforeground=TITLE)


def _section(parent, texto):
    tk.Label(parent, text=texto, bg=BG, fg=INFO,
             font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 2))
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Nuevo Dron
# ─────────────────────────────────────────────────────────────────────────────

class NuevoDronDialog:
    """Formulario para registrar un dron nuevo."""

    def __init__(self, parent, on_confirm):
        self.resultado = None
        dlg = _make_dialog(parent, "Registrar Nuevo Dron", 400, 320)

        frm = tk.Frame(dlg, bg=BG, padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        _label(frm, "REGISTRAR NUEVO DRON", bold=True, size=12).pack(anchor="w")
        _label(frm, "Complete los datos del dron a incorporar.", dim=True).pack(anchor="w", pady=(0, 8))

        _section(frm, "Información del Dron")

        r1 = tk.Frame(frm, bg=BG); r1.pack(fill="x", pady=3)
        _label(r1, "Nombre:").pack(side="left"); self.e_nombre = _entry(r1, 24); self.e_nombre.pack(side="right")

        r2 = tk.Frame(frm, bg=BG); r2.pack(fill="x", pady=3)
        _label(r2, "Capacidad (kg):").pack(side="left"); self.e_cap = _entry(r2, 24); self.e_cap.pack(side="right")
        self.e_cap.insert(0, "5.0")

        r3 = tk.Frame(frm, bg=BG); r3.pack(fill="x", pady=3)
        _label(r3, "Batería inicial (%):").pack(side="left"); self.e_bat = _entry(r3, 24); self.e_bat.pack(side="right")
        self.e_bat.insert(0, "100")

        tk.Frame(frm, bg=BG, height=12).pack()
        _btn(frm, "  Registrar Dron  ", lambda: self._confirmar(dlg, on_confirm)).pack(side="right")
        _btn(frm, "Cancelar", dlg.destroy, color=CARD).pack(side="right", padx=8)

    def _confirmar(self, dlg, callback):
        nombre = self.e_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Campo requerido", "Ingresa un nombre para el dron.", parent=dlg)
            return
        try:
            cap = float(self.e_cap.get())
            bat = float(self.e_bat.get())
            assert 0 < cap <= 50 and 0 <= bat <= 100
        except Exception:
            messagebox.showerror("Valor inválido", "Capacidad y batería deben ser números válidos.", parent=dlg)
            return
        dlg.destroy()
        callback(nombre, cap, bat)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Nuevo Pedido
# ─────────────────────────────────────────────────────────────────────────────

class NuevoPedidoDialog:
    """Formulario para crear una solicitud de entrega."""

    DESTINOS = [
        (0, "Almacén Central"),
        (1, "Centro Histórico"),
        (2, "El Rodadero"),
        (3, "Taganga"),
        (4, "Zona Hotelera"),
        (5, "Recarga Norte"),
        (6, "Recarga Sur"),
        (7, "Puerto / Bahía"),
    ]

    def __init__(self, parent, productos, nodos, on_confirm):
        dlg = _make_dialog(parent, "Nuevo Pedido de Entrega", 460, 440)
        frm = tk.Frame(dlg, bg=BG, padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        _label(frm, "NUEVO PEDIDO DE ENTREGA", bold=True, size=12).pack(anchor="w")
        _label(frm, "El pedido se añadirá al final de la cola FIFO.", dim=True).pack(anchor="w", pady=(0, 8))

        _section(frm, "Datos del Pedido")

        r1 = tk.Frame(frm, bg=BG); r1.pack(fill="x", pady=3)
        _label(r1, "Producto:").pack(side="left")
        prod_nombres = [f"[{p.id}] {p.nombre}" for p in productos] or ["(sin productos)"]
        self.cb_prod = _combo(r1, prod_nombres, 26); self.cb_prod.pack(side="right")
        self._productos = productos

        r2 = tk.Frame(frm, bg=BG); r2.pack(fill="x", pady=3)
        _label(r2, "Cantidad:").pack(side="left"); self.e_cant = _entry(r2, 26); self.e_cant.pack(side="right")
        self.e_cant.insert(0, "1")

        r3 = tk.Frame(frm, bg=BG); r3.pack(fill="x", pady=3)
        _label(r3, "Destino:").pack(side="left")
        dest_nombres = [f"{d[1]}" for d in self.DESTINOS]
        self.cb_dest = _combo(r3, dest_nombres, 26); self.cb_dest.pack(side="right")

        r_orig = tk.Frame(frm, bg=BG); r_orig.pack(fill="x", pady=3)
        _label(r_orig, "Origen:").pack(side="left")
        self._nodos = nodos
        orig_nombres = [n.nombre for n in nodos]
        self.cb_orig = _combo(r_orig, orig_nombres, 26)
        # Preseleccionar Almacén Central (id 0) si está en la lista
        for i, n in enumerate(nodos):
            if n.id == 0:
                self.cb_orig.current(i)
                break
        self.cb_orig.pack(side="right")

        r4 = tk.Frame(frm, bg=BG); r4.pack(fill="x", pady=3)
        _label(r4, "Solicitante:").pack(side="left"); self.e_sol = _entry(r4, 26); self.e_sol.pack(side="right")

        r5 = tk.Frame(frm, bg=BG); r5.pack(fill="x", pady=3)
        _label(r5, "Prioridad:").pack(side="left")
        self.cb_prio = _combo(r5, ["1 – Normal", "2 – Urgente", "3 – Crítico"], 26)
        self.cb_prio.pack(side="right")

        tk.Frame(frm, bg=BG, height=10).pack()
        _btn(frm, "  Agregar a Cola  ", lambda: self._confirmar(dlg, on_confirm)).pack(side="right")
        _btn(frm, "Cancelar", dlg.destroy, color=CARD).pack(side="right", padx=8)

    def _confirmar(self, dlg, callback):
        if not self._productos:
            messagebox.showwarning("Sin productos", "Primero añade productos al inventario.", parent=dlg)
            return
        try:
            cant = int(self.e_cant.get())
            assert cant > 0
        except Exception:
            messagebox.showerror("Valor inválido", "La cantidad debe ser un entero positivo.", parent=dlg)
            return
        idx_prod = self.cb_prod.current()
        prod = self._productos[idx_prod]
        idx_dest = self.cb_dest.current()
        dest_id, dest_nom = self.DESTINOS[idx_dest]
        idx_orig = self.cb_orig.current()
        nodo_orig = self._nodos[idx_orig]
        prio = self.cb_prio.current() + 1
        sol = self.e_sol.get().strip()
        dlg.destroy()
        callback(prod.id, cant, dest_id, dest_nom, nodo_orig.id, nodo_orig.nombre, sol, prio)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Nuevo Producto
# ─────────────────────────────────────────────────────────────────────────────

class NuevoProductoDialog:
    """Formulario para insertar un producto en el Árbol AVL."""

    CATS = ("Medicamento", "Repuesto", "Documento", "Alimento", "Otro")

    def __init__(self, parent, proximo_id, on_confirm):
        dlg = _make_dialog(parent, "Agregar Producto al Inventario", 440, 370)
        frm = tk.Frame(dlg, bg=BG, padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        _label(frm, "AGREGAR PRODUCTO — ÁRBOL AVL", bold=True, size=12).pack(anchor="w")
        _label(frm, f"Se insertará con ID = {proximo_id} y el árbol se rebalanceará.", dim=True).pack(anchor="w", pady=(0, 8))

        _section(frm, "Datos del Producto")

        r1 = tk.Frame(frm, bg=BG); r1.pack(fill="x", pady=3)
        _label(r1, "Nombre:").pack(side="left")
        self.e_nombre = _entry(r1, 24); self.e_nombre.pack(side="right")

        r2 = tk.Frame(frm, bg=BG); r2.pack(fill="x", pady=3)
        _label(r2, "Categoría:").pack(side="left")
        self.cb_cat = _combo(r2, self.CATS, 22); self.cb_cat.pack(side="right")

        r3 = tk.Frame(frm, bg=BG); r3.pack(fill="x", pady=3)
        _label(r3, "Stock inicial:").pack(side="left")
        self.e_stock = _entry(r3, 24); self.e_stock.pack(side="right")
        self.e_stock.insert(0, "10")

        r4 = tk.Frame(frm, bg=BG); r4.pack(fill="x", pady=3)
        _label(r4, "Peso/unidad (kg):").pack(side="left")
        self.e_peso = _entry(r4, 24); self.e_peso.pack(side="right")
        self.e_peso.insert(0, "0.1")

        r5 = tk.Frame(frm, bg=BG); r5.pack(fill="x", pady=3)
        _label(r5, "Precio ($):").pack(side="left")
        self.e_precio = _entry(r5, 24); self.e_precio.pack(side="right")
        self.e_precio.insert(0, "0")

        tk.Frame(frm, bg=BG, height=10).pack()
        _btn(frm, "  Insertar en AVL  ", lambda: self._confirmar(dlg, on_confirm, proximo_id)).pack(side="right")
        _btn(frm, "Cancelar", dlg.destroy, color=CARD).pack(side="right", padx=8)

    def _confirmar(self, dlg, callback, id_prod):
        nombre = self.e_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Campo requerido", "El nombre del producto es obligatorio.", parent=dlg)
            return
        try:
            stock = int(self.e_stock.get()); peso = float(self.e_peso.get())
            precio = float(self.e_precio.get())
            assert stock >= 0 and peso > 0
        except Exception:
            messagebox.showerror("Valor inválido", "Revisa stock, peso y precio.", parent=dlg)
            return
        cat = self.cb_cat.get()   # leer ANTES de destruir el widget
        dlg.destroy()
        callback(id_prod, nombre, cat, stock, peso, precio)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Registrar Mantenimiento
# ─────────────────────────────────────────────────────────────────────────────

class MantenimientoDialog:
    """Formulario para apilar un nuevo registro en la pila del dron."""

    TIPOS = (
        "Limpieza de salitre",
        "Cambio de batería",
        "Recarga completa",
        "Revisión de motores",
        "Calibración GPS",
        "Reemplazo de hélices",
        "Actualización firmware",
        "Mantenimiento preventivo",
        "Revisión post-vuelo",
        "Otro",
    )

    def __init__(self, parent, drones, on_confirm):
        dlg = _make_dialog(parent, "Registrar Mantenimiento", 460, 360)
        frm = tk.Frame(dlg, bg=BG, padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        _label(frm, "REGISTRAR MANTENIMIENTO — PILA LIFO", bold=True, size=12).pack(anchor="w")
        _label(frm, "El registro quedará en la cima de la pila del dron.", dim=True).pack(anchor="w", pady=(0, 8))

        _section(frm, "Datos del Mantenimiento")

        r1 = tk.Frame(frm, bg=BG); r1.pack(fill="x", pady=3)
        _label(r1, "Dron:").pack(side="left")
        dron_nombres = [f"{d.id} — {d.nombre}" for d in drones]
        self.cb_dron = _combo(r1, dron_nombres, 26); self.cb_dron.pack(side="right")
        self._drones = drones

        r2 = tk.Frame(frm, bg=BG); r2.pack(fill="x", pady=3)
        _label(r2, "Tipo:").pack(side="left")
        self.cb_tipo = _combo(r2, self.TIPOS, 26); self.cb_tipo.pack(side="right")

        r3 = tk.Frame(frm, bg=BG); r3.pack(fill="x", pady=3)
        _label(r3, "Técnico:").pack(side="left"); self.e_tec = _entry(r3, 26); self.e_tec.pack(side="right")

        r4 = tk.Frame(frm, bg=BG); r4.pack(fill="x", pady=3)
        _label(r4, "Notas:").pack(side="left"); self.e_notas = _entry(r4, 26); self.e_notas.pack(side="right")

        tk.Frame(frm, bg=BG, height=10).pack()
        _btn(frm, "  Apilar Registro  ", lambda: self._confirmar(dlg, on_confirm)).pack(side="right")
        _btn(frm, "Cancelar", dlg.destroy, color=CARD).pack(side="right", padx=8)

    def _confirmar(self, dlg, callback):
        if not self._drones:
            messagebox.showwarning("Sin drones", "No hay drones registrados.", parent=dlg)
            return
        tec   = self.e_tec.get().strip() or "Técnico"
        notas = self.e_notas.get().strip()   # leer ANTES de destruir
        tipo  = self.cb_tipo.get()           # leer ANTES de destruir
        idx   = self.cb_dron.current()
        dlg.destroy()
        callback(self._drones[idx].id, tipo, tec, notas)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Historial de Mantenimiento (Pila LIFO visualizada)
# ─────────────────────────────────────────────────────────────────────────────

class HistorialDronDialog:
    """Muestra la Pila LIFO del historial de un dron."""

    def __init__(self, parent, dron):
        dlg = _make_dialog(parent, f"Historial — {dron.nombre}", 520, 420)
        frm = tk.Frame(dlg, bg=BG, padx=20, pady=14)
        frm.pack(fill="both", expand=True)

        _label(frm, f"PILA LIFO — {dron.nombre}", bold=True, size=12).pack(anchor="w")
        _label(frm, "El registro más reciente aparece primero (cima de la pila).", dim=True).pack(anchor="w", pady=(0, 6))

        # Treeview
        cols = ("fecha", "tipo", "tecnico", "notas")
        tree = ttk.Treeview(frm, columns=cols, show="headings", height=12,
                            style="Dark.Treeview")
        for c, h, w in zip(cols, ("Fecha", "Tipo", "Técnico", "Notas"), (120, 170, 100, 120)):
            tree.heading(c, text=h); tree.column(c, width=w, anchor="w")
        tree.pack(fill="both", expand=True)

        registros = dron.historial.obtener_lista()
        for i, r in enumerate(registros):
            tag = "cima" if i == 0 else ""
            tree.insert("", "end", values=(r["fecha"], r["tipo"], r["tecnico"], r.get("notas", "")), tags=(tag,))
        tree.tag_configure("cima", background="#1f3a1f", foreground="#3fb950")

        _label(frm, f"Total: {len(registros)} registros en la pila.", dim=True).pack(anchor="w", pady=(6, 0))
        _btn(frm, "Cerrar", dlg.destroy, color=CARD).pack(side="right", pady=(8, 0))


# ─────────────────────────────────────────────────────────────────────────────
# 5b. Historial General de Mantenimientos (toda la flota)
# ─────────────────────────────────────────────────────────────────────────────

class HistorialGeneralDialog:
    """Vista consolidada de la Pila LIFO de mantenimientos de toda la flota."""

    def __init__(self, parent, drones: list):
        dlg = _make_dialog(parent, "Historial General de Mantenimientos", 660, 500)
        frm = tk.Frame(dlg, bg=BG, padx=20, pady=14)
        frm.pack(fill="both", expand=True)

        _label(frm, "HISTORIAL GENERAL — PILA LIFO DE TODA LA FLOTA",
               bold=True, size=12).pack(anchor="w")
        _label(frm, "Registros más recientes primero (cima de cada pila).",
               dim=True).pack(anchor="w", pady=(0, 6))

        # ── Filtro por dron ──────────────────────────────────────────────────
        filter_f = tk.Frame(frm, bg=BG)
        filter_f.pack(fill="x", pady=(0, 8))
        _label(filter_f, "Filtrar por dron:").pack(side="left")
        opciones = ["Todos los drones"] + [f"{d.id} — {d.nombre}" for d in drones]
        self._drones = drones
        self.cb_filtro = _combo(filter_f, opciones, 30)
        self.cb_filtro.pack(side="left", padx=10)
        self.cb_filtro.bind("<<ComboboxSelected>>", lambda e: self._recargar())

        # ── Tabla ────────────────────────────────────────────────────────────
        tree_f = tk.Frame(frm, bg=BG)
        tree_f.pack(fill="both", expand=True)

        cols = ("dron", "fecha", "tipo", "tecnico", "notas")
        self._tree = ttk.Treeview(tree_f, columns=cols, show="headings",
                                   height=13, style="Dark.Treeview")
        for c, h, w in zip(cols,
                           ("Dron", "Fecha", "Tipo de Mantenimiento", "Técnico", "Notas"),
                           (95, 125, 170, 105, 145)):
            self._tree.heading(c, text=h)
            self._tree.column(c, width=w, anchor="w")

        sb = ttk.Scrollbar(tree_f, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        # ── Barra inferior ───────────────────────────────────────────────────
        bot = tk.Frame(dlg, bg=BG, padx=20)
        bot.pack(fill="x", pady=(2, 10))
        self.lbl_count = tk.Label(bot, text="", bg=BG, fg=DIM,
                                   font=("Segoe UI", 9))
        self.lbl_count.pack(side="left")
        _btn(bot, "Cerrar", dlg.destroy, color=CARD).pack(side="right")

        self._recargar()

    def _recargar(self):
        for item in self._tree.get_children():
            self._tree.delete(item)

        idx = self.cb_filtro.current()
        drones_sel = self._drones if idx == 0 else [self._drones[idx - 1]]

        total = 0
        for dron in drones_sel:
            registros = dron.historial.obtener_lista()
            for i, r in enumerate(registros):
                # Resaltar cima de la pila de cada dron
                tag = "cima" if i == 0 else ("par" if i % 2 == 0 else "")
                self._tree.insert("", "end",
                                   values=(dron.nombre,
                                           r["fecha"],
                                           r["tipo"],
                                           r["tecnico"],
                                           r.get("notas", "")),
                                   tags=(tag,))
                total += 1

        self._tree.tag_configure("cima", background="#1f3a1f", foreground="#3fb950")
        self._tree.tag_configure("par",  background="#181e26")
        plural = "s" if total != 1 else ""
        self.lbl_count.config(
            text=f"Total: {total} registro{plural} en la pila  |  "
                 f"Drones con historial: {sum(1 for d in self._drones if not d.historial.esta_vacia())}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Ver Inventario (Árbol AVL)
# ─────────────────────────────────────────────────────────────────────────────

class InventarioDialog:
    """Muestra todos los productos del AVL (recorrido en-orden)."""

    def __init__(self, parent, arbol, on_delete=None):
        dlg = _make_dialog(parent, "Inventario — Árbol AVL", 600, 460)
        frm = tk.Frame(dlg, bg=BG, padx=20, pady=14)
        frm.pack(fill="both", expand=True)

        _label(frm, "INVENTARIO — ÁRBOL AVL (recorrido en-orden)", bold=True, size=12).pack(anchor="w")
        _label(frm, f"Altura del árbol: {arbol.altura_arbol()}  |  Productos: {arbol.tamaño}", dim=True).pack(anchor="w", pady=(0, 6))

        cols = ("id", "nombre", "cat", "stock", "peso", "precio")
        tree = ttk.Treeview(frm, columns=cols, show="headings", height=14, style="Dark.Treeview")
        for c, h, w in zip(cols,
                           ("ID", "Nombre", "Categoría", "Stock", "Peso kg", "Precio $"),
                           (48, 160, 100, 60, 65, 70)):
            tree.heading(c, text=h); tree.column(c, width=w, anchor="center" if c in ("id","stock") else "w")
        sb = ttk.Scrollbar(frm, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        productos = arbol.obtener_todos()
        for p in productos:
            tag = "low" if p.stock <= 5 else ""
            tree.insert("", "end",
                        values=(p.id, p.nombre, p.categoria, p.stock, p.peso_kg, f"${p.precio:.0f}"),
                        tags=(tag,))
        tree.tag_configure("low", background="#2d1b1b", foreground="#f85149")

        frm2 = tk.Frame(dlg, bg=BG, padx=20); frm2.pack(fill="x", pady=(0, 10))
        _label(frm2, "Rojo = stock ≤ 5 unidades.", dim=True).pack(side="left")
        _btn(frm2, "Cerrar", dlg.destroy, color=CARD).pack(side="right")


# ─────────────────────────────────────────────────────────────────────────────
# 7. Actualizar Stock de un producto existente
# ─────────────────────────────────────────────────────────────────────────────

class ActualizarStockDialog:
    """Suma o resta unidades al stock de un producto ya existente en el AVL."""

    def __init__(self, parent, productos, on_confirm):
        dlg = _make_dialog(parent, "Actualizar Stock — Árbol AVL", 440, 300)
        frm = tk.Frame(dlg, bg=BG, padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        _label(frm, "ACTUALIZAR STOCK — ÁRBOL AVL", bold=True, size=12).pack(anchor="w")
        _label(frm, "Busca el producto y ajusta la cantidad en inventario.", dim=True).pack(anchor="w", pady=(0, 8))

        _section(frm, "Selecciona el producto")

        r1 = tk.Frame(frm, bg=BG); r1.pack(fill="x", pady=3)
        _label(r1, "Producto:").pack(side="left")
        opciones = [f"[{p.id}] {p.nombre}  (stock actual: {p.stock})" for p in productos]
        self.cb_prod = _combo(r1, opciones, 32); self.cb_prod.pack(side="right")
        self._productos = productos

        r2 = tk.Frame(frm, bg=BG); r2.pack(fill="x", pady=3)
        _label(r2, "Cantidad a agregar:").pack(side="left")
        self.e_cant = _entry(r2, 24); self.e_cant.pack(side="right")
        self.e_cant.insert(0, "10")
        _label(frm, "  (usa número negativo para reducir stock)", dim=True, size=9).pack(anchor="e")

        tk.Frame(frm, bg=BG, height=10).pack()
        _btn(frm, "  Actualizar  ", lambda: self._confirmar(dlg, on_confirm)).pack(side="right")
        _btn(frm, "Cancelar", dlg.destroy, color=CARD).pack(side="right", padx=8)

    def _confirmar(self, dlg, callback):
        if not self._productos:
            messagebox.showwarning("Sin productos", "No hay productos en el inventario.", parent=dlg)
            return
        try:
            delta = int(self.e_cant.get())
        except ValueError:
            messagebox.showerror("Valor inválido", "La cantidad debe ser un número entero.", parent=dlg)
            return
        idx = self.cb_prod.current()
        prod = self._productos[idx]
        nuevo_stock = prod.stock + delta
        if nuevo_stock < 0:
            messagebox.showerror("Stock insuficiente",
                                 f"No puedes reducir a {nuevo_stock} unidades (stock actual: {prod.stock}).",
                                 parent=dlg)
            return
        dlg.destroy()
        callback(prod.id, delta)


# ─────────────────────────────────────────────────────────────────────────────
# 8. Buscar Producto en el AVL
# ─────────────────────────────────────────────────────────────────────────────

class BuscarProductoDialog:
    """Búsqueda O(log n) en el árbol AVL."""

    def __init__(self, parent, arbol):
        dlg = _make_dialog(parent, "Buscar Producto — O(log n)", 420, 300)
        frm = tk.Frame(dlg, bg=BG, padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        _label(frm, "BÚSQUEDA EN ÁRBOL AVL — O(log n)", bold=True, size=12).pack(anchor="w")
        _label(frm, "Introduce el ID del producto para buscarlo.", dim=True).pack(anchor="w", pady=(0, 10))

        r = tk.Frame(frm, bg=BG); r.pack(fill="x", pady=4)
        _label(r, "ID del producto:").pack(side="left")
        self.e_id = _entry(r, 20); self.e_id.pack(side="right")

        self.lbl_result = tk.Label(frm, text="", bg=CARD, fg=TEXT,
                                   font=("Segoe UI", 10), wraplength=360,
                                   justify="left", padx=10, pady=10, relief="flat")
        self.lbl_result.pack(fill="x", pady=10)

        _btn(frm, "  Buscar  ", lambda: self._buscar(arbol)).pack(side="left")
        _btn(frm, "Cerrar", dlg.destroy, color=CARD).pack(side="right")

    def _buscar(self, arbol):
        try:
            id_p = int(self.e_id.get())
        except ValueError:
            self.lbl_result.config(text="⚠  El ID debe ser un número entero.", fg=WARNING)
            return
        p = arbol.buscar(id_p)
        if p:
            self.lbl_result.config(
                fg="#3fb950",
                text=(f"✓  Encontrado  [{p.id}]\n"
                      f"Nombre: {p.nombre}\n"
                      f"Categoría: {p.categoria}\n"
                      f"Stock: {p.stock} unidades  |  Peso: {p.peso_kg} kg")
            )
        else:
            self.lbl_result.config(text=f"✗  Producto ID {id_p} no encontrado en el árbol.", fg=DANGER)


# ─────────────────────────────────────────────────────────────────────────────
# 8. Detalle del Nodo del Mapa
# ─────────────────────────────────────────────────────────────────────────────

class DetalleNodoDialog:
    """Popup con info del nodo al hacer clic en el mapa."""

    def __init__(self, parent, nodo, drones_en_nodo: list):
        dlg = _make_dialog(parent, f"Nodo: {nodo.nombre}", 380, 280)
        frm = tk.Frame(dlg, bg=BG, padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        color = {"almacen": "#06d6a0", "entrega": "#58a6ff",
                 "recarga": "#3fb950", "excluido": "#f85149"}.get(nodo.tipo, TEXT)

        _label(frm, nodo.nombre, bold=True, size=14).pack(anchor="w")
        tk.Label(frm, text=f"Tipo: {nodo.tipo.upper()}", bg=BG, fg=color,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 8))

        _section(frm, "Rutas aéreas conectadas")
        for vecino, peso in nodo.vecinos:
            if not vecino.excluido:
                tk.Label(frm, text=f"  → {vecino.nombre}   ({peso:.1f} km)",
                         bg=BG, fg=TEXT, font=("Segoe UI", 9)).pack(anchor="w")

        if drones_en_nodo:
            _section(frm, "Drones en este nodo")
            for d in drones_en_nodo:
                bat_color = DANGER if d.bateria < 20 else WARNING if d.bateria < 50 else "#3fb950"
                tk.Label(frm, text=f"  ✈ {d.nombre}  |  {d.estado}  |  bat {d.bateria:.0f}%",
                         bg=BG, fg=bat_color, font=("Segoe UI", 9)).pack(anchor="w")

        tk.Frame(frm, bg=BG, height=10).pack()
        _btn(frm, "Cerrar", dlg.destroy, color=CARD).pack(side="right")


# ─────────────────────────────────────────────────────────────────────────────
# 9. Ver Cola de Pedidos
# ─────────────────────────────────────────────────────────────────────────────

class ColaPedidosDialog:
    """Vista detallada de la Cola FIFO de pedidos pendientes."""

    def __init__(self, parent, cola):
        pedidos = cola.obtener_lista()
        dlg = _make_dialog(parent, "Cola FIFO de Pedidos", 560, 400)
        frm = tk.Frame(dlg, bg=BG, padx=20, pady=14)
        frm.pack(fill="both", expand=True)

        _label(frm, "COLA FIFO — PEDIDOS PENDIENTES", bold=True, size=12).pack(anchor="w")
        _label(frm, f"El primer pedido (frente) será despachado próximamente. Total: {len(pedidos)}", dim=True).pack(anchor="w", pady=(0, 6))

        cols = ("pos", "id", "destino", "solicitante", "prio", "fecha")
        tree = ttk.Treeview(frm, columns=cols, show="headings", height=12, style="Dark.Treeview")
        for c, h, w in zip(cols, ("#", "ID", "Destino", "Solicitante", "Prioridad", "Hora"), (32, 60, 140, 100, 80, 80)):
            tree.heading(c, text=h); tree.column(c, width=w, anchor="center" if c in ("pos","prio") else "w")
        tree.pack(fill="both", expand=True)

        for i, p in enumerate(pedidos):
            tag = "frente" if i == 0 else ""
            tree.insert("", "end",
                        values=(i + 1, f"P{p.id:03d}", p.destino_nombre, p.solicitante,
                                {1: "Normal", 2: "Urgente", 3: "Crítico"}.get(p.prioridad), p.fecha_creacion),
                        tags=(tag,))
        tree.tag_configure("frente", background="#1a2f1a", foreground="#3fb950")

        frm2 = tk.Frame(dlg, bg=BG, padx=20); frm2.pack(fill="x", pady=(0, 10))
        _label(frm2, "Verde = frente de la cola (próximo a despachar).", dim=True).pack(side="left")
        _btn(frm2, "Cerrar", dlg.destroy, color=CARD).pack(side="right")


# ─────────────────────────────────────────────────────────────────────────────
# 10. Visualizar Ruta LDE
# ─────────────────────────────────────────────────────────────────────────────

class RutaDronDialog:
    """Muestra la Lista Doblemente Encadenada de ruta de un dron."""

    def __init__(self, parent, dron):
        dlg = _make_dialog(parent, f"Ruta LDE — {dron.nombre}", 500, 340)
        frm = tk.Frame(dlg, bg=BG, padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        _label(frm, f"LISTA DOBLEMENTE ENCADENADA — {dron.nombre}", bold=True, size=11).pack(anchor="w")
        _label(frm, "Recorrido adelante (cabeza → cola):", dim=True).pack(anchor="w", pady=(4, 2))

        adelante = dron.ruta_entrega.recorrer_adelante()
        if adelante:
            txt = "  ↔  ".join(adelante)
            tk.Label(frm, text=txt, bg=CARD, fg="#58a6ff",
                     font=("Consolas", 10), wraplength=440, justify="left",
                     padx=10, pady=8).pack(fill="x", pady=4)
        else:
            tk.Label(frm, text="(Lista vacía — dron sin ruta asignada)",
                     bg=CARD, fg=DIM, font=("Segoe UI", 10), padx=10, pady=8).pack(fill="x")

        _label(frm, "Recorrido atrás (cola → cabeza):", dim=True).pack(anchor="w", pady=(8, 2))
        atras = dron.ruta_entrega.recorrer_atras()
        if atras:
            txt2 = "  ↔  ".join(atras)
            tk.Label(frm, text=txt2, bg=CARD, fg=WARNING,
                     font=("Consolas", 10), wraplength=440, justify="left",
                     padx=10, pady=8).pack(fill="x", pady=4)

        _label(frm, f"Nodos en la LDE: {dron.ruta_entrega.tamaño}", dim=True).pack(anchor="w", pady=(6, 0))
        _btn(frm, "Cerrar", dlg.destroy, color=CARD).pack(side="right", pady=(10, 0))


# ─────────────────────────────────────────────────────────────────────────────
# 11. Despachar Dron
# ─────────────────────────────────────────────────────────────────────────────

class DespacharDialog:
    """Formulario para configurar un despacho: elige pedido y dron."""

    def __init__(self, parent, pedidos, drones_disponibles, on_confirm):
        """
        pedidos            : list[Pedido] — pedidos en cola (en orden)
        drones_disponibles : list[Dron]   — drones listos para volar
        on_confirm         : callable(pedido, dron)
        """
        dlg = _make_dialog(parent, "Despachar Dron", 460, 260)
        frm = tk.Frame(dlg, bg=BG, padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        _label(frm, "Configurar despacho", bold=True, size=11).pack(anchor="w", pady=(0, 8))

        # ── Pedido ───────────────────────────────────────────────────────────
        r1 = tk.Frame(frm, bg=BG); r1.pack(fill="x", pady=4)
        _label(r1, "Pedido:").pack(side="left")
        ped_labels = [
            f"#{p.id}  {p.origen_nombre} → {p.destino_nombre}  (Prio {p.prioridad})"
            for p in pedidos
        ]
        self.cb_ped = _combo(r1, ped_labels, 32)
        self.cb_ped.pack(side="right")

        # ── Dron ─────────────────────────────────────────────────────────────
        r2 = tk.Frame(frm, bg=BG); r2.pack(fill="x", pady=4)
        _label(r2, "Dron:").pack(side="left")
        dron_labels = [
            f"{d.id}  —  {d.nombre}  ({d.bateria:.0f}% bat.)"
            for d in drones_disponibles
        ]
        self.cb_dron = _combo(r2, dron_labels, 32)
        self.cb_dron.pack(side="right")

        # ── Botones ──────────────────────────────────────────────────────────
        bfrm = tk.Frame(frm, bg=BG); bfrm.pack(fill="x", pady=(16, 0))

        def _confirmar():
            pi = self.cb_ped.current()
            di = self.cb_dron.current()
            if pi < 0 or di < 0:
                messagebox.showwarning("Campos incompletos",
                                       "Selecciona pedido y dron.",
                                       parent=dlg)
                return
            pedido_sel = pedidos[pi]
            dron_sel   = drones_disponibles[di]
            dlg.destroy()
            on_confirm(pedido_sel, dron_sel)

        _btn(bfrm, "Despachar", _confirmar).pack(side="right", padx=(6, 0))
        _btn(bfrm, "Cancelar", dlg.destroy, color=CARD).pack(side="right")
