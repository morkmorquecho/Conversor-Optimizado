# ─── Stage 1: instalar dependencias ─────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Exportar requirements desde Pipfile y instalar
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ─── Stage 2: imagen final ────────────────────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

# Copiar paquetes instalados
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código del proyecto
COPY . .

# Copiar y dar permisos al entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Usuario sin privilegios (seguridad)
RUN useradd --no-create-home --shell /bin/false django \
    && mkdir -p /app/staticfiles /app/logs \
    && chown -R django:django /app /entrypoint.sh

USER django

EXPOSE 8000

# Railway inyecta $PORT automáticamente (normalmente 8000)
CMD ["/entrypoint.sh"]