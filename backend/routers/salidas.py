from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import verificar_token, TokenData
from schemas import RegistroSalida

router = APIRouter(prefix="/salidas", tags=["Salidas"])


@router.post("/registrar", status_code=status.HTTP_201_CREATED)
def registrar_salida(
    salida: RegistroSalida,
    db: Session = Depends(get_db),
    _usuario: TokenData = Depends(verificar_token),
):
    producto = db.execute(
        text("SELECT id_producto, stock_actual FROM productos WHERE id_producto = :id_prod"),
        {"id_prod": salida.id_producto}
    ).fetchone()

    if not producto:
        raise HTTPException(status_code=404, detail="El producto especificado no existe.")

    usuario = db.execute(
        text("SELECT id_usuario FROM usuarios WHERE id_usuario = :id_user"),
        {"id_user": salida.id_usuario}
    ).fetchone()

    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario especificado no existe.")

    if producto.stock_actual < salida.cantidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente: disponible {producto.stock_actual}, solicitado {salida.cantidad}"
        )

    try:
        db.execute(
            text("""
                INSERT INTO movimientos_inventario (id_producto, tipo_movimiento, cantidad, id_usuario)
                VALUES (:id_producto, 'SALIDA', :cantidad, :id_usuario)
            """),
            {
                "id_producto": salida.id_producto,
                "cantidad": salida.cantidad,
                "id_usuario": salida.id_usuario
            }
        )

        db.commit()

        stock_actualizado = db.execute(
            text("SELECT stock_actual FROM productos WHERE id_producto = :id_prod"),
            {"id_prod": salida.id_producto}
        ).fetchone()

        return {
            "status": "success",
            "mensaje": "Salida registrada e inventario actualizado correctamente",
            "datos": {
                "id_producto": salida.id_producto,
                "cantidad_salida": salida.cantidad,
                "nuevo_stock": stock_actualizado.stock_actual
            }
        }

    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "Stock insuficiente" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {error_msg}")
