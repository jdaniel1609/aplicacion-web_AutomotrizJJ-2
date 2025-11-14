from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    """Esquema base de usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Esquema para crear usuario"""
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Esquema para login"""
    username: str
    password: str


class UserResponse(UserBase):
    """Esquema de respuesta de usuario"""
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """Esquema de usuario en base de datos"""
    id: int
    hashed_password: str
    is_active: bool
    
    class Config:
        from_attributes = True