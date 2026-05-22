import bcrypt
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from schemas import LoginRequest, TokenData, TokenResponse, UsuarioCrear, UsuarioEditar

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

    if not bcrypt.checkpw(datos.password.encode(), fila.password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    token = _crear_token({
        "sub": str(fila.id_usuario),
        "username": fila.username,
        "id_rol": fila.id_rol,
    })

    return {"access_token": token, "token_type": "bearer"}


@router.post(
    "/registrar",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description="""
    Crea un nuevo usuario en el sistema con password hasheado.
    
    **Campos requeridos:**
    - username: Nombre de usuario único
    - password: Contraseña del usuario (se hashea automáticamente)
    - id_rol: ID del rol asignado al usuario (debe existir en la tabla roles)

    **Respuesta:**
    - Retorna el usuario creado (sin el password)
    - Status 201: Usuario creado exitosamente
    - Status 409: El username ya existe
    - Status 404: El rol no existe
    """
)
def registrar_usuario(
    datos: UsuarioCrear,
    db: Session = Depends(get_db),
):
    # 1. Validar que el username no exista
    existe = db.execute(
        text("SELECT id_usuario FROM usuarios WHERE username = :username"),
        {"username": datos.username}
    ).fetchone()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario ya existe"
        )

    # 2. Validar que el rol exista
    rol = db.execute(
        text("SELECT id_col FROM roles WHERE id_col = :id_rol"),
        {"id_rol": datos.id_rol}
    ).fetchone()

    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El rol especificado no existe"
        )

    try:
        # 3. Hashear el password
        password_hash = bcrypt.hashpw(
            datos.password.encode(),
            bcrypt.gensalt()
        ).decode()

        # 4. Insertar el usuario
        resultado = db.execute(
            text("""
                INSERT INTO usuarios (username, password_hash, id_rol, activo)
                VALUES (:username, :password_hash, :id_rol, true)
                RETURNING id_usuario, username, id_rol, activo
            """),
            {
                "username": datos.username,
                "password_hash": password_hash,
                "id_rol": datos.id_rol
            }
        )
        db.commit()

        fila = resultado.fetchone()
        return {
            "id_usuario": fila.id_usuario,
            "username": fila.username,
            "id_rol": fila.id_rol,
            "activo": fila.activo
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el usuario: {str(e)}"
        )


@router.put(
    "/usuarios/{id_usuario}",
    summary="Editar un usuario",
    description="""
    Actualiza los datos de un usuario existente.
    
    **Campos opcionales:**
    - username: Nuevo nombre de usuario (debe ser único)
    - password: Nueva contraseña (se hashea automáticamente)
    - id_rol: Nuevo rol asignado
    - activo: Estado del usuario (true/false)
    
    **Respuesta:**
    - Retorna el usuario actualizado (sin el password)
    - Status 200: Usuario actualizado exitosamente
    - Status 404: El usuario no existe
    - Status 409: El username ya existe en otro usuario
    """
)
def editar_usuario(
    id_usuario: int,
    datos: UsuarioEditar,
    db: Session = Depends(get_db),
    _usuario: TokenData = Depends(verificar_token),
):
    # 1. Validar que el usuario exista
    existe = db.execute(
        text("SELECT id_usuario FROM usuarios WHERE id_usuario = :id_usuario"),
        {"id_usuario": id_usuario}
    ).fetchone()

    if not existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe"
        )

    campos = datos.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar"
        )

    try:
        # 2. Si se cambia el username, validar que no exista en otro usuario
        if "username" in campos:
            username_existe = db.execute(
                text("SELECT id_usuario FROM usuarios WHERE username = :username AND id_usuario != :id_usuario"),
                {"username": campos["username"], "id_usuario": id_usuario}
            ).fetchone()

            if username_existe:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El nombre de usuario ya existe"
                )

        # 3. Si se cambia el password, hashearlo
        if "password" in campos:
            campos["password_hash"] = bcrypt.hashpw(
                campos["password"].encode(),
                bcrypt.gensalt()
            ).decode()
            del campos["password"]

        # 4. Si se cambia el rol, validar que exista
        if "id_rol" in campos:
            rol_existe = db.execute(
                text("SELECT id_col FROM roles WHERE id_col = :id_rol"),
                {"id_rol": campos["id_rol"]}
            ).fetchone()

            if not rol_existe:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="El rol especificado no existe"
                )

        # 5. Construir la consulta de actualización
        set_clause = ", ".join(f"{campo} = :{campo}" for campo in campos)
        campos["id_usuario"] = id_usuario

        resultado = db.execute(
            text(f"""
                UPDATE usuarios SET {set_clause}
                WHERE id_usuario = :id_usuario
                RETURNING id_usuario, username, id_rol, activo
            """),
            campos
        )
        db.commit()

        fila = resultado.fetchone()
        return {
            "id_usuario": fila.id_usuario,
            "username": fila.username,
            "id_rol": fila.id_rol,
            "activo": fila.activo
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el usuario: {str(e)}"
        )


@router.delete(
    "/usuarios/{id_usuario}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un usuario",
    description="""
    Elimina un usuario del sistema.
    
    **Respuesta:**
    - Status 204: Usuario eliminado exitosamente
    - Status 404: El usuario no existe
    """
)
def eliminar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    _usuario: TokenData = Depends(verificar_token),
):
    # 1. Validar que el usuario exista
    existe = db.execute(
        text("SELECT id_usuario FROM usuarios WHERE id_usuario = :id_usuario"),
        {"id_usuario": id_usuario}
    ).fetchone()

    if not existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe"
        )

    try:
        # 2. Eliminar el usuario
        db.execute(
            text("DELETE FROM usuarios WHERE id_usuario = :id_usuario"),
            {"id_usuario": id_usuario}
        )
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el usuario: {str(e)}"
        )
