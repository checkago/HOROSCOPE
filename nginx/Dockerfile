FROM nginx:1.27-alpine

RUN apk add --no-cache certbot openssl

COPY templates/default.conf.template /etc/nginx/templates/default.conf.template
COPY default-with-ssl.conf.template /etc/nginx/default-with-ssl.conf.template
COPY docker-entrypoint.d/25-add-ssl-if-present.sh /docker-entrypoint.d/25-add-ssl-if-present.sh
COPY docker-entrypoint.d/99-certbot-renew.sh /docker-entrypoint.d/99-certbot-renew.sh

RUN sed -i 's/\r$//' /docker-entrypoint.d/25-add-ssl-if-present.sh \
    /docker-entrypoint.d/99-certbot-renew.sh \
    && chmod +x /docker-entrypoint.d/25-add-ssl-if-present.sh \
    /docker-entrypoint.d/99-certbot-renew.sh
