# GitHub Actions - VisionMoto CI/CD

Este diretório contém os workflows de CI/CD para o projeto VisionMoto.

## 📋 Workflows Disponíveis

### 1. `ci-cd.yml` - Pipeline Principal
**Triggers:** Push para `main`, `develop`, `feature/*` e Pull Requests

**Jobs:**
- **code-quality**: Testes em múltiplas versões Python (3.9, 3.10, 3.11)
  - Verificação de sintaxe
  - Lint com flake8
  - Formatação com black
  - Type checking com mypy
  - Security scan com bandit
  - Testes unitários com pytest
  - Coverage report

- **integration-tests**: Testes de integração
  - PostgreSQL e Redis como services
  - Testes de API endpoints
  - Testes de performance básicos

- **docker-build**: Build e push de imagens Docker
  - Multi-platform build (amd64, arm64)
  - Push para GitHub Container Registry
  - Teste da imagem Docker

- **security-scan**: Análise de segurança
  - Trivy scanner (filesystem + config)
  - Upload para GitHub Security tab

- **deploy-staging**: Deploy automático para staging
  - Trigger: push para `develop`
  - Docker Compose deployment

- **deploy-production**: Deploy automático para produção
  - Trigger: push para `main`
  - Requer aprovação manual (environment protection)

- **performance-tests**: Testes de carga com k6
  - Executa após deploy staging
  - Relatórios HTML e JSON

- **notify-and-report**: Notificações e relatórios
  - Comentários automáticos em PRs
  - Notificações Slack
  - Artifacts com relatórios

### 2. `pr-check.yml` - Verificação Rápida de PRs
**Triggers:** Pull Requests para `main` e `develop`

**Jobs:**
- **pr-validation**: Verificação rápida
  - Lint apenas em arquivos modificados
  - Testes unitários básicos
  - Comentário automático no PR com resultados

- **diff-analysis**: Análise de mudanças
  - Identifica arquivos críticos modificados
  - Estatísticas de linhas adicionadas/removidas
  - Upload como artifact

- **security-check-pr**: Verificação de segurança
  - Bandit scan nos arquivos modificados
  - Safety check para dependências
  - Relatório de segurança

## 🔧 Configuração

### Secrets Necessários
Configure os seguintes secrets no repositório GitHub:

```bash
# Docker Hub (opcional, usando GHCR por padrão)
DOCKER_USERNAME=seu_usuario_dockerhub
DOCKER_PASSWORD=seu_token_dockerhub

# Slack (opcional)
SLACK_WEBHOOK=https://hooks.slack.com/services/...
```

### Environments
Configure os environments no GitHub:

- **staging**: Para deploys automáticos da branch `develop`
- **production**: Para deploys da branch `main` (com proteção/aprovação)

## 📊 Métricas e Thresholds

### Code Coverage
- **Mínimo**: 70%
- **Target**: 85%+

### Performance
- **API Response Time**: < 500ms (95th percentile)
- **Error Rate**: < 10%
- **Concurrent Users**: 20 usuários simultâneos

### Security
- **Vulnerabilidades Críticas**: 0
- **Vulnerabilidades Altas**: < 5

## 🚀 Como Usar

### Para Desenvolvedores

1. **Criar Feature Branch:**
```bash
git checkout -b feature/nova-funcionalidade
git push -u origin feature/nova-funcionalidade
```

2. **Fazer Commits:**
- Cada commit trigger o workflow completo
- PRs triggam verificação rápida + análise

3. **Abrir Pull Request:**
- Comentário automático com status
- Análise de diff para arquivos críticos
- Relatório de segurança

### Para Releases

1. **Merge para develop:**
```bash
git checkout develop
git merge feature/nova-funcionalidade
git push origin develop
```
- Trigger: Deploy automático para staging
- Testes de performance
- Notificação Slack

2. **Merge para main:**
```bash
git checkout main
git merge develop
git push origin main
```
- Trigger: Deploy para produção (com aprovação)
- Build e push da imagem Docker
- Notificação de sucesso

## 📈 Monitoramento

### Artifacts Gerados
- **Test Results**: Relatórios de teste em XML/HTML
- **Coverage Reports**: Relatórios de cobertura
- **Security Reports**: Bandit e Safety reports
- **Performance Reports**: k6 load test results
- **Docker Images**: Imagens taggeadas no GHCR

### Notificações
- **Slack**: Falhas e sucessos de deploy
- **GitHub**: Comentários automáticos em PRs
- **Email**: Falhas de workflow (configuração GitHub)

## 🔍 Troubleshooting

### Falhas Comuns

1. **Lint Failures:**
```bash
# Corrigir formatação
black src/

# Corrigir lint issues
flake8 src/ --show-source
```

2. **Test Failures:**
```bash
# Executar testes localmente
pytest tests/ -v

# Com coverage
pytest tests/ --cov=src/
```

3. **Docker Build Failures:**
```bash
# Testar build local
docker build -t visionmoto-test .
docker run --rm -p 5001:5001 visionmoto-test
```

4. **Security Issues:**
```bash
# Verificar segurança local
bandit -r src/
safety check
```

### Logs e Debug

- **GitHub Actions**: Aba "Actions" no repositório
- **Artifacts**: Download de relatórios detalhados
- **Docker Logs**: `docker-compose logs -f`

## 🔄 Atualizações

### Versões das Actions
Mantenha as actions atualizadas:

```yaml
- uses: actions/checkout@v4        # Latest
- uses: actions/setup-python@v4    # Latest
- uses: docker/build-push-action@v5 # Latest
```

### Dependências Python
Atualize regularmente:

```bash
pip list --outdated
pip install --upgrade package_name
```

### Imagens Docker Base
Monitore atualizações:

```dockerfile
FROM python:3.9-slim  # Considere 3.11-slim
```

---

**Desenvolvido para o Challenge 2025 - VisionMoto v2.0**
