-- ==========================================
-- SECCIÓN DE MIGRACIONES Y CAMBIOS (HISTORIAL)
-- ==========================================
-- INSTRUCCIONES:
-- 1. NO MODIFICAR las tablas creadas arriba si el sistema ya está en producción.
-- 2. Añade cada nuevo cambio al final de esta sección con su respectiva fecha.
-- 3. Usa bloques "IF NOT EXISTS" o validaciones para mantener el script idempotente.

/* 
-- PLANTILLA PARA NUEVOS CAMBIOS:
-- FECHA: AAAA-MM-DD | Desarrollador: Tu Nombre
-- Descripción: Breve explicación de qué cambia.
-- ----------------------------------------------------
-- Tu código SQL aquí...
*/

-- ----------------------------------------------------
-- EJEMPLO 1: FECHA: 2026-05-16 | Desarrollador: Soporte DB
-- Descripción: Agregar columna 'correo' a la tabla usuarios (Evitando duplicados)
-- ----------------------------------------------------
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='usuarios' AND column_name='correo') THEN
        ALTER TABLE usuarios ADD COLUMN correo VARCHAR(100) UNIQUE;
    END IF;
END $$;


-- ----------------------------------------------------
-- EJEMPLO 2: FECHA: 2026-05-16 | Desarrollador: Soporte DB
-- Descripción: Crear tabla de proveedores (Nueva entidad del sistema)
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE
);


-- ----------------------------------------------------
-- EJEMPLO 3: FECHA: 2026-05-16 | Desarrollador: Soporte DB
-- Descripción: Relacionar la tabla productos con proveedores
-- ----------------------------------------------------
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='productos' AND column_name='id_proveedor') THEN
        -- 1. Agregar la columna que funcionará como llave foránea
        ALTER TABLE productos ADD COLUMN id_proveedor INT;
        
        -- 2. Agregar la restricción de llave foránea (FK)
        ALTER TABLE productos 
        ADD CONSTRAINT fk_productos_proveedores 
        FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor);
    END IF;
END $$;