#!/usr/bin/env python3
"""
Modelo de dados para User
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserType(str, Enum):
    """Tipos de usuário"""
    USUARIO = "usuario"
    ADMIN = "admin"
    OPERADOR = "operador"


class User(BaseModel):
    """Modelo de Usuário com validação"""
    id: str
    nome: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    tipo: UserType = UserType.USUARIO
    ativo: bool = True
    criado_em: Optional[str] = None
    ultimo_acesso: Optional[str] = None

    class Config:
        use_enum_values = True


class UserLogin(BaseModel):
    """Modelo para login"""
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=255)


class UserCreate(BaseModel):
    """Modelo para criação de usuário"""
    nome: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=8, max_length=255)
    tipo: UserType = UserType.USUARIO
