# 📈 Reports - VisionMoto

Esta pasta contém relatórios e análises do sistema VisionMoto.

## 📁 Arquivos

### `performance_report.py`
**Gerador de relatório de performance**
- Analisa métricas do sistema
- Gera relatório detalhado em JSON
- Avalia conformidade com requisitos
- Calcula pontuação final

```bash
python reports/performance_report.py
```

### `performance_report.json`
**Relatório de performance atual**
- Métricas de FPS e detecções
- Status dos componentes
- Pontuação por critério
- Recomendações de melhoria

## 🚀 Uso

### Gerar novo relatório:
```bash
python visionmoto.py report
```

### Executar diretamente:
```bash
python reports/performance_report.py
```

## 📊 Métricas Analisadas

### Performance:
- ✅ FPS médio do sistema
- ✅ Taxa de detecção
- ✅ Latência das APIs
- ✅ Throughput do backend

### Funcionalidades:
- ✅ Detecção de visão computacional
- ✅ Simulação IoT
- ✅ Dashboard em tempo real
- ✅ Persistência de dados

### Conformidade 3ª Sprint:
- ✅ Comunicação sensores/backend (30 pts)
- ✅ Dashboard/output visual (30 pts)
- ✅ Persistência de dados (20 pts)
- ✅ Organização/documentação (20 pts)

## 📋 Formato do Relatório

```json
{
  "timestamp": "2025-09-26T20:44:00",
  "performance_metrics": {
    "fps": 25.5,
    "total_detections": 150,
    "unique_motos": 12
  },
  "summary": {
    "total_score": 100,
    "overall_grade": "A (Excelente)"
  }
}
```
