#!/usr/bin/env python3
"""
Testes para a API Refatorada do VisionMoto
Cobertura abrangente de todos os endpoints
"""

import json
import os
import sys
import pytest

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from backend.app import create_app


@pytest.fixture
def app():
    """Fixture para criar aplicação de teste"""
    os.environ["FLASK_ENV"] = "testing"
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
    
    test_config = {
        "TESTING": True,
        "DATABASE_PATH": ":memory:",
        "SECRET_KEY": "test-secret-key"
    }
    
    app = create_app(config=test_config)
    yield app
    
    # Cleanup
    os.environ.pop("SECRET_KEY", None)
    os.environ.pop("FLASK_ENV", None)


@pytest.fixture
def client(app):
    """Fixture para cliente de teste"""
    return app.test_client()


class TestBasicEndpoints:
    """Testes de endpoints básicos"""
    
    def test_index(self, client):
        """Testa endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["service"] == "VisionMoto Integration API"
        assert data["version"] == "3.0"
        assert "endpoints" in data
    
    def test_health(self, client):
        """Testa health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_not_found(self, client):
        """Testa rota inexistente"""
        response = client.get("/rota/inexistente")
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert "error" in data


class TestMobileEndpoints:
    """Testes de endpoints Mobile"""
    
    def test_list_motos(self, client):
        """Testa listagem de motos"""
        response = client.get("/api/mobile/motos")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert "motos" in data
        assert "total" in data
        assert "disponiveis" in data
    
    def test_buscar_moto_existente(self, client):
        """Testa busca de moto existente"""
        response = client.get("/api/mobile/motos/buscar/ABC-1234")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["encontrada"] is True
        assert "moto" in data
    
    def test_buscar_moto_inexistente(self, client):
        """Testa busca de moto inexistente"""
        response = client.get("/api/mobile/motos/buscar/XXX-9999")
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert "error" in data
    
    def test_login_invalid_json(self, client):
        """Testa login com JSON inválido"""
        response = client.post(
            "/api/mobile/auth/login",
            data="invalid json",
            content_type="application/json"
        )
        assert response.status_code == 400
    
    def test_login_missing_fields(self, client):
        """Testa login sem campos obrigatórios"""
        response = client.post(
            "/api/mobile/auth/login",
            data=json.dumps({"email": "test@test.com"}),
            content_type="application/json"
        )
        assert response.status_code == 400
    
    def test_login_invalid_email(self, client):
        """Testa login com email inválido"""
        response = client.post(
            "/api/mobile/auth/login",
            data=json.dumps({"email": "invalid-email", "senha": "123456"}),
            content_type="application/json"
        )
        assert response.status_code == 400
    
    def test_reservar_moto_sem_usuario(self, client):
        """Testa reserva sem usuário"""
        response = client.post(
            "/api/mobile/motos/MOTO001/reservar",
            data=json.dumps({}),
            content_type="application/json"
        )
        assert response.status_code == 400


class TestJavaEndpoints:
    """Testes de endpoints Java"""
    
    def test_motos_status(self, client):
        """Testa status das motos para Java"""
        response = client.get("/api/java/motos/status")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
        assert "motos" in data["data"]
        assert "resumo" in data["data"]
    
    def test_buscar_moto_java(self, client):
        """Testa busca de moto para Java"""
        response = client.get("/api/java/motos/buscar/ABC-1234")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["success"] is True
        assert "data" in data
    
    def test_alertas_get(self, client):
        """Testa GET de alertas Java"""
        response = client.get("/api/java/alertas")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["success"] is True
        assert "alertas" in data
    
    def test_alertas_post_invalid(self, client):
        """Testa POST de alerta sem dados"""
        response = client.post(
            "/api/java/alertas",
            data="",
            content_type="application/json"
        )
        assert response.status_code == 400


class TestDotNetEndpoints:
    """Testes de endpoints .NET"""
    
    def test_get_motorcycle_data(self, client):
        """Testa dados de motos para .NET"""
        response = client.get("/api/dotnet/Dashboard/GetMotorcycleData")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["IsSuccess"] is True
        assert "Data" in data
        assert "Motorcycles" in data["Data"]
    
    def test_find_by_plate(self, client):
        """Testa busca por placa para .NET"""
        response = client.get("/api/dotnet/Motorcycles/FindByPlate/ABC-1234")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["IsSuccess"] is True


class TestIoTEndpoints:
    """Testes de endpoints IoT"""
    
    def test_list_devices(self, client):
        """Testa listagem de dispositivos"""
        response = client.get("/api/iot/devices")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert "devices" in data
        assert "total" in data
        assert "online" in data
    
    def test_criar_evento_sem_idempotency(self, client):
        """Testa criação de evento sem idempotency key"""
        response = client.post(
            "/api/iot/eventos",
            data=json.dumps({"type": "alert"}),
            content_type="application/json"
        )
        assert response.status_code == 400
    
    def test_criar_evento_com_idempotency(self, client):
        """Testa criação de evento com idempotency"""
        response = client.post(
            "/api/iot/eventos",
            data=json.dumps({"type": "alert", "deviceId": "SENSOR001"}),
            content_type="application/json",
            headers={"Idempotency-Key": "test-key-123"}
        )
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert "alertId" in data
    
    def test_idempotency_duplicate(self, client):
        """Testa idempotência com chave duplicada"""
        # Primeira requisição
        client.post(
            "/api/iot/eventos",
            data=json.dumps({"type": "alert"}),
            content_type="application/json",
            headers={"Idempotency-Key": "duplicate-key"}
        )
        
        # Segunda requisição com mesma chave
        response = client.post(
            "/api/iot/eventos",
            data=json.dumps({"type": "alert"}),
            content_type="application/json",
            headers={"Idempotency-Key": "duplicate-key"}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("idempotent") is True


class TestDatabaseEndpoints:
    """Testes de endpoints Database"""
    
    def test_analytics(self, client):
        """Testa analytics do banco"""
        response = client.get("/api/database/analytics")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data["success"] is True
        assert "analytics" in data


class TestValidation:
    """Testes de validação de input"""
    
    def test_pagination_invalid_limit(self, client):
        """Testa paginação com limite inválido"""
        response = client.get("/api/mobile/alertas?limit=invalid")
        assert response.status_code == 400
    
    def test_pagination_negative_offset(self, client):
        """Testa paginação com offset negativo"""
        response = client.get("/api/mobile/alertas?offset=-1")
        # Deve aceitar mas corrigir para 0
        assert response.status_code == 200
    
    def test_pagination_excessive_limit(self, client):
        """Testa paginação com limite excessivo"""
        response = client.get("/api/mobile/alertas?limit=1000")
        # Deve aceitar mas limitar a 100
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
