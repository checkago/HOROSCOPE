#!/bin/sh
set -e

mkdir -p /app/data /app/staticfiles

# Тома Docker часто с root-владельцем; в static_data после старых деплоев лежат чужие UID —
# collectstatic не может удалить такие файлы. Под root чистим только staticfiles, затем chown.
if [ "$(id -u)" = "0" ]; then
    find /app/staticfiles -mindepth 1 -delete 2>/dev/null || true
    chown -R appuser:appuser /app/data /app/staticfiles
    exec runuser -u appuser -g appuser -- "$0" "$@"
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "${SKIP_MD_IMPORT:-0}" != "1" ]; then
    python manage.py import_horoscope_md
fi

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-120}"
