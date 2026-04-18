#!/bin/sh
set -e

mkdir -p /app/data /app/staticfiles

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py import_horoscope_md

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
