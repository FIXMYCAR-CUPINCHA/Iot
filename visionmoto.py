#!/usr/bin/env python3
"""
VisionMoto - Sistema Principal
Script unificado para executar todas as funcionalidades do VisionMoto
"""

import sys
import os
import argparse
import subprocess

def run_demo():
    """Executa a demonstração completa"""
    print("🎯 Executando demonstração completa do VisionMoto...")
    subprocess.run([sys.executable, "demos/run_complete_system.py"])

def run_demo_final():
    """Executa a demonstração final"""
    print("🎯 Executando demonstração final do VisionMoto...")
    subprocess.run([sys.executable, "demos/demo_final.py"])

def run_vision_only():
    """Executa apenas detecção de visão computacional"""
    print("🔍 Executando apenas detecção de visão computacional...")
    subprocess.run([sys.executable, "demos/main.py"])

def run_backend():
    """Executa apenas o backend"""
    print("🌐 Executando backend Flask...")
    subprocess.run([sys.executable, "-m", "src.backend.app"])

def run_tests():
    """Executa testes do sistema"""
    print("🧪 Executando testes do sistema...")
    subprocess.run([sys.executable, "tests/test_system.py"])
    subprocess.run([sys.executable, "tests/test_backend.py"])

def generate_data():
    """Gera dados de teste"""
    print("📊 Gerando dados de teste...")
    subprocess.run([sys.executable, "scripts/generate_test_data.py"])

def generate_report():
    """Gera relatório de performance"""
    print("📈 Gerando relatório de performance...")
    subprocess.run([sys.executable, "reports/performance_report.py"])

def show_help():
    """Mostra ajuda com todas as opções"""
    help_text = """
🎯 VisionMoto - Sistema de Detecção de Motos com IoT

COMANDOS DISPONÍVEIS:
  demo          - Executa demonstração completa (recomendado)
  demo-final    - Executa demonstração final
  vision        - Executa apenas detecção de visão computacional
  backend       - Executa apenas o backend Flask
  tests         - Executa todos os testes
  data          - Gera dados de teste
  report        - Gera relatório de performance
  help          - Mostra esta ajuda

EXEMPLOS:
  python visionmoto.py demo          # Demonstração completa
  python visionmoto.py backend       # Apenas backend
  python visionmoto.py tests         # Executar testes

ESTRUTURA DO PROJETO:
  📁 demos/     - Demonstrações e scripts principais
  📁 scripts/   - Scripts utilitários
  📁 tests/     - Testes do sistema
  📁 reports/   - Relatórios e análises
  📁 src/       - Código fonte principal
  📁 assets/    - Recursos (vídeos, imagens)

Para mais informações, consulte o README.md
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
        'demo-final': run_demo_final,
        'vision': run_vision_only,
        'backend': run_backend,
        'tests': run_tests,
        'data': generate_data,
        'report': generate_report,
        'help': show_help,
        '--help': show_help,
        '-h': show_help
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ Comando '{command}' não reconhecido.")
        print("Use 'python visionmoto.py help' para ver todos os comandos disponíveis.")

if __name__ == "__main__":
    main()
