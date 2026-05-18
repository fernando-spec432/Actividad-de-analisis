from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

app = FastAPI(
    title="API Control de Inventario",
    description="Backend con FastAPI conectado a PostgreSQL",
    version="1.0.0"
)

# Permite conexión desde React
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


@app.get("/")
def inicio():
    return {
        "mensaje": "API funcionando correctamente"
    }


@app.get("/roles")
def obtener_roles(db: Session = Depends(get_db)):
    resultado = db.execute(text("SELECT id_col, nombre_rol FROM roles ORDER BY id_col"))
    roles = []

    for fila in resultado:
        roles.append({
            "id_col": fila.id_col,
            "nombre_rol": fila.nombre_rol
        })

    return roles


@app.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    resultado = db.execute(text("""
        SELECT 
            u.id_usuario,
            u.username,
            u.id_rol,
            r.nombre_rol,
            u.activo
        FROM usuarios u
        INNER JOIN roles r ON u.id_rol = r.id_col
        ORDER BY u.id_usuario
    """))

    usuarios = []

    for fila in resultado:
        usuarios.append({
            "id_usuario": fila.id_usuario,
            "username": fila.username,
            "id_rol": fila.id_rol,
            "nombre_rol": fila.nombre_rol,
            "activo": fila.activo
        })

    return usuarios


@app.get("/productos")
def obtener_productos(db: Session = Depends(get_db)):
    resultado = db.execute(text("""
        SELECT 
            id_producto,
            codigo_unico,
            nombre,
            descripcion,
            stock_actual,
            stock_minimo_alerta,
            fecha_creacion
        FROM productos
        ORDER BY id_producto
    """))

    productos = []

    for fila in resultado:
        productos.append({
            "id_producto": fila.id_producto,
            "codigo_unico": fila.codigo_unico,
            "nombre": fila.nombre,
            "descripcion": fila.descripcion,
            "stock_actual": fila.stock_actual,
            "stock_minimo_alerta": fila.stock_minimo_alerta,
            "fecha_creacion": str(fila.fecha_creacion)
        })

    return productos


@app.get("/alertas-stock")
def obtener_alertas_stock(db: Session = Depends(get_db)):
    resultado = db.execute(text("""
        SELECT 
            id_producto,
            codigo_unico,
            nombre,
            stock_actual,
            stock_minimo_alerta
        FROM v_alertas_stock
        ORDER BY id_producto
    """))

    alertas = []

    for fila in resultado:
        alertas.append({
            "id_producto": fila.id_producto,
            "codigo_unico": fila.codigo_unico,
            "nombre": fila.nombre,
            "stock_actual": fila.stock_actual,
            "stock_minimo_alerta": fila.stock_minimo_alerta
        })

    return alertas