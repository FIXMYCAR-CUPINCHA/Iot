#!/usr/bin/env python3
"""
VisionMoto - Sistema Principal
Challenge 2025 - 4º Sprint
"""

import sys
import subprocess

def run_demo():
    """Executa demonstração completa do sistema"""
    print("🎯 Executando VisionMoto - Sistema Completo...")
    subprocess.run([sys.executable, "demos/demo_final.py"])

def run_integration():
    """Executa sistema integrado com todas as APIs"""
    print("🚀 Executando Sistema Integrado...")
    subprocess.run([sys.executable, "start_integration.py"])

def run_backend():
    """Executa API de integração"""
    print("🌐 Executando API de Integração...")
    subprocess.run([sys.executable, "src/backend/integration_api.py"])

def run_tests():
    """Executa testes do sistema"""
    print("🧪 Executando testes...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])

def show_help():
    """Mostra ajuda"""
    help_text = """
🎯 VisionMoto - Challenge 2025 - 4º Sprint

COMANDOS:
  demo          - Demonstração completa
  integration   - Sistema integrado (APIs)
  backend       - API de integração
  tests         - Executar testes
  help          - Esta ajuda

EXEMPLOS:
  python visionmoto.py demo
  python visionmoto.py integration
  python visionmoto.py backend
"""
    print(help_text)

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()
    
    commands = {
        'demo': run_demo,
        'integration': run_integration,
        'backend': run_backend,
        'tests': run_tests,
        'help': show_help,
        '--help': show_help,
        '-h': show_help
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ Comando '{command}' não reconhecido.")
        show_help()

if __name__ == "__main__":
    main()
