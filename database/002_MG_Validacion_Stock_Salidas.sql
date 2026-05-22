-- ==========================================
-- Migración: Validación de stock en SALIDA
-- ==========================================
-- Descripción: Modifica fn_actualizar_stock()
-- para que valide que hay stock suficiente
-- antes de permitir una SALIDA.
-- ==========================================

CREATE OR REPLACE FUNCTION fn_actualizar_stock()
RETURNS TRIGGER AS $$
DECLARE
    stock_actual_int INT;
BEGIN
    IF NEW.tipo_movimiento = 'ENTRADA' THEN
        UPDATE productos 
        SET stock_actual = stock_actual + NEW.cantidad 
        WHERE id_producto = NEW.id_producto;

    ELSIF NEW.tipo_movimiento = 'SALIDA' THEN
        -- Validar stock disponible antes de restar
        SELECT stock_actual INTO stock_actual_int 
        FROM productos 
        WHERE id_producto = NEW.id_producto;

        IF stock_actual_int < NEW.cantidad THEN
            RAISE EXCEPTION 'Stock insuficiente para el producto %: disponible %, solicitado %',
                NEW.id_producto, stock_actual_int, NEW.cantidad;
        END IF;

        UPDATE productos 
        SET stock_actual = stock_actual - NEW.cantidad 
        WHERE id_producto = NEW.id_producto;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
