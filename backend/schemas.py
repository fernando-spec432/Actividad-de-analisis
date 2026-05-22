from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id_usuario: int
    username: str
    id_rol: int


class ProductoCrear(BaseModel):
    codigo_unico: str
    nombre: str
    descripcion: Optional[str] = None
    stock_minimo_alerta: int = 5


class ProductoEditar(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    stock_minimo_alerta: Optional[int] = None


class RegistroEntrada(BaseModel):
    id_producto: int
    cantidad: int
    id_usuario: int


class UsuarioCrear(BaseModel):
    username: str = Field(..., description="Nombre de usuario único", min_length=3, max_length=50)
    password: str = Field(..., description="Contraseña del usuario", min_length=6)
    id_rol: int = Field(..., description="ID del rol asignado al usuario", gt=0)


class UsuarioEditar(BaseModel):
    username: Optional[str] = Field(None, description="Nombre de usuario único", min_length=3, max_length=50)
    password: Optional[str] = Field(None, description="Contraseña del usuario", min_length=6)
    id_rol: Optional[int] = Field(None, description="ID del rol asignado al usuario", gt=0)
    activo: Optional[bool] = Field(None, description="Estado del usuario (activo/inactivo)")
