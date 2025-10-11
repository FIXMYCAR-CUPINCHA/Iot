#!/bin/bash
# Script para testar CI/CD localmente antes de fazer push
# Simula o que o GitHub Actions fará

set -e

echo "🧪 Testando CI/CD VisionMoto localmente..."
echo "================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica se está no diretório correto
if [ ! -f "src/backend/integration_api.py" ]; then
    log_error "Execute este script na raiz do projeto VisionMoto"
    exit 1
fi

# 1. Verificação de dependências
log_info "1. Verificando dependências Python..."
if ! python3 -c "import flask, cv2, ultralytics" 2>/dev/null; then
    log_warn "Algumas dependências não estão instaladas"
    log_info "Instalando dependências..."
    pip3 install -r requirements.txt
fi

# 2. Verificação de sintaxe
log_info "2. Verificando sintaxe Python..."
find src/ -name "*.py" -exec python3 -m py_compile {} \;
log_info "✅ Sintaxe OK"

# 3. Lint com flake8
log_info "3. Executando lint (flake8)..."
if command -v flake8 &> /dev/null; then
    flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=__pycache__
    log_info "✅ Lint OK"
else
    log_warn "flake8 não instalado, pulando..."
fi

# 4. Formatação com black
log_info "4. Verificando formatação (black)..."
if command -v black &> /dev/null; then
    black --check --diff src/
    log_info "✅ Formatação OK"
else
    log_warn "black não instalado, pulando..."
fi

# 5. Testes unitários
log_info "5. Executando testes unitários..."
if command -v pytest &> /dev/null; then
    pytest tests/test_integration_api.py -v --tb=short
    log_info "✅ Testes unitários OK"
else
    log_warn "pytest não instalado, pulando testes..."
fi

# 6. Verificação de segurança
log_info "6. Verificação de segurança..."
if command -v bandit &> /dev/null; then
    bandit -r src/ -f json -o bandit-local-report.json
    log_info "✅ Verificação de segurança OK"
else
    log_warn "bandit não instalado, pulando..."
fi

# 7. Teste de build Docker
log_info "7. Testando build Docker..."
if command -v docker &> /dev/null; then
    docker build -t visionmoto-local-test .
    log_info "✅ Docker build OK"
    
    # Teste rápido da imagem
    log_info "Testando imagem Docker..."
    docker run --rm -d -p 5002:5001 --name visionmoto-test visionmoto-local-test
    sleep 10
    
    if curl -f http://localhost:5002/health 2>/dev/null; then
        log_info "✅ Docker container OK"
    else
        log_warn "Container não respondeu no health check"
    fi
    
    docker stop visionmoto-test 2>/dev/null || true
    docker rmi visionmoto-local-test 2>/dev/null || true
else
    log_warn "Docker não disponível, pulando..."
fi

# 8. Teste de API endpoints
log_info "8. Testando API endpoints..."
python3 src/backend/integration_api.py &
API_PID=$!
sleep 5

# Testa endpoints principais
ENDPOINTS=(
    "http://localhost:5001/health"
    "http://localhost:5001/api/java/motos/status"
    "http://localhost:5001/api/dotnet/Dashboard/GetMotorcycleData"
    "http://localhost:5001/api/mobile/motos"
    "http://localhost:5001/api/iot/devices"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -f "$endpoint" >/dev/null 2>&1; then
        log_info "✅ $endpoint OK"
    else
        log_error "❌ $endpoint FAILED"
    fi
done

# Para a API
kill $API_PID 2>/dev/null || true
sleep 2

# 9. Verificação de arquivos obrigatórios
log_info "9. Verificando arquivos obrigatórios..."
REQUIRED_FILES=(
    "README_SPRINT4.md"
    "Dockerfile"
    "docker-compose.yml"
    "requirements.txt"
    ".github/workflows/ci-cd.yml"
    ".github/workflows/pr-check.yml"
    "src/backend/integration_api.py"
    "start_integration.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_info "✅ $file existe"
    else
        log_error "❌ $file não encontrado"
    fi
done

# 10. Verificação de documentação
log_info "10. Verificando documentação..."
if grep -q "Challenge 2025" README_SPRINT4.md 2>/dev/null; then
    log_info "✅ Documentação atualizada"
else
    log_warn "Documentação pode estar desatualizada"
fi

# 11. Limpeza
log_info "11. Limpeza..."
rm -f bandit-local-report.json
rm -rf __pycache__ src/__pycache__ src/backend/__pycache__
rm -rf .pytest_cache htmlcov .coverage

echo ""
echo "================================================"
log_info "🎉 Verificação local concluída!"
echo ""
log_info "Próximos passos:"
echo "  1. git add ."
echo "  2. git commit -m 'feat: sua mensagem'"
echo "  3. git push origin sua-branch"
echo ""
log_info "O GitHub Actions executará automaticamente após o push."
echo "================================================"
