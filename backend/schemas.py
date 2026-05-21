from pydantic import BaseModel
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
