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
- `DJANGO_BEHIND_HTTPS_PROXY` — `1`, только если перед приложением есть HTTPS-прокси с заголовком `X-Forwarded-Proto: https`; в типичном Docker (nginx → gunicorn по HTTP) оставьте `0`

## Docker-деплой (Ubuntu Server)

DNS: для домена **fizikazodiaka.ru** запись типа **A** должна указывать на IP сервера (сейчас в `.env` также разрешён прямой доступ по IP **37.48.251.135** для отладки).

1. Установить Docker и Compose plugin.
2. В корне репозитория уже есть `.env` (домен и настройки); при необходимости отредактируйте секрет и почту на сервере после `git pull`.

3. Запустить:

```bash
docker compose up -d --build
```

4. Проверить:

```bash
docker compose ps
docker compose logs -f web
```

Сервис будет доступен по `http://<server-ip>/` или по домену через Nginx на порту **80**.

**HTTPS:** в этом `docker-compose` Nginx только проксирует HTTP. Сертификат подключайте снаружи: TLS у провайдера / облачный прокси (например, с терминацией HTTPS перед сервером), либо отдельный reverse-proxy с Let’s Encrypt на хосте перед контейнером.

Если после `git pull` контейнеры не стартуют: смотрите логи `docker compose logs web` и `docker compose logs nginx`.

## Структура проекта

- `config/` — настройки Django и маршрутизация проекта
- `core/` — модели, API, импорт данных, основная логика
- `templates/core/` — HTML-шаблон главной страницы
- `static/core/` — стили и клиентский JS
- `nginx/default.conf` — прокси Nginx (HTTP) к Gunicorn и раздача `/static/`
- `docker-compose.yml`, `Dockerfile`, `entrypoint.sh` — контейнеризация и запуск

## GitHub

Репозиторий: [https://github.com/checkago/HOROSCOPE](https://github.com/checkago/HOROSCOPE)
