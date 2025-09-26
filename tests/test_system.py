#!/usr/bin/env python3
"""
Teste simples do sistema VisionMoto
"""

import sys
import os
import time
import requests

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.database import DatabaseManager
from src.iot.sensor_simulator import IoTDeviceSimulator

def test_database():
    """Testa o banco de dados"""
    print("🗄️ Testando banco de dados...")
    
    db = DatabaseManager()
    db.initialize()
    
    # Testa inserção
    test_detections = [{
        'class': 3,
        'class_name': 'motorbike',
        'confidence': 0.85,
        'bbox': [100, 100, 200, 200],
        'area': 10000
    }]
    
    db.save_detections(1, test_detections, 25.0, 1, 1, 0.1)
    
    # Testa consulta
    stats = db.get_statistics()
    print(f"✅ Banco funcionando - {stats['total_detections']} detecções")
    
    return True

def test_iot_simulator():
    """Testa o simulador IoT"""
    print("📡 Testando simulador IoT...")
    
    simulator = IoTDeviceSimulator("http://localhost:5000")
    
    # Testa geração de dados
    sensor = simulator.sensors[0]
    data = sensor.generate_data()
    
    print(f"✅ Simulador funcionando - Sensor {sensor.sensor_id}: {data['is_active']}")
    
    return True

def test_api():
    """Testa a API"""
    print("🌐 Testando API...")
    
    try:
        response = requests.get("http://localhost:5000/metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API funcionando - {data.get('total_events', 0)} eventos")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API não disponível: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 VisionMoto - Teste do Sistema")
    print("=" * 40)
    
    tests = [
        ("Banco de Dados", test_database),
        ("Simulador IoT", test_iot_simulator),
        ("API Backend", test_api)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro em {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n📊 RESULTADOS DOS TESTES:")
    print("=" * 30)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema funcionando!")
    else:
        print("⚠️ Alguns testes falharam. Verifique os componentes.")

if __name__ == "__main__":
    main()
