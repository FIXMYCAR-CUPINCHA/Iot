#!/usr/bin/env python3
"""
Rotas .NET - Endpoints para integração com C#/.NET
"""

import logging
from flask import Blueprint, request, jsonify

from src.services.moto_service import MotoService
from src.formatters.dotnet_formatter import DotNetFormatter

logger = logging.getLogger(__name__)

dotnet_bp = Blueprint('dotnet', __name__, url_prefix='/api/dotnet')


def get_moto_service():
    """Helper para obter serviço de motos"""
    from flask import current_app
    return MotoService(current_app.config.get('DATABASE_PATH', 'visionmoto_integration.db'))


@dotnet_bp.route('/Dashboard/GetMotorcycleData', methods=['GET'])
def get_motorcycle_data():
    """Endpoint para integração com .NET (formato C#)"""
    try:
        moto_service = get_moto_service()
        motos = moto_service.get_all_motos()
        
        return jsonify(DotNetFormatter.format_moto_list(motos)), 200
        
    except Exception as e:
        logger.error(f"Error getting motorcycle data: {e}", exc_info=True)
        return jsonify(DotNetFormatter.format_error("Failed to retrieve motorcycle data")), 500


@dotnet_bp.route('/Motorcycles/FindByPlate/<placa>', methods=['GET'])
def find_by_plate(placa):
    """Busca moto específica por placa - Endpoint .NET"""
    try:
        moto_service = get_moto_service()
        moto = moto_service.find_by_placa(placa)
        
        if not moto:
            return jsonify(DotNetFormatter.format_error(f"Motorcycle with plate {placa} not found")), 404
        
        return jsonify(DotNetFormatter.format_moto_detail(moto)), 200
        
    except Exception as e:
        logger.error(f"Error finding motorcycle: {e}", exc_info=True)
        return jsonify(DotNetFormatter.format_error("Failed to find motorcycle")), 500


@dotnet_bp.route('/Reports/GenerateUsageReport', methods=['POST'])
def generate_usage_report():
    """Gera relatório de uso para .NET"""
    try:
        import sqlite3
        from datetime import datetime, timedelta
        from flask import current_app
        
        data = request.get_json() or {}
        start_date = data.get("StartDate", (datetime.now() - timedelta(days=7)).isoformat())
        end_date = data.get("EndDate", datetime.now().isoformat())
        
        db_path = current_app.config.get('DATABASE_PATH')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                h.moto_id as MotorcycleId,
                m.modelo as Model,
                COUNT(*) as UsageCount,
                AVG(h.tempo_uso) as AverageUsageTime,
                SUM(h.distancia_percorrida) as TotalDistance
            FROM historico_uso h
            JOIN motos_patio m ON h.moto_id = m.id
            WHERE h.inicio_uso BETWEEN ? AND ?
            GROUP BY h.moto_id, m.modelo
        """, (start_date, end_date))
        
        report_data = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            "IsSuccess": True,
            "ReportData": report_data,
            "GeneratedAt": datetime.now().isoformat(),
            "Period": {"StartDate": start_date, "EndDate": end_date}
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return jsonify(DotNetFormatter.format_error("Failed to generate report")), 500
