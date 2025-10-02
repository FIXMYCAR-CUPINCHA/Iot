@echo off
echo ========================================
echo VisionMoto - Sistema Permanente
echo ========================================
echo.
echo Iniciando sistema completo...
echo Para parar: pressione CTRL+C ou ESC na janela do video
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.8+ e tente novamente.
    pause
    exit /b 1
)

REM Executa o sistema permanente
python run_permanent_system.py

echo.
echo Sistema finalizado.
pause
