from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand

from core.horoscope_loader import run_json_import


class Command(BaseCommand):
    help = (
        "Импортирует профили из JSON (корень проекта: [0-9][0-9]_*.json). "
        "Не смешивать с MD-импортом в одной папке: перед загрузкой удаляются все профили и связи.\n\n"
        "Схема одного файла:\n"
        '  {"name": "Овен", "gender_ru": "Мужчина", "code": "01", '
        '"characteristic_markdown": "# Овен — Мужчина\\n\\n...", '
        '"relationships": [\n'
        '    {"target_header": "Женщиной-Овен", "interaction_type": "...", '
        '"bound_state": "...", "why": "...", "quantum_dynamics": "", '
        '"intimacy": "...", "synthesis": "...", "vulnerabilities": "...", '
        '"result_line": "...", "human_coda": "..."}\n'
        "  ]}\n"
        "Поле target_header — как в MD после «### С » (без префикса «С »)."
    )

    def handle(self, *args, **options):
        n_profiles, n_rels = run_json_import(Path.cwd())
        self.stdout.write(
            self.style.SUCCESS(
                f"Импорт JSON завершён: {n_profiles} профилей, {n_rels} связей."
            )
        )
