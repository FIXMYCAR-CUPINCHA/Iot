#!/usr/bin/env python3
"""
Script de inicialização para VisionMoto - Sistema Integrado
Desenvolvido para o 4º Sprint - Challenge 2025
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def print_banner():
    """Exibe banner do sistema"""
    print("🚀 VisionMoto v2.0 - Sistema Integrado")
    print("Challenge 2025 - 4º Sprint")
    print("-" * 40)

def check_dependencies():
    """Verifica dependências necessárias"""
    print("🔍 Verificando dependências...")
    
    try:
        import flask
        import cv2
        import ultralytics
        print("✅ Dependências Python OK")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False
    
    return True

def start_integration_api():
    """Inicia API de integração"""
    print("🚀 Iniciando API de Integração...")
    
    try:
        from src.backend.integration_api import VisionMotoIntegrationAPI
        api = VisionMotoIntegrationAPI()
        
        # Executa em thread separada
        def run_api():
            api.run(host='0.0.0.0', port=5001, debug=False)
        
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        
        time.sleep(2)  # Aguarda inicialização
        print("✅ API de Integração rodando em http://localhost:5001")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
        return False

def start_vision_system():
    """Inicia sistema de visão computacional"""
    print("👁️  Iniciando Sistema de Visão...")
    
    try:
        # Executa sistema principal em processo separado
        process = subprocess.Popen([
            sys.executable, 'visionmoto.py', 'demo'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(3)  # Aguarda inicialização
        
        if process.poll() is None:  # Processo ainda rodando
            print("✅ Sistema de Visão iniciado")
            return process
        else:
            print("❌ Erro ao iniciar Sistema de Visão")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar visão: {e}")
        return None

def show_integration_info():
    """Mostra informações essenciais"""
    print("\n✅ Sistema iniciado com sucesso!")
    print("🌐 API Principal: http://localhost:5001")
    print("📊 Dashboard: http://localhost:5001/dashboard")
    print("🔍 Health Check: http://localhost:5001/health")
    print("\n📋 APIs disponíveis:")
    print("  • Mobile: /api/mobile/*")
    print("  • Java: /api/java/*")
    print("  • .NET: /api/dotnet/*")
    print("  • Database: /api/database/*")
    print("  • IoT: /api/iot/*")

def main():
    """Função principal"""
    print_banner()
    
    # Verifica dependências
    if not check_dependencies():
        sys.exit(1)
    
    print("\n🎯 INICIANDO SISTEMA INTEGRADO...")
    print("-" * 40)
    
    # Inicia API de integração
    if not start_integration_api():
        print("❌ Falha ao iniciar API de integração")
        sys.exit(1)
    
    # Inicia sistema de visão
    vision_process = start_vision_system()
    
    # Mostra informações
    show_integration_info()
    print("\n💡 Pressione Ctrl+C para parar o sistema")
    
    try:
        # Mantém o script rodando
        while True:
            time.sleep(1)
            
            # Verifica se processo de visão ainda está rodando
            if vision_process and vision_process.poll() is not None:
                print("\n⚠️  Sistema de visão parou. Reiniciando...")
                vision_process = start_vision_system()
                
    except KeyboardInterrupt:
        print("\n\n🛑 Parando sistema...")
        
        if vision_process:
            vision_process.terminate()
            print("✅ Sistema de visão parado")
        
        print("✅ Sistema VisionMoto parado com sucesso!")

if __name__ == "__main__":
    main()
