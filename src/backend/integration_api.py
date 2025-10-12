#!/usr/bin/env python3
"""
Integration API - API REST completa para integração com outras disciplinas
Desenvolvido para o 4º Sprint - Challenge 2025
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt


class VisionMotoIntegrationAPI:
    """API REST completa para integração multi-disciplinar"""

    def __init__(self, db_path="visionmoto_integration.db"):
        self.app = Flask(__name__, static_folder="static")
        self.app.config["SECRET_KEY"] = "visionmoto-challenge-2025"
        self.db_path = db_path

        # Habilita CORS para integração com apps mobile e web
        CORS(self.app)

        self._init_database()
        self._setup_routes()

    def _init_database(self):
        """Inicializa banco de dados com tabelas para integração"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabela de detecções (existente)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                frame INTEGER,
                class_name TEXT,
                confidence REAL,
                bbox TEXT,
                fps REAL,
                location_x REAL DEFAULT 0,
                location_y REAL DEFAULT 0,
                zone_id TEXT DEFAULT 'A1'
            )
        """
        )

        # Tabela de motos no pátio
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS motos_patio (
                id TEXT PRIMARY KEY,
                modelo TEXT,
                placa TEXT,
                status TEXT DEFAULT 'disponivel',
                bateria INTEGER DEFAULT 100,
                localizacao_x REAL DEFAULT 0,
                localizacao_y REAL DEFAULT 0,
                zona TEXT DEFAULT 'A1',
                ultima_atualizacao TEXT,
                em_uso_por TEXT,
                manutencao_agendada TEXT
            )
        """
        )

        # Tabela de usuários (para mobile app)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                tipo TEXT DEFAULT 'usuario',
                criado_em TEXT,
                ultimo_acesso TEXT,
                ativo BOOLEAN DEFAULT 1
            )
        """
        )

        # Tabela de alertas
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alertas (
                id TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                severidade TEXT DEFAULT 'info',
                titulo TEXT NOT NULL,
                descricao TEXT,
                moto_id TEXT,
                zona TEXT,
                ativo BOOLEAN DEFAULT 1,
                criado_em TEXT,
                resolvido_em TEXT,
                resolvido_por TEXT
            )
        """
        )

        # Tabela de dispositivos IoT
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dispositivos_iot (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                status TEXT DEFAULT 'online',
                localizacao TEXT,
                ultima_comunicacao TEXT,
                dados_sensor TEXT,
                configuracao TEXT
            )
        """
        )

        # Tabela de histórico de uso
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS historico_uso (
                id TEXT PRIMARY KEY,
                moto_id TEXT NOT NULL,
                usuario_id TEXT,
                inicio_uso TEXT,
                fim_uso TEXT,
                localizacao_inicial TEXT,
                localizacao_final TEXT,
                distancia_percorrida REAL DEFAULT 0,
                tempo_uso INTEGER DEFAULT 0
            )
        """
        )

        conn.commit()
        conn.close()

        # Popula dados iniciais se necessário
        self._populate_initial_data()

    def _populate_initial_data(self):
        """Popula dados iniciais para demonstração"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Verifica se já existem motos
        try:
            cursor.execute("SELECT COUNT(*) FROM motos_patio")
            if cursor.fetchone()[0] == 0:
                # Adiciona motos de exemplo
                motos_exemplo = [
                    (
                        "MOTO001",
                        "Honda CG 160",
                        "ABC-1234",
                        "disponivel",
                        95,
                        10.5,
                        20.3,
                        "A1",
                    ),
                    (
                        "MOTO002",
                        "Yamaha Factor",
                        "DEF-5678",
                        "em_uso",
                        78,
                        15.2,
                        25.1,
                        "A2",
                    ),
                    (
                        "MOTO003",
                        "Honda Biz",
                        "GHI-9012",
                        "disponivel",
                        100,
                        8.7,
                        18.9,
                        "A1",
                    ),
                    (
                        "MOTO004",
                        "Yamaha Neo",
                        "JKL-3456",
                        "manutencao",
                        45,
                        12.1,
                        22.4,
                        "B1",
                    ),
                    (
                        "MOTO005",
                        "Honda PCX",
                        "MNO-7890",
                        "disponivel",
                        88,
                        20.3,
                        30.2,
                        "B2",
                    ),
                    (
                        "MOTO006",
                        "Suzuki Burgman",
                        "PQR-1357",
                        "em_uso",
                        92,
                        25.1,
                        35.8,
                        "C1",
                    ),
                ]

            for moto in motos_exemplo:
                cursor.execute(
                    """
                    INSERT INTO motos_patio 
                    (id, modelo, placa, status, bateria, localizacao_x, localizacao_y, zona, ultima_atualizacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (*moto, datetime.now().isoformat()),
                )

            # Adiciona dispositivos IoT de exemplo
            cursor.execute("SELECT COUNT(*) FROM dispositivos_iot")
            if cursor.fetchone()[0] == 0:
                dispositivos = [
                    (
                        "SENSOR001",
                        "Sensor de Movimento A1",
                        "sensor_movimento",
                        "online",
                        "Zona A1",
                    ),
                    (
                        "SENSOR002",
                        "Sensor de Movimento A2",
                        "sensor_movimento",
                        "online",
                        "Zona A2",
                    ),
                    (
                        "SENSOR003",
                        "Sensor de Movimento B1",
                        "sensor_movimento",
                        "offline",
                        "Zona B1",
                    ),
                    (
                        "CAMERA001",
                        "Câmera Principal",
                        "camera",
                        "online",
                        "Entrada Principal",
                    ),
                    (
                        "LOCK001",
                        "Trava Inteligente A1",
                        "atuador_trava",
                        "online",
                        "Zona A1",
                    ),
                    (
                        "ALARM001",
                        "Sistema de Alarme",
                        "atuador_alarme",
                        "online",
                        "Central",
                    ),
                ]

                for dispositivo in dispositivos:
                    cursor.execute(
                        """
                        INSERT INTO dispositivos_iot 
                        (id, nome, tipo, status, localizacao, ultima_comunicacao)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (*dispositivo, datetime.now().isoformat()),
                    )
        except sqlite3.Error:
            # Se houver erro (ex: tabelas não existem), ignora
            pass

        conn.commit()
        conn.close()

    def _setup_routes(self):
        """Configura todas as rotas da API"""

        # Rotas básicas
        @self.app.route("/")
        def index():
            return jsonify(
                {
                    "service": "VisionMoto Integration API",
                    "version": "2.0",
                    "status": "running",
                    "endpoints": {
                        "mobile": "/api/mobile/*",
                        "java": "/api/java/*",
                        "dotnet": "/api/dotnet/*",
                        "database": "/api/database/*",
                        "iot": "/api/iot/*",
                        "dashboard": "/dashboard",
                    },
                }
            )

        @self.app.route("/health")
        def health():
            return jsonify(
                {"status": "healthy", "timestamp": datetime.now().isoformat()}
            )

        # Mobile App endpoints
        @self.app.route("/api/mobile/auth/login", methods=["POST"])
        def mobile_login():
            try:
                data = request.get_json()
                email = data.get("email")
                senha = data.get("senha")

                # Validação básica
                if not email or not senha:
                    return jsonify({"error": "Email e senha obrigatórios"}), 400

                # Busca usuário (implementação simplificada)
                user_data = {
                    "id": str(uuid.uuid4()),
                    "nome": "Usuário Demo",
                    "email": email,
                    "tipo": "usuario",
                }

                # Gera token JWT
                token = jwt.encode(
                    {
                        "user_id": user_data["id"],
                        "email": email,
                        "exp": datetime.now().timestamp() + (24 * 3600),
                    },
                    self.app.config["SECRET_KEY"],
                    algorithm="HS256",
                )

                return jsonify({"token": token, "user": user_data, "expires_in": 86400})

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/mobile/motos", methods=["GET"])
        def mobile_motos():
            """Lista motos disponíveis para o app mobile"""
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, modelo, placa, status, bateria, zona, ultima_atualizacao
                    FROM motos_patio 
                    WHERE status IN ('disponivel', 'em_uso')
                    ORDER BY status, bateria DESC
                """
                )

                motos = [dict(row) for row in cursor.fetchall()]
                conn.close()

                return jsonify(
                    {
                        "motos": motos,
                        "total": len(motos),
                        "disponiveis": len(
                            [m for m in motos if m["status"] == "disponivel"]
                        ),
                    }
                )

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/mobile/motos/<moto_id>/reservar", methods=["POST"])
        def mobile_reservar_moto(moto_id):
            """Reserva uma moto via app mobile"""
            try:
                data = request.get_json()
                usuario_id = data.get("usuario_id")

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Atualiza status da moto
                cursor.execute(
                    """
                    UPDATE motos_patio 
                    SET status = 'em_uso', em_uso_por = ?, ultima_atualizacao = ?
                    WHERE id = ? AND status = 'disponivel'
                """,
                    (usuario_id, datetime.now().isoformat(), moto_id),
                )

                if cursor.rowcount == 0:
                    conn.close()
                    return jsonify({"error": "Moto não disponível"}), 400

                # Registra histórico
                cursor.execute(
                    """
                    INSERT INTO historico_uso (id, moto_id, usuario_id, inicio_uso)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        str(uuid.uuid4()),
                        moto_id,
                        usuario_id,
                        datetime.now().isoformat(),
                    ),
                )

                conn.commit()
                conn.close()

                return jsonify(
                    {"message": "Moto reservada com sucesso", "moto_id": moto_id}
                )

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # Java endpoints
        @self.app.route("/api/java/motos/status", methods=["GET"])
        def java_motos_status():
            """Endpoint para integração com Spring Boot"""
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT 
                        id as motoId,
                        modelo,
                        placa,
                        status,
                        bateria as nivelBateria,
                        localizacao_x as latitude,
                        localizacao_y as longitude,
                        zona,
                        ultima_atualizacao as ultimaAtualizacao
                    FROM motos_patio
                """
                )

                motos = [dict(row) for row in cursor.fetchall()]
                conn.close()

                # Formato Java-friendly
                response = {
                    "success": True,
                    "data": {
                        "motos": motos,
                        "resumo": {
                            "total": len(motos),
                            "disponiveis": len(
                                [m for m in motos if m["status"] == "disponivel"]
                            ),
                            "emUso": len([m for m in motos if m["status"] == "em_uso"]),
                            "manutencao": len(
                                [m for m in motos if m["status"] == "manutencao"]
                            ),
                        },
                    },
                    "timestamp": datetime.now().isoformat(),
                }

                return jsonify(response)

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/java/alertas", methods=["GET", "POST"])
        def java_alertas():
            """Gerenciamento de alertas para Java"""
            if request.method == "GET":
                try:
                    conn = sqlite3.connect(self.db_path)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        SELECT * FROM alertas 
                        WHERE ativo = 1 
                        ORDER BY criado_em DESC
                    """
                    )

                    alertas = [dict(row) for row in cursor.fetchall()]
                    conn.close()

                    return jsonify({"success": True, "alertas": alertas})

                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500

            elif request.method == "POST":
                try:
                    data = request.get_json()

                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT INTO alertas (id, tipo, severidade, titulo, descricao, moto_id, zona, criado_em)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            str(uuid.uuid4()),
                            data.get("tipo", "info"),
                            data.get("severidade", "info"),
                            data.get("titulo", ""),
                            data.get("descricao", ""),
                            data.get("motoId"),
                            data.get("zona"),
                            datetime.now().isoformat(),
                        ),
                    )

                    conn.commit()
                    conn.close()

                    return jsonify({"success": True, "message": "Alerta criado"})

                except Exception as e:
                    return jsonify({"success": False, "error": str(e)}), 500

        # .NET endpoints
        @self.app.route("/api/dotnet/Dashboard/GetMotorcycleData", methods=["GET"])
        def dotnet_motorcycle_data():
            """Endpoint para integração com .NET (formato C#)"""
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT 
                        id as Id,
                        modelo as Model,
                        placa as LicensePlate,
                        status as Status,
                        bateria as BatteryLevel,
                        localizacao_x as LocationX,
                        localizacao_y as LocationY,
                        zona as Zone,
                        ultima_atualizacao as LastUpdate
                    FROM motos_patio
                """
                )

                motorcycles = [dict(row) for row in cursor.fetchall()]
                conn.close()

                # Formato .NET-friendly
                response = {
                    "IsSuccess": True,
                    "Data": {
                        "Motorcycles": motorcycles,
                        "Summary": {
                            "TotalCount": len(motorcycles),
                            "AvailableCount": len(
                                [m for m in motorcycles if m["Status"] == "disponivel"]
                            ),
                            "InUseCount": len(
                                [m for m in motorcycles if m["Status"] == "em_uso"]
                            ),
                            "MaintenanceCount": len(
                                [m for m in motorcycles if m["Status"] == "manutencao"]
                            ),
                        },
                    },
                    "Message": "Data retrieved successfully",
                    "Timestamp": datetime.now().isoformat(),
                }

                return jsonify(response)

            except Exception as e:
                return (
                    jsonify(
                        {
                            "IsSuccess": False,
                            "Error": str(e),
                            "Message": "Failed to retrieve motorcycle data",
                        }
                    ),
                    500,
                )

        @self.app.route("/api/dotnet/Reports/GenerateUsageReport", methods=["POST"])
        def dotnet_usage_report():
            """Gera relatório de uso para .NET"""
            try:
                data = request.get_json()
                start_date = data.get(
                    "StartDate", (datetime.now() - timedelta(days=7)).isoformat()
                )
                end_date = data.get("EndDate", datetime.now().isoformat())

                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
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
                """,
                    (start_date, end_date),
                )

                report_data = [dict(row) for row in cursor.fetchall()]
                conn.close()

                return jsonify(
                    {
                        "IsSuccess": True,
                        "ReportData": report_data,
                        "GeneratedAt": datetime.now().isoformat(),
                        "Period": {"StartDate": start_date, "EndDate": end_date},
                    }
                )

            except Exception as e:
                return jsonify({"IsSuccess": False, "Error": str(e)}), 500

        # Database endpoints
        @self.app.route("/api/database/backup", methods=["POST"])
        def database_backup():
            """Cria backup do banco de dados"""
            try:
                backup_path = (
                    f"backup_visionmoto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                )

                # Copia banco atual
                import shutil

                shutil.copy2(self.db_path, backup_path)

                return jsonify(
                    {
                        "success": True,
                        "backup_file": backup_path,
                        "created_at": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/database/analytics", methods=["GET"])
        def database_analytics():
            """Retorna analytics do banco de dados"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Estatísticas gerais
                stats = {}

                # Contagem de tabelas
                tables = [
                    "motos_patio",
                    "usuarios",
                    "alertas",
                    "dispositivos_iot",
                    "historico_uso",
                    "detections",
                ]
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]

                # Estatísticas de uso
                cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as total_usos,
                        AVG(tempo_uso) as tempo_medio,
                        SUM(distancia_percorrida) as distancia_total
                    FROM historico_uso
                    WHERE inicio_uso >= date('now', '-30 days')
                """
                )

                uso_stats = cursor.fetchone()
                stats.update(
                    {
                        "usos_ultimo_mes": uso_stats[0],
                        "tempo_medio_uso": uso_stats[1] or 0,
                        "distancia_total_mes": uso_stats[2] or 0,
                    }
                )

                conn.close()

                return jsonify(
                    {
                        "success": True,
                        "analytics": stats,
                        "generated_at": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        # IoT endpoints
        @self.app.route("/api/iot/devices", methods=["GET"])
        def iot_devices():
            """Lista dispositivos IoT"""
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM dispositivos_iot ORDER BY nome")
                devices = [dict(row) for row in cursor.fetchall()]
                conn.close()

                return jsonify(
                    {
                        "devices": devices,
                        "total": len(devices),
                        "online": len([d for d in devices if d["status"] == "online"]),
                    }
                )

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/iot/devices/<device_id>/data", methods=["POST"])
        def iot_device_data(device_id):
            """Recebe dados de dispositivo IoT"""
            try:
                data = request.get_json()

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Atualiza dados do dispositivo
                cursor.execute(
                    """
                    UPDATE dispositivos_iot 
                    SET dados_sensor = ?, ultima_comunicacao = ?, status = 'online'
                    WHERE id = ?
                """,
                    (json.dumps(data), datetime.now().isoformat(), device_id),
                )

                conn.commit()
                conn.close()

                return jsonify({"success": True, "message": "Dados recebidos"})

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        # Dashboard
        @self.app.route("/dashboard")
        def dashboard():
            return send_from_directory(self.app.static_folder, "index.html")

        @self.app.route("/static/<path:path>")
        def send_static(path):
            return send_from_directory(self.app.static_folder, path)

    def run(self, host="0.0.0.0", port=5001, debug=False):
        """Executa a API de integração"""
        print(f"🚀 VisionMoto Integration API rodando em http://{host}:{port}")
        print(f"📱 Mobile endpoints: http://{host}:{port}/api/mobile/*")
        print(f"☕ Java endpoints: http://{host}:{port}/api/java/*")
        print(f"🔷 .NET endpoints: http://{host}:{port}/api/dotnet/*")
        print(f"🗄️  Database endpoints: http://{host}:{port}/api/database/*")
        print(f"🌐 IoT endpoints: http://{host}:{port}/api/iot/*")
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Função principal"""
    api = VisionMotoIntegrationAPI()
    api.run()


if __name__ == "__main__":
    main()
