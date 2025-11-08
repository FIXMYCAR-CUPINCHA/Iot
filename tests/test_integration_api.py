#!/usr/bin/env python3
"""
Testes para a API de Integração do VisionMoto
"""

import json
import os
import sys

import pytest

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
# flake8: noqa: E402
from backend.integration_api import VisionMotoIntegrationAPI


@pytest.fixture
def api_client():
    """Fixture para criar cliente da API"""
    # Configura ambiente de teste
    os.environ["FLASK_ENV"] = "development"
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
    
    api = VisionMotoIntegrationAPI(db_path=":memory:")  # Usa SQLite em memória
    
    # Garante que dados iniciais estão populados
    api._populate_initial_data()
    
    with api.app.test_client() as client:
        yield client
    
    # Limpa variáveis de ambiente
    os.environ.pop("SECRET_KEY", None)
    os.environ.pop("FLASK_ENV", None)


def test_health_endpoint(api_client):
    """Testa endpoint de health check"""
    response = api_client.get("/health")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_java_motos_status(api_client):
    """Testa endpoint Java para status das motos"""
    response = api_client.get("/api/java/motos/status")
    
    # Deve retornar 200, não 500
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.data}"

    data = json.loads(response.data)
    assert data["success"] is True
    assert "data" in data
    assert "motos" in data["data"]


def test_dotnet_motorcycle_data(api_client):
    """Testa endpoint .NET para dados das motos"""
    response = api_client.get("/api/dotnet/Dashboard/GetMotorcycleData")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = json.loads(response.data)
    assert data["IsSuccess"] is True
    assert "Data" in data
    assert "Motorcycles" in data["Data"]


def test_mobile_motos(api_client):
    """Testa endpoint mobile para listar motos"""
    response = api_client.get("/api/mobile/motos")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = json.loads(response.data)
    assert "motos" in data
    assert "total" in data


def test_mobile_login(api_client):
    """Testa endpoint mobile para login"""
    login_data = {"email": "test@mottu.com", "senha": "123456"}

    response = api_client.post(
        "/api/mobile/auth/login",
        data=json.dumps(login_data),
        content_type="application/json",
    )
    assert response.status_code == 200

    data = json.loads(response.data)
    assert "token" in data
    assert "user" in data


def test_iot_devices(api_client):
    """Testa endpoint IoT para dispositivos"""
    response = api_client.get("/api/iot/devices")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = json.loads(response.data)
    assert "devices" in data
    assert "online" in data
    assert "total" in data


def test_database_analytics(api_client):
    """Testa endpoint de analytics do banco"""
    response = api_client.get("/api/database/analytics")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = json.loads(response.data)
    assert data["success"] is True
    assert "analytics" in data


def test_java_alertas_get(api_client):
    """Testa GET de alertas Java"""
    response = api_client.get("/api/java/alertas")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = json.loads(response.data)
    assert data["success"] is True
    assert "alertas" in data


def test_java_alertas_post(api_client):
    """Testa POST de alertas Java"""
    alerta_data = {
        "tipo": "warning",
        "severidade": "medium",
        "titulo": "Teste de Alerta",
        "descricao": "Alerta de teste criado automaticamente",
        "motoId": "MOTO001",
        "zona": "A1",
    }

    response = api_client.post(
        "/api/java/alertas",
        data=json.dumps(alerta_data),
        content_type="application/json",
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = json.loads(response.data)
    assert data["success"] is True
    assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
