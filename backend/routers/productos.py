from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import verificar_token
from schemas import ProductoCrear, ProductoEditar, TokenData

router = APIRouter(prefix="/productos", tags=["Productos"])


def _fila_a_dict(fila) -> dict:
    return {
        "id_producto": fila.id_producto,
        "codigo_unico": fila.codigo_unico,
        "nombre": fila.nombre,
        "descripcion": fila.descripcion,
        "stock_actual": fila.stock_actual,
        "stock_minimo_alerta": fila.stock_minimo_alerta,
        "fecha_creacion": str(fila.fecha_creacion),
    }


@router.get("/")
def obtener_productos(
    db: Session = Depends(get_db),
    _usuario: TokenData = Depends(verificar_token),
):
    resultado = db.execute(
        text("""
            SELECT id_producto, codigo_unico, nombre, descripcion,
                   stock_actual, stock_minimo_alerta, fecha_creacion
            FROM productos
            ORDER BY id_producto
        """)
    )
    return [_fila_a_dict(fila) for fila in resultado]


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_producto(
    producto: ProductoCrear,
    db: Session = Depends(get_db),
    _usuario: TokenData = Depends(verificar_token),
):
    try:
        resultado = db.execute(
            text("""
                INSERT INTO productos (codigo_unico, nombre, descripcion, stock_minimo_alerta)
                VALUES (:codigo_unico, :nombre, :descripcion, :stock_minimo_alerta)
                RETURNING id_producto, codigo_unico, nombre, descripcion,
                          stock_actual, stock_minimo_alerta, fecha_creacion
            """),
            producto.model_dump(),
        )
        db.commit()
        return _fila_a_dict(resultado.fetchone())
    except Exception as e:
        db.rollback()
        if "unique" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El código '{producto.codigo_unico}' ya existe",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el producto",
        )


@router.put("/{id_producto}")
def editar_producto(
    id_producto: int,
    datos: ProductoEditar,
    db: Session = Depends(get_db),
    _usuario: TokenData = Depends(verificar_token),
):
    existe = db.execute(
        text("SELECT id_producto FROM productos WHERE id_producto = :id"),
        {"id": id_producto},
    ).fetchone()

    if not existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    campos = datos.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar",
        )

    set_clause = ", ".join(f"{campo} = :{campo}" for campo in campos)
    campos["id_producto"] = id_producto

    resultado = db.execute(
        text(f"""
            UPDATE productos SET {set_clause}
            WHERE id_producto = :id_producto
            RETURNING id_producto, codigo_unico, nombre, descripcion,
                      stock_actual, stock_minimo_alerta, fecha_creacion
        """),
        campos,
    )
    db.commit()
    return _fila_a_dict(resultado.fetchone())


@router.delete("/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    id_producto: int,
    db: Session = Depends(get_db),
    _usuario: TokenData = Depends(verificar_token),
):
    existe = db.execute(
        text("SELECT id_producto FROM productos WHERE id_producto = :id"),
        {"id": id_producto},
    ).fetchone()

    if not existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    db.execute(
        text("DELETE FROM productos WHERE id_producto = :id"),
        {"id": id_producto},
    )
    db.commit()
