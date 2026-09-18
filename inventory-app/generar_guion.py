"""
Genera el guion de presentacion de StockMate con bloques separados por persona.
Cada persona tiene sus propias secciones completas sin intercalacion.
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Margenes ──────────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3)
    section.right_margin  = Cm(2.5)

# ── Helpers ───────────────────────────────────────────────────────────────────

AZUL   = RGBColor(0,   70,  127)
ROJO   = RGBColor(180,  0,    0)
GRIS   = RGBColor(100, 100, 100)
NEGRO  = RGBColor(0,   0,    0)
GRIS_O = RGBColor(80,  80,   80)   # titulos bloque

def set_font(run, bold=False, italic=False, size=11, color=None, font="Calibri"):
    run.bold   = bold
    run.italic = italic
    run.font.name  = font
    run.font.size  = Pt(size)
    if color:
        run.font.color.rgb = color

def agregar_titulo_pagina(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(120)
    p.paragraph_format.space_after  = Pt(12)
    r = p.add_run(texto)
    set_font(r, bold=True, size=28, color=RGBColor(0, 51, 102))

def agregar_subtitulo_pagina(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(texto)
    set_font(r, bold=False, size=14, color=GRIS)

def agregar_linea_decorativa(doc):
    """Linea horizontal usando borde inferior de parrafo."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '004680')
    pBdr.append(bottom)
    pPr.append(pBdr)

def agregar_encabezado_bloque(doc, persona_num, titulo, tiempo):
    """Encabezado de cada bloque: numero, titulo y tiempo estimado."""
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after  = Pt(2)
    color_bg = AZUL if persona_num == 1 else ROJO
    etiqueta = f"BLOQUE {_bloque_actual[0]}  —  PERSONA {persona_num}"
    r1 = p.add_run(etiqueta)
    set_font(r1, bold=True, size=12, color=color_bg)
    r2 = p.add_run(f"   [{tiempo}]")
    set_font(r2, bold=False, italic=True, size=10, color=GRIS)

    p2 = doc.add_paragraph()
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after  = Pt(6)
    r3 = p2.add_run(titulo.upper())
    set_font(r3, bold=True, size=13, color=GRIS_O)

    agregar_linea_decorativa(doc)
    _bloque_actual[0] += 1

_bloque_actual = [1]

def agregar_discurso(doc, persona_num, texto):
    """Parrafo de discurso con etiqueta de persona."""
    color = AZUL if persona_num == 1 else ROJO
    etiq  = f"P{persona_num}:  "
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.left_indent  = Cm(0.8)
    r1 = p.add_run(etiq)
    set_font(r1, bold=True, size=11, color=color)
    r2 = p.add_run(texto)
    set_font(r2, size=11, color=NEGRO)

