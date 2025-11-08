# Dockerfile para VisionMoto - Sistema Integrado
FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root para segurança
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    mkdir -p /app /app/data && \
    chown -R appuser:appuser /app

# Define diretório de trabalho
WORKDIR /app

# Copia requirements como root
COPY --chown=appuser:appuser requirements.txt .

# Muda para usuário não-root
USER appuser

# Instala dependências Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Adiciona binários do pip ao PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copia código fonte
COPY --chown=appuser:appuser . .

# Expõe portas
EXPOSE 5000 5001

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV DATABASE_PATH=/app/data/visionmoto_integration.db
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/health', timeout=5)" || exit 1

# Comando padrão - executa API de integração com gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "src.backend.app:app"]
