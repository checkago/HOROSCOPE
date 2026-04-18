#!/usr/bin/env sh
set -e

cd "$(dirname "$0")/.."

if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    . ./.env
    set +a
fi

if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "_" ]; then
    echo "Set DOMAIN in .env to your public hostname (not _)." >&2
    exit 1
fi

if [ -z "$CERTBOT_EMAIL" ]; then
    echo "Set CERTBOT_EMAIL in .env for Let's Encrypt." >&2
    exit 1
fi

docker compose up -d web nginx

docker compose exec -T nginx certbot certonly \
    --webroot \
    -w /var/www/certbot \
    -d "$DOMAIN" \
    --email "$CERTBOT_EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive

docker compose restart nginx
