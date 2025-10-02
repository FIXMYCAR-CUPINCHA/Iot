# VisionMoto - Sistema Permanente (PowerShell)
# Script para rodar o sistema completo permanentemente

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VisionMoto - Sistema Permanente" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Iniciando sistema completo..." -ForegroundColor Green
Write-Host "Para parar: pressione CTRL+C ou ESC na janela do video" -ForegroundColor Yellow
Write-Host ""

# Verifica se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale Python 3.8+ e tente novamente." -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verifica se o arquivo existe
if (-not (Test-Path "run_permanent_system.py")) {
    Write-Host "ERRO: Arquivo run_permanent_system.py não encontrado!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Executa o sistema permanente
try {
    Write-Host "Executando sistema..." -ForegroundColor Green
    python run_permanent_system.py
} catch {
    Write-Host "ERRO ao executar o sistema: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Sistema finalizado." -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
}
