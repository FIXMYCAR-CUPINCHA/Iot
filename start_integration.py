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
import logging
from pathlib import Path

from src.constants import API_STARTUP_DELAY_SECONDS, VISION_SYSTEM_STARTUP_DELAY_SECONDS

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Exibe banner do sistema"""
    logger.info("🚀 VisionMoto v2.0 - Sistema Integrado")
    logger.info("Challenge 2025 - 4º Sprint")
    logger.info("-" * 40)

def check_dependencies():
    """Verifica dependências necessárias"""
    logger.info("🔍 Verificando dependências...")
    
    try:
        import flask
        import cv2
        import ultralytics
        logger.info("✅ Dependências Python OK")
        return True
    except ImportError as e:
        logger.error(f"❌ Dependência faltando: {e}")
        logger.info("💡 Execute: pip install -r requirements.txt")
        return False

def start_integration_api():
    """Inicia API de integração"""
    logger.info("🚀 Iniciando API de Integração...")
    
    try:
        from src.backend.app import app
        
        # Executa em thread separada
        def run_api():
            app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
        
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        
        time.sleep(API_STARTUP_DELAY_SECONDS)
        logger.info("✅ API de Integração rodando em http://localhost:5001")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar API: {e}", exc_info=True)
        return False

def start_vision_system():
    """Inicia sistema de visão computacional"""
    logger.info("👁️  Iniciando Sistema de Visão...")
    
    try:
        # Executa sistema principal em processo separado
        process = subprocess.Popen([
            sys.executable, 'visionmoto.py', 'demo'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(VISION_SYSTEM_STARTUP_DELAY_SECONDS)
        
        if process.poll() is None:  # Processo ainda rodando
            logger.info("✅ Sistema de Visão iniciado")
            return process
        else:
            logger.error("❌ Erro ao iniciar Sistema de Visão")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar visão: {e}", exc_info=True)
        return None

def show_integration_info():
    """Mostra informações essenciais"""
    logger.info("\n✅ Sistema iniciado com sucesso!")
    logger.info("🌐 API Principal: http://localhost:5001")
    logger.info("📊 Dashboard: http://localhost:5001/dashboard")
    logger.info("🔍 Health Check: http://localhost:5001/health")
    logger.info("\n📋 APIs disponíveis:")
    logger.info("  • Mobile: /api/mobile/*")
    logger.info("  • Java: /api/java/*")
    logger.info("  • .NET: /api/dotnet/*")
    logger.info("  • Database: /api/database/*")
    logger.info("  • IoT: /api/iot/*")

def main():
    """Função principal"""
    print_banner()
    
    # Verifica dependências
    if not check_dependencies():
        sys.exit(1)
    
    logger.info("\n🎯 INICIANDO SISTEMA INTEGRADO...")
    logger.info("-" * 40)
    
    # Inicia API de integração
    if not start_integration_api():
        logger.error("❌ Falha ao iniciar API de integração")
        sys.exit(1)
    
    # Inicia sistema de visão
    vision_process = start_vision_system()
    
    # Mostra informações
    show_integration_info()
    logger.info("\n💡 Pressione Ctrl+C para parar o sistema")
    
    try:
        # Mantém o script rodando
        while True:
            time.sleep(1)
            
            # Verifica se processo de visão ainda está rodando
            if vision_process and vision_process.poll() is not None:
                logger.warning("\n⚠️  Sistema de visão parou. Reiniciando...")
                vision_process = start_vision_system()
                
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Parando sistema...")
        
        if vision_process:
            vision_process.terminate()
            logger.info("✅ Sistema de visão parado")
        
        logger.info("✅ Sistema VisionMoto parado com sucesso!")

if __name__ == "__main__":
    main()
