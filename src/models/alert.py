#!/usr/bin/env python3
"""
Modelo de dados para Alert
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Severidade de alertas"""
    INFO = "info"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Alert(BaseModel):
    """Modelo de Alerta com validação"""
    id: str
    tipo: str = Field(..., min_length=1, max_length=50)
    severidade: AlertSeverity = AlertSeverity.INFO
    titulo: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=1000)
    moto_id: Optional[str] = None
    zona: Optional[str] = Field(None, max_length=10)
    ativo: bool = True
    criado_em: str
    resolvido_em: Optional[str] = None
    resolvido_por: Optional[str] = None

    class Config:
        use_enum_values = True
