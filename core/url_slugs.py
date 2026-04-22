"""Человекочитаемые slug-профилей из имени файла (латиница для SEO и URL)."""

from __future__ import annotations

import re
from pathlib import Path

from .models import Profile

# Упрощённая транслитерация кириллицы (имена файлов знаков/куспидов).
_RU_TO_LAT = str.maketrans(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
        "А": "a",
        "Б": "b",
        "В": "v",
        "Г": "g",
        "Д": "d",
        "Е": "e",
        "Ё": "e",
        "Ж": "zh",
        "З": "z",
        "И": "i",
        "Й": "y",
        "К": "k",
        "Л": "l",
        "М": "m",
        "Н": "n",
        "О": "o",
        "П": "p",
        "Р": "r",
        "С": "s",
        "Т": "t",
        "У": "u",
        "Ф": "f",
        "Х": "h",
        "Ц": "ts",
        "Ч": "ch",
        "Ш": "sh",
        "Щ": "sch",
        "Ъ": "",
        "Ы": "y",
        "Ь": "",
        "Э": "e",
        "Ю": "yu",
        "Я": "ya",
    }
)


def _ascii_slug_tail(tail: str) -> str:
    s = tail.translate(_RU_TO_LAT)
    s = s.lower()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def profile_public_slug(profile: Profile) -> str:
    """Стабильный slug из source_file: `09_Лев_Мужчина.md` -> `lev-muzhchina`."""
    stem = Path(profile.source_file or "").stem
    m = re.match(r"^\d{2}_(.+)$", stem)
    tail = m.group(1) if m else stem
    tail = tail.replace("_", "-")
    return _ascii_slug_tail(tail)


def get_profile_by_public_slug(slug: str) -> Profile | None:
    """Поиск профиля по публичному slug (без доп. полей в БД)."""
    want = (slug or "").strip().lower()
    if not want:
        return None
    for p in Profile.objects.all().iterator():
        if profile_public_slug(p) == want:
            return p
    return None
