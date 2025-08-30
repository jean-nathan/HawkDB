# =============================================================================
# HawkDB - Dockerfile Simples e Performático
# =============================================================================

FROM python:3.11-slim

# Metadados
LABEL maintainer="HawkDB Team"
LABEL description="HawkDB - Sistema de Consulta com Interface Gráfica"
LABEL version="2.0"

# Otimizações de ambiente
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências mínimas do sistema
RUN apt-get update && apt-get install -y \
    # Para Tkinter
    python3-tk \
    # Para X11 forwarding
    libx11-6 \
    libxext6 \
    libxrender1 \
    # Fonts básicas
    fonts-dejavu-core \
    # Limpeza automática
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get clean

# Cria diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY hawkdb.py .

# Cria diretórios para dados
RUN mkdir -p /app/exports /app/data

# Comando para executar o HawkDB
CMD ["python", "hawkdb.py"]
