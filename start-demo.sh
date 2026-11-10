#!/bin/sh
set -eu
: "${DJANGO_SECRET_KEY:?Defina uma chave exclusiva para a demonstracao}"
export DJANGO_SETTINGS_MODULE=config.demo_settings
mkdir -p demo-data
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py collectstatic --noinput
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 1 --worker-class gthread --threads 4 --timeout 30 --access-logfile - --error-logfile -
