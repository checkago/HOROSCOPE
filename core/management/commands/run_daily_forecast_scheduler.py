from __future__ import annotations

import time
from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Бесконечный планировщик: генерирует ежедневный прогноз каждый день в 00:00 локального времени."

    def add_arguments(self, parser):
        parser.add_argument(
            "--poll-seconds",
            type=int,
            default=30,
            help="Интервал проверки времени в секундах (по умолчанию: 30).",
        )

    def handle(self, *args, **options):
        poll_seconds = max(5, int(options.get("poll_seconds") or 30))
        self.stdout.write(self.style.SUCCESS("Daily forecast scheduler started"))

        last_processed_date = None

        while True:
            now_local = timezone.localtime()
            today = now_local.date()

            # Генерируем один раз в сутки, как только наступит 00:00.
            if now_local.hour == 0 and today != last_processed_date:
                call_command("generate_daily_forecast", date=today.isoformat())
                last_processed_date = today

            # Защита от пропуска старта контейнера после полуночи: если за сегодня ещё не генерировали — добиваем.
            if today != last_processed_date:
                call_command("generate_daily_forecast", date=today.isoformat())
                last_processed_date = today

            next_tick = timezone.localtime() + timedelta(seconds=poll_seconds)
            sleep_for = max(1.0, (next_tick - timezone.localtime()).total_seconds())
            time.sleep(sleep_for)
