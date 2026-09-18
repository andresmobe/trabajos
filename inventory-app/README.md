# StockMate — Sistema de Gestión de Inventarios

Aplicación web para pequeños comerciantes que permite registrar, actualizar, consultar y controlar su inventario de productos en tiempo real.

---

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11 + Flask 3.0 |
| Base de datos | MySQL 8 + SQLAlchemy ORM |
| Autenticación | Flask-Login + Google OAuth 2.0 (Authlib) |
| Frontend | HTML5, Bootstrap 5.3, Chart.js 4 |
| Email | Flask-Mail (SMTP) |

---

## Estructura del Proyecto

```
inventory_app/
├── app/
│   ├── __init__.py          # Application Factory (Flask)
│   ├── extensions.py        # Instancias compartidas (db, mail, oauth)
│   ├── models/              # Modelos SQLAlchemy (MVC – Model)
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── movement.py
│   │   └── alert.py
│   ├── repositories/        # Patrón Repository
│   │   ├── base_repo.py
│   │   ├── product_repo.py
│   │   ├── user_repo.py
│   │   └── movement_repo.py
│   ├── observers/           # Patrón Observer + Strategy
│   │   ├── stock_observer.py
│   │   └── alert_strategies.py
│   ├── factories/           # Patrón Factory Method
│   │   └── report_factory.py
│   ├── services/            # Capa de servicio (orquestación)
│   │   └── inventory_service.py
│   ├── controllers/         # Blueprints Flask (MVC – Controller)
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── products.py
│   │   ├── movements.py
│   │   ├── reports.py
│   │   └── categories.py
│   ├── templates/           # Plantillas Jinja2 (MVC – View)
│   └── static/              # CSS y JS
├── database/
│   └── schema.sql           # Script de base de datos MySQL
├── config.py                # Configuración Singleton
├── run.py                   # Punto de entrada
└── requirements.txt
```

---

## Patrones de Diseño Implementados

### 1. MVC — Model-View-Controller *(Arquitectura general)*

**Propósito:** Separar las responsabilidades de datos, presentación y lógica de control en tres capas independientes.

**Aplicación en el proyecto:**

| Capa | Implementación | Archivos |
|------|---------------|---------|
| **Model** | Clases SQLAlchemy que representan tablas y relaciones | `app/models/*.py` |
| **View** | Plantillas Jinja2 que renderizan HTML con datos del contexto | `app/templates/**/*.html` |
| **Controller** | Blueprints Flask que reciben peticiones HTTP y coordinan Model+View | `app/controllers/*.py` |

```python
# Controller (products.py) — recibe la petición, llama al repositorio y pasa datos a la vista
@products_bp.route("/")
@login_required
def list_products():
    products = product_repo.get_active()           # consulta al Model
    return render_template("products/list.html",   # devuelve la View
                           products=products)
```

**Beneficio:** Cada capa puede evolucionar independientemente. Cambiar de Jinja2 a React o de MySQL a PostgreSQL no afecta a las otras capas.

---

### 2. Singleton *(Configuración única)*

**Propósito:** Garantizar que solo exista **una instancia** de la clase `Config` en toda la aplicación, evitando múltiples lecturas del archivo `.env` y asegurando consistencia.

**Aplicación en el proyecto:** `config.py`

```python
class Config:
    _instance = None                          # única referencia a la instancia

    def __new__(cls):
        if cls._instance is None:             # solo se crea una vez
            cls._instance = super().__new__(cls)
            cls._instance._initialize()       # lee .env una sola vez
        return cls._instance                  # siempre retorna la misma instancia

def get_config():
    return Config()   # llamadas múltiples → misma instancia
```

**Beneficio:** Toda la app comparte la misma configuración sin duplicar lecturas de disco ni crear inconsistencias entre instancias.

---

### 3. Observer *(Alertas de stock bajo)*

**Propósito:** Definir una relación uno-a-muchos entre objetos para que, cuando el **Sujeto** cambie de estado, todos sus **Observadores** sean notificados automáticamente sin acoplamiento directo.

**Aplicación en el proyecto:** `app/observers/`

```
StockSubject (Sujeto)
    ├── DatabaseAlertObserver  → persiste la alerta en stock_alerts
    ├── EmailAlertObserver     → envía correo al administrador
    └── ScreenAlertObserver    → puede mostrar mensaje en sesión
```

```python
# stock_observer.py – Sujeto
class StockSubject:
    def attach(self, observer): ...
    def notify(self, product):
        for observer in self._observers:
            observer.update(product)      # notifica a todos
    def check_and_notify(self, product):
        if product.is_low_stock:
            self.notify(product)          # solo si stock bajo

# inventory_service.py – dispara la notificación tras cada movimiento
inv_service.register_movement(...)
stock_subject.check_and_notify(product)  # ← Observer en acción
```

**Beneficio:** Agregar un nuevo canal de notificación (SMS, Telegram, webhook) solo requiere crear una nueva clase que implemente `StockObserver.update()`, sin modificar el código existente.

