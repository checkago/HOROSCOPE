from __future__ import annotations

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from core.daily_forecast import ensure_daily_forecast
from core.models import Profile


class Command(BaseCommand):
    help = "Генерация ежедневного прогноза для всех профилей (или одного профиля)."

    def add_arguments(self, parser):
        parser.add_argument("--date", type=str, default="", help="Дата в формате YYYY-MM-DD")
        parser.add_argument("--profile-id", type=int, default=0, help="ID профиля (опционально)")

    def handle(self, *args, **options):
        raw_date = (options.get("date") or "").strip()
        profile_id = int(options.get("profile_id") or 0)
        if raw_date:
            try:
                target_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError as exc:
                raise CommandError("Неверный формат --date, ожидается YYYY-MM-DD") from exc
        else:
            target_date = datetime.now().date()

        qs = Profile.objects.all().order_by("code")
        if profile_id:
            qs = qs.filter(pk=profile_id)
        profiles = list(qs)
        if not profiles:
            raise CommandError("Профили не найдены")

        created = 0
        for profile in profiles:
            ensure_daily_forecast(profile, target_date)
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Ежедневные прогнозы сгенерированы: {created} (дата: {target_date.isoformat()})"
            )
        )
