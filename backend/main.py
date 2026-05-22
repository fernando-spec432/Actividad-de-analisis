from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field

from database import get_db
from routers import auth, productos, entradas, salidas


app = FastAPI(
    title="API Control de Inventario",
    description="Backend con FastAPI conectado a PostgreSQL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(entradas.router)
app.include_router(salidas.router)


@app.get("/")
def inicio():
    return {"mensaje": "API funcionando correctamente"}


@app.get("/roles")
def obtener_roles(db: Session = Depends(get_db)):
    resultado = db.execute(text("SELECT id_col, nombre_rol FROM roles ORDER BY id_col"))
    return [{"id_col": fila.id_col, "nombre_rol": fila.nombre_rol} for fila in resultado]


@app.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    resultado = db.execute(text("""
        SELECT u.id_usuario, u.username, u.id_rol, r.nombre_rol, u.activo
        FROM usuarios u
        INNER JOIN roles r ON u.id_rol = r.id_col
        ORDER BY u.id_usuario
    """))
    return [
        {
            "id_usuario": fila.id_usuario,
            "username": fila.username,
            "id_rol": fila.id_rol,
            "nombre_rol": fila.nombre_rol,
            "activo": fila.activo,
        }
        for fila in resultado
    ]


@app.get("/alertas-stock")
def obtener_alertas_stock(db: Session = Depends(get_db)):
    resultado = db.execute(text("""
        SELECT id_producto, codigo_unico, nombre, stock_actual, stock_minimo_alerta
        FROM v_alertas_stock
        ORDER BY id_producto
    """))
    return [
        {
            "id_producto": fila.id_producto,
            "codigo_unico": fila.codigo_unico,
            "nombre": fila.nombre,
            "stock_actual": fila.stock_actual,
            "stock_minimo_alerta": fila.stock_minimo_alerta,
        }
        for fila in resultado
    ]


#==============================================================================
# Endpoint para registrar entradas
#==============================================================================
class RegistroEntrada(BaseModel):
    id_producto: int
    cantidad: int = Field(..., gt=0, description="La cantidad debe ser mayor a 0")
    id_usuario: int


@app.post("/registrar-entrada")
def regitrar_entrada(entrada: RegistroEntrada, db: Session = Depends(get_db)):

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