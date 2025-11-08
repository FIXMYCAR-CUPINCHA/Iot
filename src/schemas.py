#!/usr/bin/env python3
"""
Schemas de validação para VisionMoto usando Pydantic
Garante type safety e validação de dados
"""

from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator, field_validator
from enum import Enum
import re


# ==================== ENUMS ====================

class MotoStatus(str, Enum):
    """Status possíveis de uma moto"""
    DISPONIVEL = "disponivel"
    EM_USO = "em_uso"
    MANUTENCAO = "manutencao"
    RESERVADA = "reservada"


class AlertSeverity(str, Enum):
    """Severidade de alertas"""
    INFO = "info"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    """Status de alertas"""
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class DeviceType(str, Enum):
    """Tipos de dispositivos IoT"""
    SENSOR_MOVIMENTO = "sensor_movimento"
    CAMERA = "camera"
    ATUADOR_TRAVA = "atuador_trava"
    ATUADOR_ALARME = "atuador_alarme"


class DeviceStatus(str, Enum):
    """Status de dispositivos"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


# ==================== AUTH SCHEMAS ====================

class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., min_length=6, description="Senha (mínimo 6 caracteres)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "usuario@mottu.com",
                "senha": "senha123"
            }
        }
    }


class LoginResponse(BaseModel):
    """Schema para resposta de login"""
    token: str = Field(..., description="JWT token")
    user: Dict[str, Any] = Field(..., description="Dados do usuário")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")


# ==================== MOTO SCHEMAS ====================

class MotoLocation(BaseModel):
    """Schema para localização detalhada de moto"""
    endereco: str = Field(..., description="Endereço completo")
    setor: str = Field(..., description="Setor do pátio")
    andar: int = Field(..., ge=1, description="Andar (mínimo 1)")
    vaga: str = Field(..., description="Código da vaga")
    descricao: str = Field(..., description="Descrição da localização")
    coordenadas: Dict[str, float] = Field(..., description="Coordenadas X/Y")
    zona: str = Field(..., description="Zona do pátio")


class MotoBase(BaseModel):
    """Schema base de moto"""
    modelo: str = Field(..., min_length=1, max_length=100)
    placa: str = Field(
        ..., 
        pattern=r'^[A-Z]{3}-\d{4}$',
        description="Placa no formato ABC-1234"
    )
    status: MotoStatus = Field(default=MotoStatus.DISPONIVEL)
    bateria: int = Field(default=100, ge=0, le=100, description="Nível de bateria (0-100)")


class MotoCreate(MotoBase):
    """Schema para criação de moto"""
    localizacao_x: float = Field(default=0.0)
    localizacao_y: float = Field(default=0.0)
    zona: str = Field(default="A1")


class MotoResponse(MotoBase):
    """Schema para resposta de moto"""
    id: str
    localizacao_x: float
    localizacao_y: float
    zona: str
    endereco: Optional[str] = None
    setor: Optional[str] = None
    andar: Optional[int] = None
    vaga: Optional[str] = None
    descricao_localizacao: Optional[str] = None
    ultima_atualizacao: Optional[str] = None
    em_uso_por: Optional[str] = None
    
    class Config:
        orm_mode = True


class MotoReservaRequest(BaseModel):
    """Schema para reserva de moto"""
    usuario_id: str = Field(..., min_length=1)
    
    @validator('usuario_id')
    def validate_usuario_id(cls, v):
        if not v or v.strip() == "":
            raise ValueError("usuario_id não pode ser vazio")
        return v


# ==================== ALERT SCHEMAS ====================

class AlertCreate(BaseModel):
    """Schema para criação de alerta"""
    tipo: str = Field(..., min_length=1)
    severidade: AlertSeverity = Field(default=AlertSeverity.INFO)
    titulo: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=1000)
    motoId: Optional[str] = None
    zona: Optional[str] = None


class AlertResponse(BaseModel):
    """Schema para resposta de alerta"""
    id: str
    status: AlertStatus
    title: str
    message: Optional[str]
    severity: AlertSeverity
    deviceId: Optional[str]
    createdAt: str
    location: Optional[Dict[str, Optional[float]]]


# ==================== IOT SCHEMAS ====================

class IoTEventRequest(BaseModel):
    """Schema para evento IoT"""
    id: Optional[str] = Field(None, description="ID do evento (idempotency key)")
    type: Optional[str] = Field(None, description="Tipo de evento")
    deviceId: str = Field(..., description="ID do dispositivo")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('deviceId')
    def validate_device_id(cls, v):
        if not v or v.strip() == "":
            raise ValueError("deviceId não pode ser vazio")
        return v


class IoTEventResponse(BaseModel):
    """Schema para resposta de evento IoT"""
    alertId: str
    status: AlertStatus
    idempotent: bool = False


class DeviceDataRequest(BaseModel):
    """Schema para dados de dispositivo"""
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    motion_detected: Optional[bool] = None
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    signal_strength: Optional[int] = Field(None, ge=-100, le=0)
    custom_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DeviceResponse(BaseModel):
    """Schema para resposta de dispositivo"""
    id: str
    nome: str
    tipo: DeviceType
    status: DeviceStatus
    localizacao: Optional[str]
    ultima_comunicacao: Optional[str]
    dados_sensor: Optional[str]


# ==================== REPORT SCHEMAS ====================

class UsageReportRequest(BaseModel):
    """Schema para requisição de relatório de uso"""
    StartDate: Optional[str] = None
    EndDate: Optional[str] = None
    
    @validator('StartDate', 'EndDate')
    def validate_date_format(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Data deve estar no formato ISO 8601")
        return v


class UsageReportResponse(BaseModel):
    """Schema para resposta de relatório"""
    IsSuccess: bool
    ReportData: List[Dict[str, Any]]
    GeneratedAt: str
    Period: Dict[str, Optional[str]]


# ==================== PAGINATION ====================

class PaginationParams(BaseModel):
    """Schema para parâmetros de paginação"""
    limit: int = Field(default=50, ge=1, le=100, description="Itens por página")
    offset: int = Field(default=0, ge=0, description="Offset para paginação")


# ==================== RESPONSE WRAPPERS ====================

class SuccessResponse(BaseModel):
    """Schema genérico para resposta de sucesso"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ErrorResponse(BaseModel):
    """Schema genérico para resposta de erro"""
    success: bool = False
    error: str
    details: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ==================== VALIDATORS ====================

def validate_placa(placa: str) -> str:
    """
    Valida formato de placa brasileira
    
    Args:
        placa: Placa a validar
    
    Returns:
        Placa normalizada (uppercase)
    
    Raises:
        ValueError: Se formato inválido
    """
    import re
    
    placa = placa.strip().upper()
    
    # Formato antigo: ABC-1234
    pattern_old = r'^[A-Z]{3}-\d{4}$'
    # Formato Mercosul: ABC1D23
    pattern_mercosul = r'^[A-Z]{3}\d[A-Z]\d{2}$'
    
    if not (re.match(pattern_old, placa) or re.match(pattern_mercosul, placa)):
        raise ValueError(
            "Placa inválida. Use formato ABC-1234 ou ABC1D23 (Mercosul)"
        )
    
    return placa
