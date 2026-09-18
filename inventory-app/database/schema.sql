-- =============================================================
-- Sistema de Gestion de Inventarios
-- Schema MySQL
-- =============================================================

CREATE DATABASE IF NOT EXISTS inventory_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE inventory_db;

-- -------------------------------------------------------------
-- Usuarios
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id            INT PRIMARY KEY AUTO_INCREMENT,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),                   -- NULL si usa Google OAuth
    google_id     VARCHAR(255) UNIQUE,            -- ID de Google OAuth
    avatar_url    VARCHAR(512),
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- Categorias de productos
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------------------------------------
-- Productos
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id             INT PRIMARY KEY AUTO_INCREMENT,
    name           VARCHAR(255) NOT NULL,
    description    TEXT,
    sku            VARCHAR(100) UNIQUE,           -- codigo de referencia
    quantity       INT NOT NULL DEFAULT 0,
    min_stock      INT NOT NULL DEFAULT 5,        -- umbral para alerta de stock bajo
    purchase_price DECIMAL(10,2) NOT NULL,
    sale_price     DECIMAL(10,2) NOT NULL,
    category_id    INT,
    created_by     INT NOT NULL,
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by)  REFERENCES users(id)
);

-- -------------------------------------------------------------
-- Movimientos de inventario (entradas y salidas)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_movements (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    product_id      INT NOT NULL,
    user_id         INT NOT NULL,
    movement_type   ENUM('entry', 'exit') NOT NULL,  -- entry=entrada, exit=salida/venta
    quantity        INT NOT NULL,
    quantity_before INT NOT NULL,                     -- stock antes del movimiento
    quantity_after  INT NOT NULL,                     -- stock despues del movimiento
    unit_price      DECIMAL(10,2),                    -- precio unitario en el momento
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (user_id)    REFERENCES users(id)
);

-- -------------------------------------------------------------
-- Alertas generadas por stock bajo
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_alerts (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    product_id  INT NOT NULL,
    quantity    INT NOT NULL,       -- stock en el momento de la alerta
    min_stock   INT NOT NULL,       -- umbral configurado
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- -------------------------------------------------------------
-- Indices para mejorar rendimiento en consultas frecuentes
-- -------------------------------------------------------------
CREATE INDEX idx_products_category  ON products(category_id);
CREATE INDEX idx_products_quantity  ON products(quantity);
CREATE INDEX idx_movements_product  ON stock_movements(product_id);
CREATE INDEX idx_movements_date     ON stock_movements(created_at);
CREATE INDEX idx_alerts_read        ON stock_alerts(is_read);

-- -------------------------------------------------------------
-- Datos iniciales: categorias por defecto
-- -------------------------------------------------------------
INSERT INTO categories (name, description) VALUES
    ('General',     'Productos sin categoria especifica'),
    ('Alimentos',   'Productos alimenticios'),
    ('Bebidas',     'Bebidas y liquidos'),
    ('Limpieza',    'Articulos de limpieza e higiene'),
    ('Electronicos','Equipos y accesorios electronicos'),
    ('Ropa',        'Prendas de vestir y accesorios');
