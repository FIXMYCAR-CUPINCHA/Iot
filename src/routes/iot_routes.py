#!/usr/bin/env python3
"""
Rotas IoT - Endpoints para dispositivos IoT
"""

import logging
import sqlite3
import uuid
import json
from datetime import datetime
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

iot_bp = Blueprint('iot', __name__, url_prefix='/api/iot')


def get_db_connection():
    """Helper para obter conexão com banco"""
    from flask import current_app
    db_path = current_app.config.get('DATABASE_PATH', 'visionmoto_integration.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@iot_bp.route('/eventos', methods=['POST'])
def criar_evento():
    """Recebe eventos IoT e cria/atualiza alerta com idempotência"""
    try:
        data = request.get_json() or {}
        idem = request.headers.get("Idempotency-Key") or data.get("id")
        
        if not idem:
            return jsonify({"error": "Idempotency-Key obrigatório"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Idempotência: já existe?
        cursor.execute(
            "SELECT alert_id FROM iot_eventos WHERE idempotency_key = ?",
            (idem,)
        )
        row = cursor.fetchone()
        
        if row:
            alert_id = row[0]
            conn.close()
            logger.info(f"Idempotent request for event: {idem}")
            return jsonify({
                "alertId": alert_id,
                "status": "OPEN",
                "idempotent": True
            }), 200
        
        # Cria alerta
        alert_id = f"ALR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        titulo = "Moto fora da vaga" if data.get("type") else "Alerta IoT"
        descricao = f"Dispositivo {data.get('deviceId','desconhecido')} detectou irregularidade"
        
        cursor.execute("""
            INSERT INTO alertas (id, tipo, severidade, titulo, descricao, moto_id, zona, ativo, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            alert_id,
            data.get("type", "iot"),
            "HIGH" if data.get("type") else "info",
            titulo,
            descricao,
            None,
            (data.get("metadata") or {}).get("slot"),
            datetime.now().isoformat()
        ))
        
        # Registra idempotência
        cursor.execute(
            "INSERT INTO iot_eventos (idempotency_key, alert_id, created_at) VALUES (?, ?, ?)",
            (idem, alert_id, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"IoT event created: {alert_id}")
        return jsonify({"alertId": alert_id, "status": "OPEN"}), 201
        
    except Exception as e:
        logger.error(f"Error creating IoT event: {e}", exc_info=True)
        return jsonify({"error": "Failed to create event"}), 500


@iot_bp.route('/devices', methods=['GET'])
def list_devices():
    """Lista dispositivos IoT"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM dispositivos_iot ORDER BY nome")
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            "devices": devices,
            "total": len(devices),
            "online": len([d for d in devices if d["status"] == "online"])
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing devices: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve devices"}), 500


@iot_bp.route('/devices/<device_id>/data', methods=['POST'])
def receive_device_data(device_id):
    """Recebe dados de dispositivo IoT"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Atualiza dados do dispositivo
        cursor.execute("""
            UPDATE dispositivos_iot 
            SET dados_sensor = ?, ultima_comunicacao = ?, status = 'online'
            WHERE id = ?
        """, (json.dumps(data), datetime.now().isoformat(), device_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Device not found"}), 404
        
        conn.commit()
        conn.close()
        
        logger.info(f"Device data received: {device_id}")
        return jsonify({"success": True, "message": "Dados recebidos"}), 200
        
    except Exception as e:
        logger.error(f"Error receiving device data: {e}", exc_info=True)
        return jsonify({"error": "Failed to process device data"}), 500
