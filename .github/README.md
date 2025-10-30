# CI/CD - VisionMoto

Este diretório contém os workflows de automação GitHub Actions para o projeto VisionMoto.

## Workflows

- **ci-cd.yml** - Pipeline completo de CI/CD
  - Testes em Python 3.9, 3.10, 3.11
  - Build Docker multi-platform
  - Deploy automático para staging/produção
  - Análise de segurança
  - Testes de performance

- **pr-check.yml** - Verificação rápida para Pull Requests
  - Lint e testes
  - Análise de mudanças
  - Verificação de segurança

Para mais detalhes sobre CI/CD, consulte: `.github/workflows/`
