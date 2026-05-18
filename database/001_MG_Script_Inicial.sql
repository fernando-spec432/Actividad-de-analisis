--Script inicial para Base de Datos proyecto control_inventario_db
-- ==========================================
-- IMPORTANTE
-- ==========================================
--	1. Instalar postgreSQL en entorno desarrollador
--	2. Configurar usuario y contrasena, si es nuevo se sugiere:
--		usuario: 	localhost
--		pass:		pass1234

-- ==========================================
-- Crear base de datos manual:
-- ==========================================
-- 1. Click derecho en databases: Create: Database:
-- 2. Nombre: control_inventario_db
-- 3. Click en Save.


-- ==========================================
-- ESTRUCTURA DE TIPOS PERSONALIZADOS
-- ==========================================

-- Crear el tipo ENUM para movimientos (solo si no existe)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_movimiento_enum') THEN
        CREATE TYPE tipo_movimiento_enum AS ENUM ('ENTRADA', 'SALIDA');
    END IF;
END $$;

-- ==========================================
-- ESTRUCTURA DE TABLAS (Idempotente)
-- ==========================================

CREATE TABLE IF NOT EXISTS roles (
    id_col SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    id_rol INT NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_rol) REFERENCES roles(id_col)
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto SERIAL PRIMARY KEY,
    codigo_unico VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    stock_actual INT DEFAULT 0,
    stock_minimo_alerta INT DEFAULT 5,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id_movimiento SERIAL PRIMARY KEY,
    id_producto INT NOT NULL,
    tipo_movimiento tipo_movimiento_enum NOT NULL, -- Uso del ENUM de Postgres
    cantidad INT NOT NULL,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- ==========================================
-- FUNCIONES Y TRIGGERS (Lógica Automatizada)
-- ==========================================

-- 1. Función para actualizar stock
CREATE OR REPLACE FUNCTION fn_actualizar_stock()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.tipo_movimiento = 'ENTRADA' THEN
        UPDATE productos 
        SET stock_actual = stock_actual + NEW.cantidad 
        WHERE id_producto = NEW.id_producto;
    ELSIF NEW.tipo_movimiento = 'SALIDA' THEN
        UPDATE productos 
        SET stock_actual = stock_actual - NEW.cantidad 
        WHERE id_producto = NEW.id_producto;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Creación del Trigger único (En Postgres, si ya existe el trigger, se debe borrar o validar)
DROP TRIGGER IF EXISTS trg_actualizar_stock ON movimientos_inventario;

CREATE TRIGGER trg_actualizar_stock
AFTER INSERT ON movimientos_inventario
FOR EACH ROW
EXECUTE FUNCTION fn_actualizar_stock();

-- ==========================================
-- VISTAS
-- ==========================================

CREATE OR REPLACE VIEW v_alertas_stock AS
SELECT id_producto, codigo_unico, nombre, stock_actual, stock_minimo_alerta
FROM productos
WHERE stock_actual <= stock_minimo_alerta;

-- ==========================================
-- SEMILLAS (Datos iniciales idempotentes)
-- ==========================================

-- Insertar roles (si el ID ya existe, no hace nada)
INSERT INTO roles (id_col, nombre_rol) VALUES 
(1, 'Administrador'), 
(2, 'Bodeguero'), 
(3, 'Empleado')
ON CONFLICT (id_col) DO NOTHING;

-- Ajustar la secuencia del autoincrementable de roles para evitar colisiones futuras
SELECT setval(pg_get_serial_sequence('roles', 'id_col'), COALESCE(MAX(id_col), 1)) FROM roles;

-- Insertar usuarios (si el username ya existe, no hace nada)
INSERT INTO usuarios (username, password_hash, id_rol) VALUES 
('admin', 'admin123', 1), 
('bodega', 'bodega123', 2)
ON CONFLICT (username) DO NOTHING;