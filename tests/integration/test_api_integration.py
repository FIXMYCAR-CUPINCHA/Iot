#!/usr/bin/env python3
"""
Testes de integração para VisionMoto API
"""

import pytest
import requests
import time
import subprocess
import sys
import os
import signal

class TestAPIIntegration:
    """Testes de integração da API"""
    
    @classmethod
    def setup_class(cls):
        """Inicia a API para testes"""
        cls.api_process = None
        cls.base_url = 'http://localhost:5001'
        
        # Inicia a API em background
        try:
            cls.api_process = subprocess.Popen([
                sys.executable, 
                'src/backend/integration_api.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Aguarda a API inicializar
            time.sleep(5)
            
            # Verifica se a API está respondendo
            for _ in range(10):
                try:
                    response = requests.get(f'{cls.base_url}/health', timeout=2)
                    if response.status_code == 200:
                        break
                except:
                    time.sleep(1)
            else:
                raise Exception("API não iniciou corretamente")
                
        except Exception as e:
            if cls.api_process:
                cls.api_process.terminate()
            pytest.skip(f"Não foi possível iniciar a API: {e}")
    
    @classmethod
    def teardown_class(cls):
        """Para a API após os testes"""
        if cls.api_process:
            cls.api_process.terminate()
            cls.api_process.wait()
    
    def test_health_check(self):
        """Testa health check da API"""
        response = requests.get(f'{self.base_url}/health')
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_java_endpoints(self):
        """Testa endpoints Java"""
        # Testa status das motos
        response = requests.get(f'{self.base_url}/api/java/motos/status')
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] is True
        assert len(data['data']['motos']) > 0
        
        # Testa alertas
        response = requests.get(f'{self.base_url}/api/java/alertas')
        assert response.status_code == 200
    
    def test_dotnet_endpoints(self):
        """Testa endpoints .NET"""
        response = requests.get(f'{self.base_url}/api/dotnet/Dashboard/GetMotorcycleData')
        assert response.status_code == 200
        
        data = response.json()
        assert data['IsSuccess'] is True
        assert len(data['Data']['Motorcycles']) > 0
    
    def test_mobile_endpoints(self):
        """Testa endpoints Mobile"""
        # Testa login
        login_data = {
            'email': 'test@mottu.com',
            'senha': '123456'
        }
        response = requests.post(f'{self.base_url}/api/mobile/auth/login', json=login_data)
        assert response.status_code == 200
        
        # Testa listagem de motos
        response = requests.get(f'{self.base_url}/api/mobile/motos')
        assert response.status_code == 200
        
        data = response.json()
        assert 'motos' in data
        assert data['total'] > 0
    
    def test_iot_endpoints(self):
        """Testa endpoints IoT"""
        response = requests.get(f'{self.base_url}/api/iot/devices')
        assert response.status_code == 200
        
        data = response.json()
        assert 'devices' in data
        assert data['total'] > 0
    
    def test_database_endpoints(self):
        """Testa endpoints de banco de dados"""
        response = requests.get(f'{self.base_url}/api/database/analytics')
        assert response.status_code == 200
        
        data = response.json()
        assert data['success'] is True
        assert 'analytics' in data
    
    def test_api_performance(self):
        """Testa performance básica da API"""
        start_time = time.time()
        
        # Faz múltiplas requisições
        for _ in range(10):
            response = requests.get(f'{self.base_url}/health')
            assert response.status_code == 200
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        # Verifica se a resposta média é menor que 1 segundo
        assert avg_time < 1.0, f"API muito lenta: {avg_time}s por requisição"
    
    def test_concurrent_requests(self):
        """Testa requisições concorrentes"""
        import threading
        
        results = []
        
        def make_request():
            try:
                response = requests.get(f'{self.base_url}/health', timeout=5)
                results.append(response.status_code == 200)
            except:
                results.append(False)
        
        # Cria 5 threads fazendo requisições simultâneas
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Aguarda todas as threads terminarem
        for thread in threads:
            thread.join()
        
        # Verifica se todas as requisições foram bem-sucedidas
        assert all(results), "Algumas requisições concorrentes falharam"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
