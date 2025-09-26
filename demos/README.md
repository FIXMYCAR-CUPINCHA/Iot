# 🎯 Demos - VisionMoto

Esta pasta contém as demonstrações principais do sistema VisionMoto.

## 📁 Arquivos

### `run_complete_system.py`
**Demonstração completa integrada**
- Executa sistema completo com IoT + Visão Computacional
- Inicia backend Flask automaticamente
- Simula dispositivos IoT
- Processa vídeo com detecção de motos
- **Recomendado para apresentações**

```bash
python demos/run_complete_system.py
```

### `demo_final.py`
**Demonstração final do projeto**
- Versão otimizada para apresentação final
- Interface mais polida
- Métricas detalhadas
- Relatórios automáticos

```bash
python demos/demo_final.py
```

### `main.py`
**Detecção de visão computacional apenas**
- Executa apenas o módulo de detecção YOLOv8
- Sem IoT ou backend
- Ideal para testes de performance de visão

```bash
python demos/main.py
```

## 🚀 Execução Rápida

Para executar a demonstração completa:
```bash
# Da raiz do projeto
python visionmoto.py demo
```

## 📊 Dashboard

Após executar qualquer demo com backend, acesse:
- **URL**: http://localhost:5000
- **Dashboard**: Interface web em tempo real
- **Métricas**: Dados de IoT e detecções
