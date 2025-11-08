#!/usr/bin/env python3
"""
Rotas Mobile - Endpoints para integração com React Native
"""

import logging
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from src.models.user import UserLogin
from src.services.moto_service import MotoService
from src.services.auth_service import AuthService
from src.formatters.mobile_formatter import MobileFormatter

logger = logging.getLogger(__name__)

mobile_bp = Blueprint('mobile', __name__, url_prefix='/api/mobile')


def get_moto_service():
    """Helper para obter serviço de motos"""
    from flask import current_app
    return MotoService(current_app.config.get('DATABASE_PATH', 'visionmoto_integration.db'))


def get_auth_service():
    """Helper para obter serviço de autenticação"""
    from flask import current_app
    return AuthService(
        current_app.config.get('DATABASE_PATH', 'visionmoto_integration.db'),
        current_app.config.get('SECRET_KEY')
    )


@mobile_bp.route('/auth/login', methods=['POST'])
def login():
    """Endpoint de login para mobile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Validação com Pydantic
        try:
            login_data = UserLogin(**data)
        except ValidationError as e:
            logger.warning(f"Validation error in login: {e}")
            return jsonify({"error": "Invalid email or password format"}), 400
        
        auth_service = get_auth_service()
        result = auth_service.authenticate(login_data.email, login_data.senha)
        
        if not result:
            return jsonify({"error": "Invalid credentials"}), 401
        
        logger.info(f"Login successful for email: {login_data.email}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return jsonify({"error": "Authentication failed"}), 500


@mobile_bp.route('/motos', methods=['GET'])
def list_motos():
    """Lista motos disponíveis para o app mobile"""
    try:
        moto_service = get_moto_service()
        motos = moto_service.get_all_motos(status_filter=['disponivel', 'em_uso'])
        
        return jsonify(MobileFormatter.format_moto_list(motos)), 200
        
    except Exception as e:
        logger.error(f"Error listing motos: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve motorcycles"}), 500


@mobile_bp.route('/motos/buscar/<placa>', methods=['GET'])
def buscar_moto_por_placa(placa):
    """Busca moto específica por placa com localização detalhada"""
    try:
        moto_service = get_moto_service()
        moto = moto_service.find_by_placa(placa)
        
        if not moto:
            return jsonify({"error": f"Moto com placa {placa} não encontrada"}), 404
        
        return jsonify(MobileFormatter.format_moto_detail(moto)), 200
        
    except Exception as e:
        logger.error(f"Error finding moto by plate: {e}", exc_info=True)
        return jsonify({"error": "Failed to find motorcycle"}), 500


@mobile_bp.route('/motos/<moto_id>/reservar', methods=['POST'])
def reservar_moto(moto_id):
    """Reserva uma moto via app mobile"""
    try:
        data = request.get_json() or {}
        usuario_id = data.get("usuario_id")
        
        if not usuario_id:
            return jsonify({"error": "usuario_id é obrigatório"}), 400
        
        moto_service = get_moto_service()
        moto_service.reservar_moto(moto_id, usuario_id)
        
        return jsonify({
            "message": "Moto reservada com sucesso",
            "moto_id": moto_id
        }), 200
        
    except ValueError as e:
        logger.warning(f"Reservation failed: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error reserving moto: {e}", exc_info=True)
        return jsonify({"error": "Failed to reserve motorcycle"}), 500


@mobile_bp.route('/alertas', methods=['GET'])
def list_alertas():
    """Lista alertas para mobile"""
    try:
        from src.services.alert_service import AlertService
        from flask import current_app
        
        status = request.args.get("status", "OPEN").upper()
        
        # Validação de paginação
        try:
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))
            limit = max(1, min(limit, 100))
            offset = max(0, offset)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid pagination parameters"}), 400
        
        # Valida status
        if status not in ["OPEN", "RESOLVED", "ALL"]:
            return jsonify({"error": "Invalid status"}), 400
        
        alert_service = AlertService(current_app.config.get('DATABASE_PATH'))
        alerts = alert_service.get_alerts(
            status=status if status != "ALL" else None,
            limit=limit,
            offset=offset
        )
        
        # Formata para mobile
        items = []
        for alert in alerts:
            items.append({
                "id": alert["id"],
                "status": "OPEN" if alert["ativo"] else "RESOLVED",
                "title": alert["titulo"],
                "message": alert.get("descricao"),
                "severity": alert.get("severidade", "info").upper(),
                "createdAt": alert.get("criado_em"),
            })
        
        return jsonify({"items": items, "total": len(items)}), 200
        
    except Exception as e:
        logger.error(f"Error listing alerts: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve alerts"}), 500


@mobile_bp.route('/alertas/<alert_id>/resolver', methods=['PATCH'])
def resolver_alerta(alert_id):
    """Resolve um alerta"""
    try:
        from src.services.alert_service import AlertService
        from flask import current_app
        
        data = request.get_json() or {}
        resolved_by = data.get("resolvedBy")
        
        alert_service = AlertService(current_app.config.get('DATABASE_PATH'))
        alert_service.resolve_alert(alert_id, resolved_by)
        
        from datetime import datetime
        return jsonify({
            "id": alert_id,
            "status": "RESOLVED",
            "updatedAt": datetime.now().isoformat()
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error resolving alert: {e}", exc_info=True)
        return jsonify({"error": "Failed to resolve alert"}), 500
