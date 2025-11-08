#!/usr/bin/env python3
"""
Serviço de Alertas - Gerenciamento centralizado de alertas
"""

import sqlite3
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AlertService:
    """Serviço para operações de alertas"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """Retorna conexão com banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_alert(
        self,
        tipo: str,
        titulo: str,
        severidade: str = "info",
        descricao: Optional[str] = None,
        moto_id: Optional[str] = None,
        zona: Optional[str] = None
    ) -> str:
        """
        Cria um novo alerta
        
        Args:
            tipo: Tipo do alerta
            titulo: Título do alerta
            severidade: Severidade (info, LOW, MEDIUM, HIGH, CRITICAL)
            descricao: Descrição detalhada
            moto_id: ID da moto relacionada
            zona: Zona relacionada
        
        Returns:
            ID do alerta criado
        """
        try:
            alert_id = str(uuid.uuid4())
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alertas (
                    id, tipo, severidade, titulo, descricao, 
                    moto_id, zona, ativo, criado_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                alert_id,
                tipo,
                severidade,
                titulo,
                descricao,
                moto_id,
                zona,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(
                "Alerta criado",
                alert_id=alert_id,
                tipo=tipo,
                severidade=severidade
            )
            
            return alert_id
            
        except sqlite3.Error as e:
            logger.error("Erro ao criar alerta", error=e, tipo=tipo)
            raise
    
    def get_alerts(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Lista alertas com filtros
        
        Args:
            status: Filtro de status (OPEN, RESOLVED)
            limit: Limite de resultados
            offset: Offset para paginação
        
        Returns:
            Lista de alertas
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if status == "OPEN":
                cursor.execute("""
                    SELECT * FROM alertas 
                    WHERE ativo = 1 
                    ORDER BY criado_em DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            elif status == "RESOLVED":
                cursor.execute("""
                    SELECT * FROM alertas 
                    WHERE ativo = 0 
                    ORDER BY resolvido_em DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM alertas 
                    ORDER BY criado_em DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            
            alerts = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.debug(
                "Alertas listados",
                total=len(alerts),
                status=status,
                limit=limit,
                offset=offset
            )
            
            return alerts
            
        except sqlite3.Error as e:
            logger.error("Erro ao listar alertas", error=e, status=status)
            raise
    
    def resolve_alert(
        self,
        alert_id: str,
        resolved_by: Optional[str] = None
    ) -> bool:
        """
        Resolve um alerta
        
        Args:
            alert_id: ID do alerta
            resolved_by: ID de quem resolveu
        
        Returns:
            True se resolvido com sucesso
        
        Raises:
            ValueError: Se alerta não encontrado ou já resolvido
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE alertas 
                SET ativo = 0, 
                    resolvido_em = ?, 
                    resolvido_por = ?
                WHERE id = ? AND ativo = 1
            """, (datetime.now().isoformat(), resolved_by, alert_id))
            
            if cursor.rowcount == 0:
                conn.close()
                logger.warning(
                    "Tentativa de resolver alerta inexistente ou já resolvido",
                    alert_id=alert_id
                )
                raise ValueError("Alerta não encontrado ou já resolvido")
            
            conn.commit()
            conn.close()
            
            logger.info(
                "Alerta resolvido",
                alert_id=alert_id,
                resolved_by=resolved_by
            )
            
            return True
            
        except sqlite3.Error as e:
            logger.error("Erro ao resolver alerta", error=e, alert_id=alert_id)
            raise
