#!/usr/bin/env python3
"""
Rotas Database - Endpoints para operações de banco de dados
"""

import logging
import sqlite3
import shutil
from datetime import datetime
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

database_bp = Blueprint('database', __name__, url_prefix='/api/database')


def get_db_path():
    """Helper para obter caminho do banco"""
    from flask import current_app
    return current_app.config.get('DATABASE_PATH', 'visionmoto_integration.db')


def validate_table_name(table_name: str) -> bool:
    """Valida nome de tabela para prevenir SQL injection"""
    ALLOWED_TABLES = [
        "motos_patio", "usuarios", "alertas", "dispositivos_iot",
        "historico_uso", "detections", "iot_eventos", "push_devices"
    ]
    return table_name in ALLOWED_TABLES and table_name.replace("_", "").isalnum()


@database_bp.route('/backup', methods=['POST'])
def create_backup():
    """Cria backup do banco de dados"""
    try:
        db_path = get_db_path()
        backup_path = f"backup_visionmoto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        shutil.copy2(db_path, backup_path)
        
        logger.info(f"Database backup created: {backup_path}")
        return jsonify({
            "success": True,
            "backup_file": backup_path,
            "created_at": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to create backup"}), 500


@database_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Retorna analytics do banco de dados"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        stats = {}
        
        # Contagem de tabelas com validação
        ALLOWED_TABLES = [
            "motos_patio", "usuarios", "alertas", "dispositivos_iot",
            "historico_uso", "detections"
        ]
        
        for table in ALLOWED_TABLES:
            if not validate_table_name(table):
                logger.error(f"Invalid table name attempted: {table}")
                continue
            
            # Usa parametrização mesmo com whitelist
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = cursor.fetchone()
            stats[f"{table}_count"] = result["count"] if result else 0
        
        # Estatísticas de uso
        cursor.execute("""
            SELECT 
                COUNT(*) as total_usos,
                AVG(tempo_uso) as tempo_medio,
                SUM(distancia_percorrida) as distancia_total
            FROM historico_uso
            WHERE inicio_uso >= date('now', '-30 days')
        """)
        
        uso_stats = cursor.fetchone()
        if uso_stats:
            stats.update({
                "usos_ultimo_mes": uso_stats["total_usos"] or 0,
                "tempo_medio_uso": round(uso_stats["tempo_medio"] or 0, 2),
                "distancia_total_mes": round(uso_stats["distancia_total"] or 0, 2)
            })
        
        conn.close()
        
        return jsonify({
            "success": True,
            "analytics": stats,
            "generated_at": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to retrieve analytics"}), 500
