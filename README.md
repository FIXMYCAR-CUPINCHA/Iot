# VisionMoto - Challenge 2025

Sistema integrado de detecção de motos com IoT e APIs multi-disciplinares.

## Execução Rápida

### Sistema Completo
```bash
python start_integration.py
```

### Demonstração
```bash
python visionmoto.py demo
```

### API de Integração
```bash
python visionmoto.py backend
```

## APIs Disponíveis

- **Mobile App**: `/api/mobile/*`
- **Java/Spring**: `/api/java/*`
- **ASP.NET**: `/api/dotnet/*`
- **Database**: `/api/database/*`
- **IoT**: `/api/iot/*`

## Tecnologias

- **Backend**: Python Flask + SQLite
- **Visão**: OpenCV + YOLO
- **IoT**: MQTT + HTTP/REST
- **DevOps**: Docker + GitHub Actions

## Estrutura

```
VisionMoto/
├── src/backend/integration_api.py    # API principal
├── start_integration.py              # Sistema completo
├── visionmoto.py                     # Script principal
├── demos/demo_final.py               # Demonstração
├── tests/                            # Testes
├── integration/                      # Docs integração
└── .github/workflows/                # CI/CD
```

## Equipe

- **Vinicius Souza Carvalho** - RM556089
- **Thomaz Oliveira Vilas Boas Bartol** - RM555323
- **Gabriel Duarte** - RM556972

**4º Sprint - Disruptive Architectures: IoT, IoB & Generative AI**
