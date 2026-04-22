# Физика знаков и куспидов

Интерактивный Django-проект с физико-химической интерпретацией:
- характеристик знаков и куспидов;
- отношений между парами (знак/куспид);
- расширенного объяснения взаимодействий в научно-образном стиле.

## Возможности

- Пошаговый выбор в UI:
  - режим: характеристика или отношения;
  - профиль или пара профилей.
- Хранение данных в Markdown-файлах (`01_...md` — `48_...md`) и импорт в БД.
- API для фронтенда:
  - `/api/options/`
  - `/api/relationship-targets/`
  - `/api/result/`
- SEO-мета, Open Graph, Twitter Card и JSON-LD.

## Стек

- Python 3.12
- Django 5
- Django REST Framework
- SQLite
- Bootstrap 5 + vanilla JS
- Gunicorn
- Docker + Nginx

## Локальный запуск (Windows/Linux/macOS)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py import_horoscope_md
python manage.py runserver 0.0.0.0:8000
```

Открыть: `http://127.0.0.1:8000`

## Переменные окружения

- `DJANGO_SECRET_KEY` — секретный ключ Django
- `DJANGO_DEBUG` — `True/False`
- `DJANGO_ALLOWED_HOSTS` — список хостов через запятую
- `DJANGO_CSRF_TRUSTED_ORIGINS` — trusted origins через запятую
- `DJANGO_SQLITE_PATH` — путь к SQLite-файлу
- `PUBLIC_SITE_URL` — базовый URL сайта (канонические ссылки в SEO)
- `SITE_DOMAIN` — имя хоста для Caddy (Let's Encrypt, порты 80/443)

## Docker-деплой (Ubuntu Server)

DNS: для домена **fizikazodiaka.ru** запись типа **A** должна указывать на IP сервера (см. также `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` в `.env.example`).

1. Установить Docker и Compose plugin.
2. Скопировать переменные окружения: `cp .env.example .env` и задать реальный `DJANGO_SECRET_KEY` и при необходимости домен (`SITE_DOMAIN`, `PUBLIC_SITE_URL`). Файл `.env` в git не коммитится.
3. Запуск в проде (Gunicorn → Nginx → Caddy, порты **80/443**):

```bash
docker compose up -d --build
```

4. Локально без занятия портов 80/443 (только Nginx на **8080**, без Caddy):

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up --build
```

5. Проверка:

```bash
docker compose ps
docker compose logs -f web
```

**HTTPS:** Caddy в основном `docker-compose.yml` получает сертификат Let’s Encrypt для `{$SITE_DOMAIN}` и проксирует на внутренний Nginx. Внутри сети compose Nginx отдаёт статику и проксирует динамику на Gunicorn.

При повторных деплоях с уже заполненной БД в volume можно выставить `SKIP_MD_IMPORT=1` в `.env`, чтобы не перезапускать полный импорт MD при каждом старте контейнера (см. `entrypoint.sh`).

Если контейнеры не стартуют: `docker compose logs web`, `docker compose logs nginx`, `docker compose logs caddy`.

## Структура проекта

- `config/` — настройки Django и маршрутизация проекта
- `core/` — модели, API, импорт данных, основная логика
- `templates/core/` — HTML-шаблон главной страницы
- `static/core/` — стили и клиентский JS
- `nginx/default.conf` — внутренний прокси Nginx (HTTP) к Gunicorn и `/static/`
- `caddy/Caddyfile` — Caddy: TLS и прокси на Nginx
- `docker-compose.yml`, `docker-compose.local.yml`, `Dockerfile`, `entrypoint.sh`, `.dockerignore` — контейнеризация и запуск

## GitHub

Репозиторий: [https://github.com/checkago/HOROSCOPE](https://github.com/checkago/HOROSCOPE)
