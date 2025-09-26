# 🛠️ Scripts - VisionMoto

Esta pasta contém scripts utilitários para o sistema VisionMoto.

## 📁 Arquivos

### `generate_test_data.py`
**Gerador de dados de teste**
- Gera dados sintéticos para o dashboard
- Simula detecções de motos
- Cria dados de sensores IoT
- Útil para testes e demonstrações

```bash
python scripts/generate_test_data.py
```

**Funcionalidades:**
- ✅ Gera detecções aleatórias de motos
- ✅ Simula dados de sensores IoT
- ✅ Envia dados via API REST
- ✅ Executa por 30 segundos por padrão

## 🚀 Uso

### Executar da raiz do projeto:
```bash
python visionmoto.py data
```

### Executar diretamente:
```bash
python scripts/generate_test_data.py
```

## ⚙️ Configuração

O script requer:
- Backend Flask rodando (porta 5000)
- Banco de dados inicializado
- APIs `/detections` e `/iot/sensor` funcionais

## 📊 Dados Gerados

- **Detecções**: Frame, classe, confiança, bbox, área
- **Sensores IoT**: ID, localização, bateria, sinal
- **Métricas**: FPS, taxa de detecção, motos únicas
