#!/bin/sh
set -e

mkdir -p /app/data /app/staticfiles

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "${SKIP_MD_IMPORT:-0}" != "1" ]; then
    python manage.py import_horoscope_md
fi

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-120}"
