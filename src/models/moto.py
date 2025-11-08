#!/usr/bin/env python3
"""
Modelo de dados para Moto
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class MotoStatus(str, Enum):
    """Status possíveis de uma moto"""
    DISPONIVEL = "disponivel"
    EM_USO = "em_uso"
    MANUTENCAO = "manutencao"


class Moto(BaseModel):
    """Modelo de Moto com validação"""
    id: str
    modelo: str = Field(..., min_length=1, max_length=100)
    placa: str = Field(..., min_length=7, max_length=10)
    status: MotoStatus = MotoStatus.DISPONIVEL
    bateria: int = Field(default=100, ge=0, le=100)
    localizacao_x: float = Field(default=0.0)
    localizacao_y: float = Field(default=0.0)
    zona: str = Field(default="A1", max_length=10)
    endereco: str = Field(default="", max_length=255)
    setor: str = Field(default="", max_length=50)
    andar: int = Field(default=1, ge=1, le=10)
    vaga: str = Field(default="", max_length=20)
    descricao_localizacao: str = Field(default="", max_length=500)
    ultima_atualizacao: Optional[str] = None
    em_uso_por: Optional[str] = None
    manutencao_agendada: Optional[str] = None

    @field_validator('placa')
    @classmethod
    def validate_placa(cls, v: str) -> str:
        """Valida formato de placa brasileira"""
        v = v.upper().strip()
        # Remove hífens e espaços
        v = v.replace("-", "").replace(" ", "")
        
        if len(v) < 7 or len(v) > 8:
            raise ValueError("Placa deve ter 7 ou 8 caracteres")
        
        return v

    class Config:
        use_enum_values = True
