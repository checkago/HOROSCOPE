from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Article

# Минимальная длина текста статьи (символы UTF-8) для выдачи и SEO.
MIN_SEO_CHARS = 6000


def _parse_article_file(raw: str) -> tuple[str, str, str]:
    text = raw.lstrip("\ufeff").strip()
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if not m:
        raise ValueError("ожидается заголовок первой строкой вида # Заголовок")
    title = m.group(1).strip()
    after_title = text[m.end() :].lstrip("\n")
    sep = re.split(r"\n-{3,}\s*\n", after_title, maxsplit=1)
    if len(sep) == 2:
        summary = sep[0].strip()
        body = sep[1].strip()
    else:
        lines = after_title.splitlines()
        summary_lines: list[str] = []
        idx = 0
        for i, line in enumerate(lines):
            s = line.strip()
            if not s:
                if summary_lines:
                    idx = i + 1
                    break
                continue
            if s.startswith("#"):
                break
            summary_lines.append(line)
            idx = i + 1
        summary = "\n".join(summary_lines).strip()
        body = "\n".join(lines[idx:]).strip()
    if not summary:
        summary = (body or text)[:280].rsplit(" ", 1)[0] + "…" if len(body or text) > 280 else (body or text)
    # В БД и на странице — весь файл: лид до `---` даёт контекст и длину для SEO; после `---` — основной текст.
    body_md = text
    return title, summary, body_md


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
            title, summary, body_md = _parse_article_file(raw)
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
