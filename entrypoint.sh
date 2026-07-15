#!/bin/sh
# entrypoint.sh — Se ejecuta cada vez que el contenedor arranca

set -e  # Si algo falla, detener todo

echo "▶ Corriendo migraciones..."
python manage.py migrate --noinput

echo "▶ Colectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "▶ Iniciando servidor..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -