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
- `DOMAIN`, `CERTBOT_EMAIL`, `CERTBOT_RENEW_SLEEP_SEC` — домен и Let's Encrypt для Docker Nginx

## Docker-деплой (Ubuntu Server)

1. Установить Docker и Compose plugin.
2. Создать `.env` из шаблона и задать секрет и почту (файл `.env` в Git не хранится):

```bash
cp .env.example .env
nano .env   # или другой редактор
```

3. Запустить:

```bash
docker compose up -d --build
```

4. Проверить:

```bash
docker compose ps
docker compose logs -f web
```

Сервис будет доступен по `http://<server-ip>/` через Nginx.

## Структура проекта

- `config/` — настройки Django и маршрутизация проекта
- `core/` — модели, API, импорт данных, основная логика
- `templates/core/` — HTML-шаблон главной страницы
- `static/core/` — стили и клиентский JS
- `nginx/` — образ Nginx с шаблонами конфигурации и поддержкой Let's Encrypt
- `docker-compose.yml`, `Dockerfile`, `entrypoint.sh` — контейнеризация и запуск

## GitHub

Репозиторий: [https://github.com/checkago/HOROSCOPE](https://github.com/checkago/HOROSCOPE)
