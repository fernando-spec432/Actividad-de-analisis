from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import verificar_token
from schemas import TokenData

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("/stock-bajo")
def obtener_alertas_stock_bajo(
    db: Session = Depends(get_db),
    _usuario: TokenData = Depends(verificar_token),
):
    resultado = db.execute(text("""
        SELECT 
            id_producto,
            codigo_unico,
            nombre,
            stock_actual,
            stock_minimo_alerta
        FROM v_alertas_stock
        ORDER BY stock_actual ASC
    """))

    return [
        {
            "id_producto": fila.id_producto,
            "codigo_unico": fila.codigo_unico,
            "nombre": fila.nombre,
            "stock_actual": fila.stock_actual,
            "stock_minimo_alerta": fila.stock_minimo_alerta,
            "estado": "Stock bajo"
        }
        for fila in resultado
    ]