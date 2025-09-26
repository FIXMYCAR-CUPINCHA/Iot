# 🧪 Tests - VisionMoto

Esta pasta contém os testes do sistema VisionMoto.

## 📁 Arquivos

### `test_system.py`
**Teste completo do sistema**
- Testa integração entre componentes
- Verifica detecção de visão computacional
- Valida simulação IoT
- Testa persistência de dados

```bash
python tests/test_system.py
```

### `test_backend.py`
**Teste do backend e APIs**
- Testa todas as rotas da API
- Verifica banco de dados
- Testa comunicação em tempo real
- Valida métricas

```bash
python tests/test_backend.py
```

## 🚀 Execução

### Executar todos os testes:
```bash
python visionmoto.py tests
```

### Executar testes individuais:
```bash
python tests/test_system.py
python tests/test_backend.py
```

## ✅ Cobertura de Testes

### Sistema Completo:
- ✅ Detecção YOLOv8
- ✅ Simulação IoT
- ✅ Banco de dados SQLite
- ✅ Integração de componentes

### Backend/API:
- ✅ Rotas REST
- ✅ Socket.IO
- ✅ Persistência
- ✅ Métricas

## 📊 Relatórios

Os testes geram:
- Status de cada componente
- Métricas de performance
- Logs detalhados
- Recomendações de melhoria
