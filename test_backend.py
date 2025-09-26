#!/usr/bin/env python3
"""
Script para testar o backend diretamente
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.database import DatabaseManager
import requests
import json

def test_database():
    """Testa o banco de dados diretamente"""
    print("🗄️ Testando banco de dados...")
    
    try:
        db = DatabaseManager()
        db.initialize()
        
        # Testa inserção de detecção
        detection_data = {
            'frame': 1,
            'class': 3,
            'class_name': 'motorbike',
            'confidence': 0.85,
            'bbox': [100, 100, 200, 200],
            'area': 10000
        }
        
        db.save_detections(1, [detection_data], 25.0)
        print("✅ Detecção salva no banco")
        
        # Verifica estatísticas
        stats = db.get_statistics()
        print(f"📊 Estatísticas: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return False

def test_api():
    """Testa as APIs do backend"""
    print("\n🌐 Testando APIs...")
    
    try:
        # Testa métricas
        response = requests.get('http://localhost:5000/metrics', timeout=5)
        print(f"✅ /metrics: {response.status_code}")
        
        # Testa dispositivos IoT
        response = requests.get('http://localhost:5000/iot/devices', timeout=5)
        print(f"✅ /iot/devices: {response.status_code}")
        
        # Testa alertas
        response = requests.get('http://localhost:5000/alerts', timeout=5)
        print(f"✅ /alerts: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return False

def send_test_data():
    """Envia dados de teste via API"""
    print("\n📡 Enviando dados de teste...")
    
    # Dados de sensor IoT
    sensor_data = {
        'sensor_id': 'SENSOR_01',
        'moto_id': 'MOTO_123',
        'location': 'Vaga A1',
        'is_active': True,
        'battery_level': 85.0,
        'signal_strength': 90.0,
        'temperature': 25.5,
        'humidity': 60.0,
        'vibration': 1.2
    }
    
    try:
        response = requests.post('http://localhost:5000/iot/sensor', json=sensor_data, timeout=5)
        print(f"📡 Sensor enviado: {response.status_code}")
        
        if response.status_code != 201:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao enviar sensor: {e}")

def main():
    """Função principal"""
    print("🧪 Teste do Backend VisionMoto")
    print("=" * 40)
    
    # Testa banco de dados
    if not test_database():
        return
    
    # Testa APIs
    if not test_api():
        return
    
    # Envia dados de teste
    send_test_data()
    
    print("\n✅ Testes concluídos!")
    print("🌐 Verifique o dashboard: http://localhost:5000")

if __name__ == "__main__":
    main()
