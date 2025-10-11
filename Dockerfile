# Dockerfile para VisionMoto - Sistema Integrado
FROM python:3.9-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY . .

# Cria diretório para banco de dados
RUN mkdir -p /app/data

# Expõe portas
EXPOSE 5000 5001

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV DATABASE_PATH=/app/data/visionmoto_integration.db

# Comando padrão - executa API de integração
CMD ["python", "src/backend/integration_api.py"]