---

### 4. Factory Method *(Generación de reportes)*

**Propósito:** Definir una interfaz para crear objetos, dejando que las subclases decidan qué clase instanciar. Desacopla al cliente (controlador) de las clases concretas de reporte.

**Aplicación en el proyecto:** `app/factories/report_factory.py`

```python
# Interfaz base
class BaseReport(ABC):
    @abstractmethod
    def generate(self, days: int) -> dict: ...

# Implementaciones concretas
class MovementReport(BaseReport):     ...   # movimientos del periodo
class PopularProductsReport(BaseReport): ... # productos más vendidos
class LowStockReport(BaseReport):     ...   # productos bajo mínimo

# Factory — el controlador no importa las clases concretas
class ReportFactory:
    _registry = {
        "movements": MovementReport,
        "popular":   PopularProductsReport,
        "low_stock": LowStockReport,
    }
    @classmethod
    def create(cls, report_type: str) -> BaseReport:
        return cls._registry[report_type]()   # crea el objeto correcto

# Uso en reports.py
report = ReportFactory.create(report_type)    # ← Factory en acción
data   = report.generate(days=30)
```

**Beneficio:** Agregar un nuevo tipo de reporte (ej. `InventoryValueReport`) solo requiere una nueva clase y una línea en `_registry`, sin tocar el controlador.

---

### 5. Repository *(Acceso a datos)*

**Propósito:** Abstraer la capa de persistencia detrás de una interfaz de colección, separando la lógica de negocio del ORM/SQL.

**Aplicación en el proyecto:** `app/repositories/`

```python
# BaseRepository – operaciones genéricas CRUD
class BaseRepository:
    def get_by_id(self, id): ...
    def get_all(self): ...
    def save(self, instance): ...
    def delete(self, instance): ...

# ProductRepository – consultas específicas de productos
class ProductRepository(BaseRepository):
    def get_low_stock(self): ...    # productos bajo mínimo
    def search(self, term): ...     # búsqueda por nombre/SKU
    def update_quantity(self, product, delta): ...

# Los controladores usan el repositorio, no SQLAlchemy directamente
product_repo = ProductRepository()
products = product_repo.get_active()   # ← Repository en acción
```

**Beneficio:** Los controladores son independientes de SQLAlchemy. Si se migra a otra base de datos o a una API REST, solo cambia el repositorio, no los controladores ni los servicios.

---

### 6. Strategy *(Exportación de reportes)*

**Propósito:** Definir una familia de algoritmos intercambiables encapsulados, permitiendo variar el algoritmo de forma independiente del cliente.

**Aplicación en el proyecto:** `app/controllers/reports.py`

```
ExportStrategy (implícita)
    ├── HTML  → render_template(...)       respuesta web normal
    ├── CSV   → _export_csv(...)           descarga de archivo
    └── JSON  → jsonify(...)               API para integraciones
```

```python
# El parámetro ?fmt= selecciona la estrategia en tiempo de ejecución
@reports_bp.route("/")
def index():
    fmt = request.args.get("fmt", "html")

    if fmt == "json":   return _export_json(data)  # Estrategia JSON
    if fmt == "csv":    return _export_csv(data)   # Estrategia CSV
    return render_template(...)                     # Estrategia HTML
```

**Beneficio:** Agregar una exportación a PDF o Excel no requiere modificar la lógica del reporte, solo agregar una nueva rama/estrategia.

---

## Instalación y Ejecución

### 1. Clonar y crear entorno virtual

```bash
cd inventory_app
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
copy .env.example .env
# Editar .env con tus credenciales de MySQL, Google OAuth y SMTP
```

### 3. Crear la base de datos MySQL

```sql
-- En MySQL Workbench o CLI:
source database/schema.sql
```

### 4. Ejecutar la aplicación

```bash
python run.py
```

La app estará disponible en **http://localhost:5000**

---

## Configurar Google OAuth

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear proyecto → APIs y servicios → Credenciales
3. Crear **ID de cliente OAuth 2.0** (tipo: Aplicación web)
4. URI de redirección autorizada: `http://localhost:5000/auth/google/callback`
5. Copiar **Client ID** y **Client Secret** al archivo `.env`

---

## Funcionalidades

| Módulo | Funcionalidad |
|--------|--------------|
| **Autenticación** | Registro, login email/password, Google OAuth, cierre de sesión |
| **Productos** | CRUD completo, búsqueda, filtro por categoría, margen de ganancia |
| **Movimientos** | Entradas y salidas con validación de stock, historial completo |
| **Alertas** | Automáticas por Observer, polling en tiempo real (30s), panel offcanvas |
| **Reportes** | Movimientos, más vendidos, stock bajo; exportación CSV/JSON |
| **Categorías** | CRUD de categorías de productos |
| **Dashboard** | Métricas generales, gráfica de 7 días, stock crítico, movimientos recientes |
