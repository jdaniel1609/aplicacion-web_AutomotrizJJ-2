from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Esquema de respuesta de token"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Datos contenidos en el token"""
    username: Optional[str] = None