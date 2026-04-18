#!/bin/sh
set -e

mkdir -p /app/data /app/staticfiles

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py import_horoscope_md || {
    echo "WARNING: import_horoscope_md failed; Gunicorn will start anyway." >&2
}

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
