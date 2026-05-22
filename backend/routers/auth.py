import bcrypt
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from schemas import LoginRequest, TokenData, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])

security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "clave-secreta-cambiar-en-produccion")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60


def _crear_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(
            id_usuario=int(payload["sub"]),
            username=payload["username"],
            id_rol=payload["id_rol"],
        )
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    fila = db.execute(
        text(
            "SELECT id_usuario, username, password_hash, id_rol, activo "
            "FROM usuarios WHERE username = :username"
        ),
        {"username": datos.username},
    ).fetchone()

    if not fila:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not fila.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
        )
    print(f"FRONTEND MANDA -> Usuario: {datos.username}, Clave: {datos.password}")
    print(f"BASE DATOS TIENE -> Usuario: {fila.username}, Clave: {fila.password_hash}")
    # 1. Validación de contraseña en texto plano
    if datos.password != fila.password_hash:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    # 2. Creación del token con los nombres exactos de tu tabla (id_usuario, username, id_rol)
    token = _crear_token({
        "sub": str(fila.id_usuario),
        "username": fila.username,
        "id_rol": fila.id_rol
    })

    # 3. Retorno del token al frontend
    return {"access_token": token, "token_type": "bearer"}
