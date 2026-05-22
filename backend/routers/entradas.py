from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import verificar_token, TokenData

router = APIRouter(prefix="/entradas", tags=["Entradas"])


class RegistroEntrada(BaseModel):
    id_producto: int
    cantidad: int = Field(..., gt=0, description="La cantidad debe ser mayor a 0")
    id_usuario: int


@router.post("/registrar", status_code=status.HTTP_201_CREATED)
def registrar_entrada(
    entrada: RegistroEntrada,
    db: Session = Depends(get_db),
    _usuario: TokenData = Depends(verificar_token),
):
    # 1. Validar que el producto exista
    producto = db.execute(
        text("SELECT id_producto FROM productos WHERE id_producto = :id_prod"),
        {"id_prod": entrada.id_producto}
    ).fetchone()

    if not producto:
        raise HTTPException(status_code=404, detail="El producto especificado no existe.")

    # 2. Validar que el usuario exista
    usuario = db.execute(
        text("SELECT id_usuario FROM usuarios WHERE id_usuario = :id_user"),
        {"id_user": entrada.id_usuario}
    ).fetchone()

    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario especificado no existe.")

    try:
        # 3. Insertar el movimiento
        db.execute(
            text("""
                INSERT INTO movimientos_inventario (id_producto, tipo_movimiento, cantidad, id_usuario)
                VALUES (:id_producto, 'ENTRADA', :cantidad, :id_usuario)
            """),
            {
                "id_producto": entrada.id_producto,
                "cantidad": entrada.cantidad,
                "id_usuario": entrada.id_usuario
            }
        )
        
        # 4. Guardar los cambios
        db.commit()

        # 5. Obtener el stock ya actualizado por la base de datos
        stock_actualizado = db.execute(
            text("SELECT stock_actual FROM productos WHERE id_producto = :id_prod"),
            {"id_prod": entrada.id_producto}
        ).fetchone()

        return {
            "status": "success",
            "mensaje": "Entrada registrada e inventario actualizado correctamente",
            "datos": {
                "id_producto": entrada.id_producto,
                "cantidad_ingresada": entrada.cantidad,
                "nuevo_stock": stock_actualizado.stock_actual
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")
