#!/usr/bin/env python3
"""
Serviço de IoT - Gerenciamento de dispositivos e eventos
"""

import sqlite3
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class IoTService:
    """Serviço para operações de IoT"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Retorna conexão com banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def process_event(
        self,
        idempotency_key: str,
        event_type: Optional[str],
        device_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa evento IoT com idempotência
        
        Args:
            idempotency_key: Chave de idempotência
            event_type: Tipo do evento
            device_id: ID do dispositivo
            metadata: Metadados adicionais
        
        Returns:
            Dicionário com alertId e status
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verifica idempotência
            cursor.execute("""
                SELECT alert_id FROM iot_eventos 
                WHERE idempotency_key = ?
            """, (idempotency_key,))
            
            row = cursor.fetchone()
            
            if row:
                # Evento já processado
                alert_id = row["alert_id"]
                conn.close()
                
                logger.debug(
                    "Evento IoT já processado (idempotente)",
                    idempotency_key=idempotency_key,
                    alert_id=alert_id
                )
                
                return {
                    "alertId": alert_id,
                    "status": "OPEN",
                    "idempotent": True
                }
            
            # Cria novo alerta
            alert_id = f"ALR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            
            titulo = "Moto fora da vaga" if event_type else "Alerta IoT"
            descricao = f"Dispositivo {device_id} detectou irregularidade"
            severidade = "HIGH" if event_type else "info"
            zona = (metadata or {}).get("slot")
            
            cursor.execute("""
                INSERT INTO alertas (
                    id, tipo, severidade, titulo, descricao, 
                    moto_id, zona, ativo, criado_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                alert_id,
                event_type or "iot",
                severidade,
                titulo,
                descricao,
                None,
                zona,
                datetime.now().isoformat()
            ))
            
            # Registra idempotência
            cursor.execute("""
                INSERT INTO iot_eventos (idempotency_key, alert_id, created_at)
                VALUES (?, ?, ?)
            """, (idempotency_key, alert_id, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.info(
                "Evento IoT processado",
                idempotency_key=idempotency_key,
                alert_id=alert_id,
                device_id=device_id,
                event_type=event_type
            )
            
            return {
                "alertId": alert_id,
                "status": "OPEN",
                "idempotent": False
            }
            
        except sqlite3.Error as e:
            logger.error(
                "Erro ao processar evento IoT",
                error=e,
                idempotency_key=idempotency_key,
                device_id=device_id
            )
            raise
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """
        Lista todos os dispositivos IoT
        
        Returns:
            Lista de dispositivos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM dispositivos_iot 
                ORDER BY nome
            """)
            
            devices = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.debug("Dispositivos IoT listados", total=len(devices))
            
            return devices
            
        except sqlite3.Error as e:
            logger.error("Erro ao listar dispositivos", error=e)
            raise
    
    def update_device_data(
        self,
        device_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Atualiza dados de um dispositivo
        
        Args:
            device_id: ID do dispositivo
            data: Dados do sensor
        
        Returns:
            True se atualizado com sucesso
        """
        try:
            import json
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE dispositivos_iot 
                SET dados_sensor = ?, 
                    ultima_comunicacao = ?, 
                    status = 'online'
                WHERE id = ?
            """, (
                json.dumps(data),
                datetime.now().isoformat(),
                device_id
            ))
            
            success = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            if success:
                logger.info(
                    "Dados do dispositivo atualizados",
                    device_id=device_id
                )
            else:
                logger.warning(
                    "Dispositivo não encontrado",
                    device_id=device_id
                )
            
            return success
            
        except sqlite3.Error as e:
            logger.error(
                "Erro ao atualizar dados do dispositivo",
                error=e,
                device_id=device_id
            )
            raise
