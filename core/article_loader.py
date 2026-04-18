"""Чтение статей из каталога articles/ (тот же формат, что и у import_articles_md)."""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings


def parse_article_markdown(raw: str) -> tuple[str, str, str]:
    """Возвращает title, summary (лид до ---), body_markdown (весь файл)."""
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
    body_md = text
    return title, summary, body_md


def articles_dir() -> Path:
    return Path(settings.BASE_DIR) / "articles"


def load_article_stubs_from_disk() -> list[SimpleNamespace]:
    """Список статей для шаблона (как у queryset: slug, title, summary, sort_order)."""
    base = articles_dir()
    if not base.is_dir():
        return []
    out: list[SimpleNamespace] = []
    for path in sorted(base.glob("*.md")):
        m = re.match(r"^(\d+)_(.+)\.md$", path.name)
        if not m:
            continue
        try:
            raw = path.read_text(encoding="utf-8")
            title, summary, body_md = parse_article_markdown(raw)
        except ValueError:
            continue
        out.append(
            SimpleNamespace(
                slug=m.group(2),
                title=title,
                summary=summary,
                body_markdown=body_md,
                sort_order=int(m.group(1)),
            )
        )
    out.sort(key=lambda x: (x.sort_order, x.slug))
    return out


def get_article_from_disk(slug: str) -> SimpleNamespace | None:
    """Одна статья по slug или None."""
    for stub in load_article_stubs_from_disk():
        if stub.slug == slug:
            return stub
    return None
