from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand

from core.horoscope_loader import run_md_import


class Command(BaseCommand):
    help = "Импортирует характеристики и отношения из MD-файлов в БД."

    def handle(self, *args, **options):
        n_profiles, n_rels = run_md_import(Path.cwd())
        self.stdout.write(
            self.style.SUCCESS(
                f"Импорт завершен: {n_profiles} профилей, {n_rels} связей."
            )
        )
