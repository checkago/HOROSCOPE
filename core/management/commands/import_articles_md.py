from __future__ import annotations

from pathlib import Path

import re

from django.conf import settings
from django.core.management.base import BaseCommand

from core.article_loader import parse_article_markdown
from core.models import Article

# Минимальная длина текста статьи (символы UTF-8) для выдачи и SEO.
MIN_SEO_CHARS = 6000


class Command(BaseCommand):
    help = "Импорт статей из каталога articles (*.md, имя: NN_slug.md)."

    def handle(self, *args, **options):
        base = Path(settings.BASE_DIR) / "articles"
        if not base.is_dir():
            self.stderr.write(self.style.ERROR(f"нет каталога {base}"))
            return
        paths = sorted(base.glob("*.md"))
        if not paths:
            self.stderr.write(self.style.WARNING("нет .md файлов"))
            return
        created = 0
        for path in paths:
            m = re.match(r"^(\d+)_(.+)\.md$", path.name)
            if not m:
                self.stderr.write(self.style.WARNING(f"пропуск (имя): {path.name}"))
                continue
            sort_order = int(m.group(1))
            slug = m.group(2)
            raw = path.read_text(encoding="utf-8")
            title, summary, body_md = parse_article_markdown(raw)
            if len(body_md) < MIN_SEO_CHARS:
                self.stdout.write(
                    self.style.WARNING(
                        f"{path.name}: markdown короче {MIN_SEO_CHARS} символов ({len(body_md)})"
                    )
                )
            Article.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "summary": summary,
                    "body_markdown": body_md,
                    "sort_order": sort_order,
                },
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f"статей обработано: {created}"))
