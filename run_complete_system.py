#!/usr/bin/env python3
"""
VisionMoto - Script de Inicialização
Wrapper para executar o sistema completo
"""

import os
import sys
import subprocess

def main():
    """Executa o sistema completo VisionMoto"""
    # Caminho para o script real
    script_path = os.path.join(os.path.dirname(__file__), 'demos', 'run_complete_system.py')
    
    if not os.path.exists(script_path):
        print("❌ Erro: Script não encontrado em demos/run_complete_system.py")
        return 1
    
    print("🚀 Iniciando VisionMoto - Sistema Completo")
    print("📁 Executando:", script_path)
    
    try:
        # Executa o script principal
        result = subprocess.run([sys.executable, script_path], 
                              cwd=os.path.dirname(__file__))
        return result.returncode
    except KeyboardInterrupt:
        print("\n⏹️ Sistema interrompido pelo usuário")
        return 0
    except Exception as e:
        print(f"❌ Erro ao executar sistema: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