def agregar_acotacion(doc, texto):
    """Acotacion escénica en gris italica."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.left_indent  = Cm(1.2)
    r = p.add_run(f"[ {texto} ]")
    set_font(r, italic=True, size=10, color=GRIS)

def agregar_parrafo_normal(doc, texto):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.left_indent  = Cm(0.8)
    r = p.add_run(texto)
    set_font(r, size=10.5, color=RGBColor(60, 60, 60))

# ══════════════════════════════════════════════════════════════════════════════
# PORTADA
# ══════════════════════════════════════════════════════════════════════════════
agregar_titulo_pagina(doc, "Guion de Presentacion")
p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_sub.add_run("StockMate")
set_font(r, bold=True, size=36, color=RGBColor(0, 51, 102))

agregar_subtitulo_pagina(doc, "Sistema de Gestion de Inventarios para Tiendas Pequenas")
doc.add_paragraph()
agregar_subtitulo_pagina(doc, "Proyecto Final — Patrones de Diseno de Software")
doc.add_paragraph()
agregar_linea_decorativa(doc)
doc.add_paragraph()

p_info = doc.add_paragraph()
p_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p_info.add_run("Dos expositores  |  Duracion estimada: 18-22 minutos")
set_font(r, size=11, color=GRIS)

p_leyenda = doc.add_paragraph()
p_leyenda.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_leyenda.paragraph_format.space_before = Pt(20)
r1 = p_leyenda.add_run("P1")
set_font(r1, bold=True, size=11, color=AZUL)
r2 = p_leyenda.add_run("  =  Persona 1     ")
set_font(r2, size=11, color=NEGRO)
r3 = p_leyenda.add_run("P2")
set_font(r3, bold=True, size=11, color=ROJO)
r4 = p_leyenda.add_run("  =  Persona 2     ")
set_font(r4, size=11, color=NEGRO)
r5 = p_leyenda.add_run("[ acotaciones en gris italico ]")
set_font(r5, italic=True, size=10, color=GRIS)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 1 — BLOQUE 1: INTRODUCCION
# ══════════════════════════════════════════════════════════════════════════════
agregar_encabezado_bloque(doc, 1, "Introduccion general al proyecto", "aprox. 2-3 min")
agregar_acotacion(doc, "Persona 1 empieza la presentacion. Mostrar la pantalla del sistema o el diagrama general.")
agregar_discurso(doc, 1,
    "Buenos dias profesor. Hoy le vamos a presentar StockMate, un sistema de gestion de inventarios "
    "disenado para tiendas pequenas. La idea principal es que cualquier dueno de tienda pueda controlar "
    "su stock, registrar entradas y salidas de productos, y recibir alertas cuando un articulo esta por "
    "agotarse, todo desde una interfaz web facil de usar.")
agregar_discurso(doc, 1,
    "El sistema esta construido con Flask como framework de backend, MySQL como base de datos, "
    "y Bootstrap 5 para el frontend. Todo corre sobre Python y usamos SQLAlchemy como ORM para "
    "interactuar con la base de datos sin escribir SQL directamente.")
agregar_discurso(doc, 1,
    "Una caracteristica importante es que el sistema soporta multiples usuarios: cada cuenta tiene su "
    "propio inventario completamente aislado. Esto lo logramos guardando el ID del usuario en cada "
    "producto mediante un campo llamado created_by, y filtrando todas las consultas por ese campo.")
agregar_discurso(doc, 1,
    "La autenticacion funciona de dos formas: con correo y contrasena tradicionales, o mediante "
    "Google OAuth, para que el usuario pueda iniciar sesion directamente con su cuenta de Google "
    "sin necesidad de registrarse manualmente.")
agregar_acotacion(doc, "Pausa breve. Mostrar el dashboard del sistema.")
agregar_discurso(doc, 1,
    "Aqui pueden ver el dashboard: muestra el total de productos, el valor del inventario, "
    "los productos con stock bajo y un grafico de barras con los movimientos de los ultimos 7 dias. "
    "Las alertas de stock se actualizan automaticamente cada 30 segundos sin necesidad de recargar la pagina.")

# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 1 — BLOQUE 2: PATRON MVC
# ══════════════════════════════════════════════════════════════════════════════
agregar_encabezado_bloque(doc, 1, "Patron de diseno: MVC (Model-View-Controller)", "aprox. 3 min")
agregar_acotacion(doc, "Mostrar la estructura de carpetas del proyecto: app/models, app/controllers, app/templates.")
agregar_discurso(doc, 1,
    "El primer patron que usamos es MVC, que significa Modelo-Vista-Controlador. "
    "Este patron separa la aplicacion en tres capas con responsabilidades distintas "
    "para que el codigo sea mas organizado y facil de mantener.")
agregar_discurso(doc, 1,
    "Los Modelos estan en la carpeta app/models y representan la estructura de la base de datos. "
    "Por ejemplo, el modelo Product define los campos del producto: nombre, descripcion, SKU, cantidad, "
    "precio de compra, precio de venta, categoria, y el created_by que mencionamos antes. "
    "Tambien tiene una propiedad calculada llamada is_low_stock que devuelve True si el stock "
    "es menor o igual al minimo definido.")
agregar_discurso(doc, 1,
    "Las Vistas son los archivos HTML en app/templates, que usan el motor de plantillas Jinja2 de Flask. "
    "Hay una plantilla base llamada base.html que contiene el sidebar de navegacion, la barra superior "
    "y el panel de alertas, y las demas paginas extienden esa base mediante bloques de contenido.")
agregar_discurso(doc, 1,
    "Los Controladores estan en app/controllers y son los que reciben las peticiones HTTP, "
    "consultan los datos que necesitan, y devuelven la vista correspondiente. Por ejemplo, "
    "el controlador de productos en products.py maneja el listado, la creacion, la edicion "
    "y la eliminacion de productos, cada uno en su propia funcion decorada con la ruta Flask correspondiente.")
agregar_acotacion(doc, "Mostrar rapidamente el archivo products.py en el editor.")
agregar_discurso(doc, 1,
    "La ventaja de este patron es clara: si queremos cambiar como se muestran los productos, "
    "solo tocamos el HTML de la vista. Si queremos cambiar la logica de negocio, solo tocamos "
    "el controlador. Y si cambia la base de datos, solo modificamos el modelo. Las tres partes "
    "son independientes entre si.")

# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 1 — BLOQUE 3: PATRON SINGLETON
# ══════════════════════════════════════════════════════════════════════════════
agregar_encabezado_bloque(doc, 1, "Patron de diseno: Singleton", "aprox. 2 min")
agregar_acotacion(doc, "Mostrar el archivo config.py.")
agregar_discurso(doc, 1,
    "El segundo patron que implementamos es el Singleton. Este patron garantiza que una clase "
    "tenga una sola instancia durante toda la ejecucion del programa, y que esa instancia sea "
    "accesible globalmente.")
agregar_discurso(doc, 1,
    "En nuestro proyecto lo usamos en la clase Config, que carga la configuracion del sistema: "
    "la clave secreta de Flask, los datos de conexion a MySQL, la configuracion del correo para "
    "las notificaciones, y las credenciales de Google OAuth.")
agregar_discurso(doc, 1,
    "La implementacion usa un atributo de clase llamado _instance. Cuando se llama al constructor, "
    "primero revisa si _instance es None. Si lo es, crea la instancia y la guarda ahi. "
    "Si ya existe, simplemente devuelve la misma instancia que ya fue creada. "
    "Eso garantiza que no haya configuraciones duplicadas ni inconsistentes en distintas partes del sistema.")
agregar_discurso(doc, 1,
    "Esto es importante porque la configuracion se lee desde un archivo .env una sola vez al arrancar, "
    "y no queremos que distintas partes de la aplicacion tengan versiones diferentes de esa configuracion.")

# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 1 — BLOQUE 4: PATRON REPOSITORY
# ══════════════════════════════════════════════════════════════════════════════
agregar_encabezado_bloque(doc, 1, "Patron de diseno: Repository", "aprox. 2-3 min")
agregar_acotacion(doc, "Mostrar la carpeta app/repositories y abrir base_repo.py.")
agregar_discurso(doc, 1,
    "El tercer patron que implementamos es el Repository. La idea de este patron es crear "
    "una capa intermedia entre los controladores y la base de datos, de modo que el controlador "
    "no tenga que saber como funcionan las consultas SQL internamente.")
agregar_discurso(doc, 1,
    "Tenemos una clase base llamada BaseRepository que define las operaciones comunes: "
    "get_by_id para buscar por ID, get_all para traer todos los registros, save para guardar "
    "uno nuevo, delete para eliminar, y commit para confirmar los cambios en la base de datos. "
    "Todas estas operaciones las hereda cualquier repositorio concreto.")
agregar_discurso(doc, 1,
    "Luego tenemos repositorios especificos que extienden esa base. Por ejemplo, ProductRepository "
    "agrega metodos propios como get_active para traer solo los productos activos, "
    "get_low_stock para los que tienen stock bajo, get_by_category para filtrar por categoria, "
    "y search para buscar por nombre o SKU. Todos esos metodos reciben un user_id para "
    "asegurarse de devolver solo los datos del usuario autenticado.")
agregar_discurso(doc, 1,
    "MovementRepository tiene su propio metodo get_recent que devuelve los movimientos "
    "de los ultimos N dias, tambien filtrado por usuario haciendo un JOIN con la tabla de productos.")
agregar_discurso(doc, 1,
    "La ventaja de este patron es que si en el futuro decidimos cambiar de MySQL a otro motor "
    "de base de datos, solo hay que modificar los repositorios. Los controladores no cambian en absoluto "
    "porque siguen llamando a los mismos metodos del repositorio.")
agregar_acotacion(doc, "Pausa. Mirar al profesor. Ceder la palabra a Persona 2.")
agregar_discurso(doc, 1,
    "Con esto cubro los primeros tres patrones de diseno y la arquitectura base del sistema. "
    "Ahora mi companero va a explicar los tres patrones restantes y las funcionalidades avanzadas del sistema.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 2 — BLOQUE 5: PATRON OBSERVER
# ══════════════════════════════════════════════════════════════════════════════
agregar_encabezado_bloque(doc, 2, "Patron de diseno: Observer", "aprox. 3 min")
agregar_acotacion(doc, "Persona 2 toma la palabra. Mostrar app/observers/stock_observer.py.")
agregar_discurso(doc, 2,
    "Gracias. Voy a continuar con los patrones de diseno. El cuarto patron que implementamos "
    "es el Observer, que tambien se conoce como patron de publicacion-suscripcion. "
    "La idea es que cuando ocurre un evento importante, el sistema lo notifica automaticamente "
    "a todos los componentes interesados, sin que esos componentes esten acoplados entre si.")
agregar_discurso(doc, 2,
    "En StockMate lo usamos para las alertas de stock bajo. Tenemos una clase llamada StockSubject "
    "que actua como el sujeto que emite eventos. Esta clase mantiene una lista de observadores "
    "registrados y tiene un metodo check_and_notify que se llama cada vez que se registra "
    "un movimiento de inventario.")
agregar_discurso(doc, 2,
    "Cuando check_and_notify detecta que el stock de un producto cayo por debajo del minimo, "
    "recorre la lista de observadores y llama al metodo update de cada uno, pasandole "
    "los datos del producto afectado.")
agregar_acotacion(doc, "Mostrar alert_strategies.py.")
agregar_discurso(doc, 2,
    "Los observadores concretos son tres. El primero es DatabaseAlertObserver, que guarda "
    "la alerta en la tabla stock_alerts de la base de datos con la cantidad actual y el minimo "
    "configurado. El segundo es EmailAlertObserver, que envia un correo al administrador usando "
    "Flask-Mail avisando que ese producto necesita reabastecerse. El tercero es ScreenAlertObserver, "
    "que registra el evento en los logs del servidor.")
agregar_discurso(doc, 2,
    "Hay una instancia global llamada stock_subject que se crea al arrancar la aplicacion "
    "con los tres observadores ya registrados. Desde cualquier parte del codigo, cuando se "
    "registra un movimiento, simplemente se llama stock_subject.check_and_notify y el sistema "
    "se encarga del resto automaticamente.")
agregar_discurso(doc, 2,
    "La ventaja de este diseno es que es completamente extensible: si manana queremos agregar "
    "un observador que mande un mensaje de WhatsApp o un SMS, solo creamos una nueva clase "
    "que implemente el metodo update y la registramos. No hay que tocar el codigo existente.")

# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 2 — BLOQUE 6: PATRON FACTORY METHOD
# ══════════════════════════════════════════════════════════════════════════════
agregar_encabezado_bloque(doc, 2, "Patron de diseno: Factory Method", "aprox. 2-3 min")
agregar_acotacion(doc, "Mostrar app/factories/report_factory.py.")
agregar_discurso(doc, 2,
    "El quinto patron es el Factory Method. Este patron define una interfaz para crear objetos, "
    "pero delega la decision de que clase instanciar a una fabrica centralizada. "
    "El codigo que necesita el objeto no sabe ni le importa como fue creado.")
agregar_discurso(doc, 2,
    "En el proyecto lo usamos para el modulo de reportes. Hay una clase abstracta llamada BaseReport "
    "con un metodo generate que todos los tipos de reporte deben implementar. "
    "Luego tenemos tres clases concretas: MovementReport que genera el historial de entradas y salidas, "
    "PopularProductsReport que calcula los productos mas vendidos usando una consulta de agregacion, "
    "y LowStockReport que lista todos los productos por debajo de su stock minimo.")
agregar_discurso(doc, 2,
    "La clase ReportFactory tiene un diccionario interno llamado _registry que mapea un nombre "
    "como movements, popular o low_stock a su clase correspondiente. El metodo create recibe "
    "el nombre del reporte, busca la clase en el diccionario, la instancia y la devuelve. "
    "Si el tipo no existe, lanza un ValueError.")
agregar_discurso(doc, 2,
    "La gran ventaja es la extensibilidad. Si manana el profesor nos pide un cuarto tipo de reporte, "
    "por ejemplo un reporte de ganancias, solo creamos la clase GananciasReport que extienda "
    "BaseReport, implementamos su metodo generate, y agregamos una linea al diccionario _registry. "
    "No hay que modificar el controlador ni la vista.")
agregar_acotacion(doc, "Mostrar el selector de tipos de reporte en la pagina web.")

# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 2 — BLOQUE 7: PATRON STRATEGY
# ══════════════════════════════════════════════════════════════════════════════
agregar_encabezado_bloque(doc, 2, "Patron de diseno: Strategy", "aprox. 2 min")
agregar_acotacion(doc, "Mostrar app/controllers/reports.py.")
agregar_discurso(doc, 2,
    "El sexto y ultimo patron de diseno es el Strategy. Este patron permite definir una familia "
    "de algoritmos intercambiables y elegir cual usar en tiempo de ejecucion, sin que el cliente "
    "tenga que saber los detalles de cada algoritmo.")
agregar_discurso(doc, 2,
    "Nosotros lo aplicamos a la exportacion de reportes. El mismo reporte puede exportarse "
    "en tres formatos distintos segun un parametro en la URL llamado fmt. "
    "Si fmt es html, se renderiza la pagina web normal con la tabla y el grafico. "
    "Si fmt es csv, se genera un archivo descargable separado por comas. "
    "Si fmt es json, se devuelve la informacion como objeto JSON para integracion con otras aplicaciones.")
agregar_discurso(doc, 2,
    "En el controlador, esto se implementa con tres ramas de codigo: la funcion index revisa "
    "el valor de fmt y llama a la estrategia correspondiente. La exportacion CSV esta en una funcion "
    "llamada _export_csv que maneja cada tipo de reporte por separado con sus columnas correctas. "
    "La exportacion JSON usa _make_serializable para convertir los objetos de SQLAlchemy a "
    "diccionarios simples que se puedan serializar.")
agregar_discurso(doc, 2,
    "Esto es exactamente el patron Strategy: el mismo dato, tres algoritmos de salida distintos, "
    "seleccionados dinamicamente segun la necesidad del usuario.")

# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 2 — BLOQUE 8: FUNCIONALIDADES PRINCIPALES
# ══════════════════════════════════════════════════════════════════════════════
agregar_encabezado_bloque(doc, 2, "Funcionalidades principales del sistema", "aprox. 3 min")
agregar_acotacion(doc, "Navegar por las pantallas del sistema mientras se explica.")
agregar_discurso(doc, 2,
    "Ademas de los patrones de diseno, quiero mostrarle rapidamente las funcionalidades "
    "mas importantes del sistema para que tenga una vision completa de lo que se construyo.")
agregar_discurso(doc, 2,
    "La autenticacion soporta dos metodos. El primero es el registro e inicio de sesion "
    "tradicional con correo y contrasena, usando Werkzeug para el hash seguro de contrasenas "
    "y Flask-Login para gestionar la sesion. El segundo es Google OAuth 2.0 mediante la libreria "
    "Authlib: el usuario hace clic en Iniciar sesion con Google, se autentica en la cuenta de "
    "Google, y el sistema crea o recupera automaticamente su perfil local.")
agregar_acotacion(doc, "Mostrar pantalla de login con el boton de Google.")
agregar_discurso(doc, 2,
    "El inventario esta completamente aislado por usuario. Cuando alguien crea un producto, "
    "se guarda con su user ID en el campo created_by. Todas las consultas — tanto en los "
    "repositorios como en los reportes y el dashboard — filtran por ese campo, "
    "asi que cada usuario ve unicamente sus propios datos.")
agregar_discurso(doc, 2,
    "El dashboard muestra cuatro indicadores clave: total de productos activos, "
    "cantidad de productos con stock bajo, valor total del inventario calculado como "
    "la suma de cantidad por precio de compra de cada producto, y un grafico de barras "
    "con las entradas y salidas de los ultimos 7 dias generado con Chart.js.")
agregar_discurso(doc, 2,
    "El sistema de alertas funciona en tiempo real. Cada 30 segundos, el JavaScript de la pagina "
    "hace una peticion al endpoint /api/alerts para revisar si hay alertas no leidas. "
    "Si las hay, actualiza el contador en la campana del topbar y las muestra en un panel "
    "lateral. El usuario puede marcar alertas individuales como leidas o limpiarlas todas de una vez.")
agregar_acotacion(doc, "Abrir el panel de alertas y mostrar como funciona.")

# ══════════════════════════════════════════════════════════════════════════════
# PERSONA 2 — BLOQUE 9: CIERRE Y CONCLUSIONES
# ══════════════════════════════════════════════════════════════════════════════
agregar_encabezado_bloque(doc, 2, "Cierre y conclusiones", "aprox. 1-2 min")
agregar_acotacion(doc, "Ambos expositores de frente al profesor para el cierre.")
agregar_discurso(doc, 2,
    "Para cerrar, StockMate es un sistema completo que implementa seis patrones de diseno "
    "de forma practica y justificada: MVC para la arquitectura general, Singleton para la "
    "configuracion, Repository para el acceso a datos, Observer para las notificaciones, "
    "Factory Method para la creacion de reportes, y Strategy para la exportacion de datos.")
agregar_discurso(doc, 2,
    "Cada patron fue elegido porque resuelve un problema real del sistema, no solo como ejercicio "
    "academico. El resultado es una aplicacion extensible: agregar un nuevo tipo de reporte, "
    "un nuevo formato de exportacion o un nuevo canal de notificacion requiere minimos cambios "
    "en el codigo existente.")
agregar_discurso(doc, 2,
    "Quedamos a disposicion para cualquier pregunta sobre la implementacion, "
    "la base de datos, los patrones o cualquier parte del codigo. Muchas gracias.")
agregar_acotacion(doc, "Fin de la presentacion. Disponibles para preguntas.")

# ══════════════════════════════════════════════════════════════════════════════
# GUARDAR
# ══════════════════════════════════════════════════════════════════════════════
ruta = r"C:\Users\andre\Downloads\Guion_StockMate_v2.docx"
doc.save(ruta)
print(f"Guardado en: {ruta}")
