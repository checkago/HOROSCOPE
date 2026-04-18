#!/bin/sh
set -e

if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "_" ]; then
    exit 0
fi

if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    exit 0
fi

export DOMAIN
envsubst '${DOMAIN}' < /etc/nginx/default-with-ssl.conf.template > /etc/nginx/conf.d/default.conf
