# VisionMoto v2.0 - Sistema Integrado (4º Sprint)

**Challenge 2025 - 2º Semestre - Disruptive Architectures: IoT, IoB & Generative AI**

Sistema completo de detecção e gerenciamento de motos com integração multi-disciplinar desenvolvido para o desafio da Mottu.

## 🎯 Visão Geral do 4º Sprint

O VisionMoto v2.0 representa a evolução completa do sistema desenvolvido no 3º Sprint, agora com **integração total** entre todas as disciplinas do curso:

- **✅ Sistema Base (3º Sprint)**: Visão computacional + IoT + Backend + Dashboard
- **🆕 Integração Mobile App**: APIs REST para aplicativos móveis
- **🆕 Integração Java**: Endpoints compatíveis com Spring Boot
- **🆕 Integração .NET**: APIs no formato ASP.NET Core
- **🆕 Banco de Dados Expandido**: Suporte multi-plataforma
- **🆕 DevOps Completo**: Docker, CI/CD, monitoramento

## 🚀 Execução Rápida

### Sistema Integrado Completo
```bash
python start_integration.py
```

### Com Docker (Recomendado para Produção)
```bash
docker-compose up -d
```

### Sistema Original (3º Sprint)
```bash
python visionmoto.py demo
```

## 📋 Requisitos do 4º Sprint - ✅ ATENDIDOS

### ✅ Fluxo Completo de Dados
- **Captura**: IoT sensors + Visão computacional (YOLO)
- **Processamento**: Backend Python com Flask
- **Armazenamento**: SQLite expandido + PostgreSQL (Docker)
- **Visualização**: Dashboard web em tempo real

### ✅ Dashboard/Interface Final
- **Localização das motos**: Grid visual + mapa interativo
- **Status em tempo real**: Disponível, Em Uso, Manutenção
- **Alertas**: Sistema de notificações em tempo real
- **Métricas**: Bateria, localização, histórico de uso

### ✅ Integração Multi-Disciplinar
- **Mobile App**: APIs REST completas com autenticação JWT
- **Java/Spring Boot**: Endpoints compatíveis com padrões Java
- **ASP.NET Core**: APIs no formato .NET com DTOs apropriados
- **Banco de Dados**: Schema expandido para suporte multi-plataforma
- **DevOps**: Docker, CI/CD, monitoramento com Prometheus/Grafana

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   Java/Spring   │    │   .NET Core     │
│   (React/Flutter)│    │   Boot App      │    │   Application   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Integration API       │
                    │   (Flask + SQLite)      │
                    │   Port: 5001           │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Vision System         │
                    │   (YOLO + OpenCV)       │
                    │   Port: 5000           │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   IoT Devices           │
                    │   (MQTT + HTTP)         │
                    └─────────────────────────┘
```

## 🌐 Endpoints de Integração

### 📱 Mobile App (`/api/mobile/`)
```
POST /api/mobile/auth/login          # Autenticação
GET  /api/mobile/motos               # Lista motos
POST /api/mobile/motos/{id}/reservar # Reserva moto
```

### ☕ Java/Spring Boot (`/api/java/`)
```
GET  /api/java/motos/status          # Status das motos
GET  /api/java/alertas               # Lista alertas
POST /api/java/alertas               # Cria alerta
```

### 🔷 .NET Core (`/api/dotnet/`)
```
GET  /api/dotnet/Dashboard/GetMotorcycleData    # Dados das motos
POST /api/dotnet/Reports/GenerateUsageReport   # Relatório de uso
```

### 🗄️ Database (`/api/database/`)
```
POST /api/database/backup            # Backup do banco
GET  /api/database/analytics         # Analytics
```

### 📡 IoT (`/api/iot/`)
```
GET  /api/iot/devices               # Lista dispositivos
POST /api/iot/devices/{id}/data     # Dados do dispositivo
```

## 🛠️ Tecnologias Utilizadas

### Backend & APIs
- **Python 3.9+**: Linguagem principal
- **Flask**: Framework web + APIs REST
- **Flask-CORS**: Suporte CORS para integração
- **JWT**: Autenticação para mobile
- **SQLite**: Banco principal (desenvolvimento)
- **PostgreSQL**: Banco produção (Docker)

### Visão Computacional & IoT
- **YOLOv8**: Detecção de objetos
- **OpenCV**: Processamento de imagem
- **MQTT**: Comunicação IoT
- **Socket.IO**: Tempo real

### DevOps & Infraestrutura
- **Docker**: Containerização
- **Docker Compose**: Orquestração
- **GitHub Actions**: CI/CD
- **Nginx**: Load balancer
- **Prometheus**: Monitoramento
- **Grafana**: Dashboards

## 📊 Demonstração dos Casos de Uso

### 1. 🏍️ Detecção em Tempo Real
- Sistema detecta motos via câmera
- Identifica localização no pátio
- Atualiza status no dashboard
- Envia dados para apps integrados

### 2. 📱 Reserva via Mobile App
- Usuário faz login no app
- Lista motos disponíveis
- Reserva moto específica
- Sistema atualiza status em tempo real

### 3. ☕ Monitoramento Java
- Aplicação Java consulta status
- Recebe dados em formato compatível
- Cria alertas quando necessário
- Integra com sistemas empresariais

### 4. 🔷 Relatórios .NET
- Sistema .NET gera relatórios
- Consulta dados de uso histórico
- Exporta métricas de performance
- Integra com dashboards corporativos

### 5. 🚨 Alertas Automáticos
- Moto desaparece do pátio
- Sistema gera alerta automático
- Notifica todas as aplicações
- Registra evento no histórico

## 🐳 Deploy com Docker

### Desenvolvimento
```bash
# Inicia todos os serviços
docker-compose up -d

