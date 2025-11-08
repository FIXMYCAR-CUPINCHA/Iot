#!/bin/bash
# Script para testar a refatoração do VisionMoto

echo "🧪 Testando Refatoração do VisionMoto v3.0"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de testes
PASSED=0
FAILED=0

# Função para testar
test_command() {
    local description=$1
    local command=$2
    
    echo -n "Testing: $description... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
    fi
}

echo "📦 1. Verificando estrutura de arquivos"
echo "----------------------------------------"
test_command "Models package" "test -f src/models/__init__.py"
test_command "Moto model" "test -f src/models/moto.py"
test_command "Alert model" "test -f src/models/alert.py"
test_command "User model" "test -f src/models/user.py"
test_command "Routes package" "test -f src/routes/__init__.py"
test_command "Mobile routes" "test -f src/routes/mobile_routes.py"
test_command "Java routes" "test -f src/routes/java_routes.py"
test_command ".NET routes" "test -f src/routes/dotnet_routes.py"
test_command "IoT routes" "test -f src/routes/iot_routes.py"
test_command "Database routes" "test -f src/routes/database_routes.py"
test_command "Formatters package" "test -f src/formatters/__init__.py"
test_command "Auth service" "test -f src/services/auth_service.py"
test_command "New app.py" "test -f src/backend/app.py"
test_command "Refactoring guide" "test -f REFACTORING_GUIDE.md"
test_command "New tests" "test -f tests/test_app_refactored.py"
echo ""

echo "🔍 2. Verificando sintaxe Python"
echo "----------------------------------------"
test_command "Models syntax" "python -m py_compile src/models/*.py"
test_command "Routes syntax" "python -m py_compile src/routes/*.py"
test_command "Formatters syntax" "python -m py_compile src/formatters/*.py"
test_command "Services syntax" "python -m py_compile src/services/auth_service.py"
test_command "App syntax" "python -m py_compile src/backend/app.py"
echo ""

echo "📚 3. Verificando imports"
echo "----------------------------------------"
test_command "Can import app" "python -c 'from src.backend.app import create_app'"
test_command "Can import models" "python -c 'from src.models import Moto, Alert, User'"
test_command "Can import formatters" "python -c 'from src.formatters import MobileFormatter, JavaFormatter, DotNetFormatter'"
test_command "Can import routes" "python -c 'from src.routes import mobile_bp, java_bp, dotnet_bp'"
echo ""

echo "🧪 4. Executando testes"
echo "----------------------------------------"
if command -v pytest &> /dev/null; then
    echo "Running pytest..."
    if pytest tests/test_app_refactored.py -v --tb=short; then
        echo -e "${GREEN}✓ All tests passed${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠ pytest not installed, skipping tests${NC}"
fi
echo ""

echo "📊 RESULTADOS"
echo "=========================================="
echo -e "Testes passados: ${GREEN}$PASSED${NC}"
echo -e "Testes falhados: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 SUCESSO! Refatoração completa e funcional!${NC}"
    echo ""
    echo "Próximos passos:"
    echo "1. Leia REFACTORING_GUIDE.md"
    echo "2. Execute: python src/backend/app.py"
    echo "3. Teste os endpoints em http://localhost:5001"
    exit 0
else
    echo -e "${RED}❌ Alguns testes falharam. Verifique os erros acima.${NC}"
    exit 1
fi
