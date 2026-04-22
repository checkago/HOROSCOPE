FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN groupadd --system appuser \
    && useradd --system --gid appuser --no-create-home appuser \
    && mkdir -p /app/data /app/staticfiles \
    && chown -R appuser:appuser /app \
    && sed -i 's/\r$//' /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Старт под root: entrypoint.sh выставит права на тома и перейдёт на appuser (см. runuser).
USER root

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=50s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=4)" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
