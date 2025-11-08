#!/usr/bin/env python3
"""
Rotas Java - Endpoints para integração com Spring Boot
"""

import logging
from flask import Blueprint, request, jsonify

from src.services.moto_service import MotoService
from src.formatters.java_formatter import JavaFormatter

logger = logging.getLogger(__name__)

java_bp = Blueprint('java', __name__, url_prefix='/api/java')


def get_moto_service():
    """Helper para obter serviço de motos"""
    from flask import current_app
    return MotoService(current_app.config.get('DATABASE_PATH', 'visionmoto_integration.db'))


@java_bp.route('/motos/status', methods=['GET'])
def motos_status():
    """Endpoint para integração com Spring Boot"""
    try:
        moto_service = get_moto_service()
        motos = moto_service.get_all_motos()
        
        return jsonify(JavaFormatter.format_moto_list(motos)), 200
        
    except Exception as e:
        logger.error(f"Error getting motos status: {e}", exc_info=True)
        return jsonify(JavaFormatter.format_error("Failed to retrieve motorcycle data")), 500


@java_bp.route('/motos/buscar/<placa>', methods=['GET'])
def buscar_moto_por_placa(placa):
    """Busca moto específica por placa - Endpoint Java/Spring Boot"""
    try:
        moto_service = get_moto_service()
        moto = moto_service.find_by_placa(placa)
        
        if not moto:
            return jsonify(JavaFormatter.format_error(f"Moto com placa {placa} não encontrada")), 404
        
        return jsonify(JavaFormatter.format_moto_detail(moto)), 200
        
    except Exception as e:
        logger.error(f"Error finding moto: {e}", exc_info=True)
        return jsonify(JavaFormatter.format_error("Failed to find motorcycle")), 500


@java_bp.route('/alertas', methods=['GET', 'POST'])
def alertas():
    """Gerenciamento de alertas para Java"""
    if request.method == 'GET':
        try:
            from src.services.alert_service import AlertService
            from flask import current_app
            
            alert_service = AlertService(current_app.config.get('DATABASE_PATH'))
            alerts = alert_service.get_alerts(status="OPEN")
            
            return jsonify({"success": True, "alertas": alerts}), 200
            
        except Exception as e:
            logger.error(f"Error listing alerts: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            from src.services.alert_service import AlertService
            from flask import current_app
            
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Invalid JSON"}), 400
            
            alert_service = AlertService(current_app.config.get('DATABASE_PATH'))
            alert_id = alert_service.create_alert(
                tipo=data.get("tipo", "info"),
                titulo=data.get("titulo", ""),
                severidade=data.get("severidade", "info"),
                descricao=data.get("descricao"),
                moto_id=data.get("motoId"),
                zona=data.get("zona")
            )
            
            return jsonify({"success": True, "message": "Alerta criado", "alertId": alert_id}), 201
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500
