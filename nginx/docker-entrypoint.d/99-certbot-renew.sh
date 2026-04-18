#!/bin/sh
set -e

if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "_" ]; then
    exit 0
fi

if [ -z "$CERTBOT_EMAIL" ]; then
    exit 0
fi

INTERVAL="${CERTBOT_RENEW_SLEEP_SEC:-7689600}"

(
    sleep 45
    while true; do
        certbot renew \
            --webroot \
            -w /var/www/certbot \
            --non-interactive \
            --quiet \
            --deploy-hook "nginx -s reload" || true
        sleep "$INTERVAL"
    done
) &