# Visualiza logs
docker-compose logs -f

# Para todos os serviços
docker-compose down
```

### Produção
```bash
# Build e deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitoramento
docker-compose exec visionmoto-api python health_check.py
```

## 📈 Monitoramento e Métricas

### Prometheus Metrics
- **API Response Time**: Latência das APIs
- **Detection Rate**: Taxa de detecção por segundo
- **IoT Device Status**: Status dos dispositivos
- **Database Performance**: Performance do banco

### Grafana Dashboards
- **Sistema Overview**: Métricas gerais
- **Detecções**: Análise de detecções
- **IoT Devices**: Status dos dispositivos
- **API Performance**: Performance das APIs

## 🧪 Testes e Qualidade

### Testes Automatizados
```bash
# Executa todos os testes
pytest tests/ -v --cov=src/

# Testes de integração
pytest tests/integration/ -v

# Testes de API
pytest tests/api/ -v
```

### Qualidade de Código
```bash
# Linting
flake8 src/

# Formatação
black src/

# Type checking
mypy src/
```

## 📋 Checklist do 4º Sprint

### ✅ Funcionalidade Técnica (60 pts)
- [x] Fluxo completo de dados IoT → Visualização
- [x] Dashboard com localização das motos
- [x] Sistema de alertas em tempo real
- [x] APIs funcionais para todas as integrações

### ✅ Integração Multi-Disciplinar (20 pts)
- [x] Mobile App: APIs REST + JWT
- [x] Java: Endpoints Spring Boot compatíveis
- [x] .NET: APIs ASP.NET Core format
- [x] Database: Schema expandido
- [x] DevOps: Docker + CI/CD

### ✅ Apresentação (10 pts)
- [x] Sistema funcionando end-to-end
- [x] Demonstração de todas as integrações
- [x] Documentação completa
- [x] Vídeo explicativo preparado

### ✅ Organização (10 pts)
- [x] Código bem estruturado
- [x] Documentação detalhada
- [x] README atualizado
- [x] Instruções de instalação

## 🎥 Demonstração em Vídeo

O vídeo de demonstração incluirá:

1. **Visão Geral**: Apresentação do sistema integrado
2. **Detecção em Tempo Real**: Sistema funcionando com câmera
3. **Dashboard**: Interface com mapa das motos
4. **Mobile Integration**: App consumindo APIs
5. **Java Integration**: Sistema Java recebendo dados
6. **.NET Integration**: Aplicação .NET gerando relatórios
7. **DevOps**: Deploy com Docker
8. **Monitoramento**: Dashboards Grafana

## 👥 Equipe

**Thomaz Oliveira Vilas Boas Bartol** - RM555323  
**Vinicius Souza Carvalho** - RM556089  
**Gabriel Duarte** - RM556972  

**4º Sprint - Disruptive Architectures: IoT, IoB & Generative AI**

---

## 🚀 Próximos Passos

### Melhorias Futuras
- **Machine Learning**: Predição de demanda
- **Blockchain**: Rastreabilidade de transações
- **5G/Edge Computing**: Processamento distribuído
- **AR/VR**: Interface imersiva

### Escalabilidade
- **Microserviços**: Arquitetura distribuída
- **Kubernetes**: Orquestração avançada
- **Multi-cloud**: Deploy em múltiplas clouds
- **Global CDN**: Distribuição mundial

---

**Sistema VisionMoto v2.0 - Integração Completa para o Challenge 2025**

*Desenvolvido com foco em integração multi-disciplinar e escalabilidade empresarial.*
