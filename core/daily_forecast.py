from __future__ import annotations

import hashlib
import json
import os
from datetime import date
from math import sin, pi
from urllib import error as url_error
from urllib import request as url_request

from .models import DailyForecast, Profile

ENERGY_COMMENTS = (
    "Контур дня тянет к спокойной сборке: лучше сначала выстроить базу, потом ускоряться.",
    "Поле дня даёт нормальную рабочую динамику: результат приходит через последовательность, а не рывок.",
    "Фон слегка турбулентный: важнее фильтровать входящие сигналы и не отвечать на каждый импульс.",
)

FOCUS_COMMENTS = (
    "Для когнитивной нагрузки подходит формат «одна сложная задача + короткие блоки поддержки».",
    "Сильнее всего работает режим глубокой концентрации с чётким временем старта и финиша.",
    "Продуктивность выше в рутине и систематизации, чем в резких разворотах и новых гипотезах.",
)

SOCIAL_COMMENTS = (
    "В контакте выигрывает тихая точность: меньше оценок, больше проверяемых формулировок.",
    "Коммуникация лучше идёт через вопросы и согласование границ, чем через попытку «додавить смысл».",
    "Социальный канал чувствителен к тону: сперва стабилизация, затем обсуждение спорного.",
)

RISK_COMMENTS = (
    "Риск дня — перегрев от многозадачности и избыточной реактивности.",
    "Уязвимость дня — конфликт интерпретаций: одинаковые факты будут читаться по-разному.",
    "Слабая точка дня — вечерний спад ресурса, где растёт вероятность резких ответов.",
)

PRACTICE_COMMENTS = (
    "Практика: перед важным разговором сделайте паузу 5-7 минут и зафиксируйте цель одной фразой.",
    "Практика: выберите 1 главный критерий дня и сверяйтесь с ним каждые 3-4 часа.",
    "Практика: вечером закройте день коротким протоколом «что сработало / что шумело / что перенести».",
)

PATTERN_COMMENTS = (
    "Паттерн дня: лучше работает стратегия «меньше переключений, больше глубины».",
    "Паттерн дня: выигрыш приходит через точную последовательность шагов, а не через скорость старта.",
    "Паттерн дня: ключевой ресурс — чистый канал коммуникации, а не объём аргументов.",
    "Паттерн дня: максимальная отдача в задачах, где есть ясная структура и понятный критерий завершения.",
)

HUMAN_CODA = (
    "По-человечески: сегодня лучшее решение — держать ровный темп и проверять качество сигнала перед каждым ускорением.",
    "По-человечески: выиграет тот, кто сохранит ясные рамки в общении и не отдаст ресурс импульсивным реакциям.",
    "По-человечески: результат приходит через дисциплину малых шагов, а не через разовые эмоциональные рывки.",
    "По-человечески: меньше внутреннего шума и больше наблюдаемых фактов — тогда день складывается заметно устойчивее.",
)


def _extract_field(markdown_text: str, prefix: str) -> str:
    for raw_line in (markdown_text or "").splitlines():
        line = raw_line.strip()
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return ""


def _hash_unit(seed: str) -> float:
    value = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16)
    return value / 0xFFFFFFFF


def _day_wave(forecast_date: date, phase_shift: float) -> float:
    day = forecast_date.toordinal()
    # Гладкая суточная волна 0..1 для кросс-профильной структуры дня.
    return (sin((2 * pi * (day + phase_shift)) / 7.0) + 1.0) / 2.0


def _profile_bias(profile: Profile, axis: str) -> float:
    seed = f"{profile.code}:{profile.kind}:{profile.gender}:{axis}"
    return _hash_unit(seed)


def _to_score(base: float, wave: float, noise: float) -> int:
    raw = 100.0 * (0.55 * base + 0.30 * wave + 0.15 * noise)
    return max(0, min(100, int(round(raw))))


def _tier(score: int) -> str:
    if score >= 67:
        return "high"
    if score >= 40:
        return "mid"
    return "low"


def _pick(seq: tuple[str, ...], seed: str, tier: str) -> str:
    # Для разных tiers выбираем разный сдвиг, чтобы результат не схлопывался.
    tier_shift = {"high": 0, "mid": 1, "low": 2}[tier]
    idx = (int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) + tier_shift) % len(seq)
    return seq[idx]


def _profile_signature(profile: Profile) -> str:
    particle = (_extract_field(profile.characteristic_markdown, "- **Частица:**") or "").lower()
    spin = (_extract_field(profile.characteristic_markdown, "- **Спин:**") or "").lower()
    charge = (_extract_field(profile.characteristic_markdown, "- **Заряд:**") or "").lower()
    seed = f"{profile.code}:{profile.kind}:{profile.gender}:{particle}:{spin}:{charge}"
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return h[:10]


def build_daily_markdown(profile: Profile, forecast_date: date) -> str:
    key = f"{profile.code}:{forecast_date.isoformat()}"
    particle = _extract_field(profile.characteristic_markdown, "- **Частица:**") or "не указан"
    spin = _extract_field(profile.characteristic_markdown, "- **Спин:**") or "не указан"
    charge = _extract_field(profile.characteristic_markdown, "- **Заряд:**") or "не указан"

    base_focus = _profile_bias(profile, "focus")
    base_social = _profile_bias(profile, "social")
    base_resilience = _profile_bias(profile, "resilience")
    base_impulse = _profile_bias(profile, "impulse")

    wave_focus = _day_wave(forecast_date, 0.3)
    wave_social = _day_wave(forecast_date, 1.7)
    wave_resilience = _day_wave(forecast_date, 2.9)
    wave_impulse = _day_wave(forecast_date, 4.1)

    focus_score = _to_score(base_focus, wave_focus, _hash_unit(f"{key}:focus_noise"))
    social_score = _to_score(base_social, wave_social, _hash_unit(f"{key}:social_noise"))
    resilience_score = _to_score(base_resilience, wave_resilience, _hash_unit(f"{key}:res_noise"))
    impulse_score = _to_score(base_impulse, wave_impulse, _hash_unit(f"{key}:impulse_noise"))
    overload_risk = max(0, min(100, int(round((impulse_score * 0.7 + (100 - resilience_score) * 0.6) / 1.3))))

    focus_tier = _tier(focus_score)
    social_tier = _tier(social_score)
    resilience_tier = _tier(resilience_score)
    overload_tier = _tier(100 - overload_risk)

    energy_line = _pick(ENERGY_COMMENTS, f"{key}:energy", resilience_tier)
    focus_line = _pick(FOCUS_COMMENTS, f"{key}:focus", focus_tier)
    social_line = _pick(SOCIAL_COMMENTS, f"{key}:social", social_tier)
    risk_line = _pick(RISK_COMMENTS, f"{key}:risk", overload_tier)
    practice_line = _pick(PRACTICE_COMMENTS, f"{key}:practice", resilience_tier)
    human_line = _pick(HUMAN_CODA, f"{key}:human:{_profile_signature(profile)}", _tier((resilience_score + social_score) // 2))

    profile_specific = (
        f"Профильная связка дня: частица «{particle}», спин «{spin}», заряд «{charge}». "
        "Это задаёт не «судьбу», а диапазон устойчивых реакций в текущем фоне."
    )
    profile_pattern = _pick(PATTERN_COMMENTS, f"{key}:pattern:{_profile_signature(profile)}", _tier((focus_score + social_score) // 2))

    timing_hint = (
        "Окно высокой точности чаще открывается в первой половине дня; "
        "во второй половине приоритет — удержание качества канала, а не скорость."
        if focus_score >= social_score
        else "Социальный канал сегодня значимее индивидуального рывка: "
             "лучше встраивать решения в диалог, а не в одиночный импульс."
    )

    # Верифицируемые гипотезы дня (чтобы в конце дня можно было сверить, без Барнума-расплывчатости).
    check_1 = (
        "Если вы ограничите день 1 главным приоритетом, вероятность его завершения будет выше 70%."
        if focus_score >= 55
        else "Если вы возьмёте больше 1 приоритета, высок риск недозавершения ключевой задачи."
    )
    check_2 = (
        "В диалогах эффект даст формат «короткий факт -> уточняющий вопрос» (минимум 1 конфликт будет снят на ранней стадии)."
        if social_score >= 60
        else "В диалогах сегодня критично заранее зафиксировать рамку разговора, иначе высок шанс срыва в интерпретации."
    )
    check_3 = (
        "После 18:00 держите темп на 20-30% ниже дневного: это снизит вечерний перегрев."
        if overload_risk >= 50
        else "После 18:00 можно делать лёгкую добивку задач, но без входа в новые сложные темы."
    )

    return "\n".join(
        [
            f"### Ежедневный прогноз: {profile.display_name} · {forecast_date.strftime('%d.%m.%Y')}",
            "",
            "#### Параметры системы на день",
            "",
            f"- **Фокус:** {focus_score}/100",
            f"- **Социальная проводимость:** {social_score}/100",
            f"- **Ресурс устойчивости:** {resilience_score}/100",
            f"- **Импульсивность контура:** {impulse_score}/100",
            f"- **Риск перегрева:** {overload_risk}/100",
            "",
            "#### Интерпретация по вашей физической модели",
            "",
            f"- **Фон поля:** {energy_line}",
            f"- **Когнитивный режим:** {focus_line}",
            f"- **Социальная динамика:** {social_line}",
            f"- **Зона риска:** {risk_line}",
            f"- **Практика стабилизации:** {practice_line}",
            "",
            "#### Профильно-специфический контур",
            "",
            profile_specific,
            profile_pattern,
            "",
            "#### Окна дня",
            "",
            timing_hint,
            "",
            "#### Гипотезы дня для вечерней сверки",
            "",
            f"1. {check_1}",
            f"2. {check_2}",
            f"3. {check_3}",
            "",
            "#### Протокол сверки в конце дня (2 минуты)",
            "",
            "- Отметьте: выполнен ли главный приоритет дня (да/нет).",
            "- Оцените по шкале 0-10 качество коммуникации в ключевом разговоре.",
            "- Зафиксируйте, был ли перегрев после 18:00 (да/нет) и из-за чего.",
            "- Сверьте прогноз с фактом: какие 1-2 пункта совпали максимально точно.",
            "",
            human_line,
        ]
    )


def _build_llm_prompt(profile: Profile, forecast_date: date) -> str:
    particle = _extract_field(profile.characteristic_markdown, "- **Частица:**") or "не указан"
    spin = _extract_field(profile.characteristic_markdown, "- **Спин:**") or "не указан"
    charge = _extract_field(profile.characteristic_markdown, "- **Заряд:**") or "не указан"
    base_profile_md = (profile.characteristic_markdown or "")[:2400]

    return (
        "Сгенерируй ежедневный прогноз строго на русском языке в стиле "
        "«физика знаков и куспидов», без мистики и без эффекта Барнума.\n\n"
        f"Профиль: {profile.display_name}\n"
        f"Дата: {forecast_date.isoformat()}\n"
        f"Тип: {profile.kind}\n"
        f"Частица: {particle}\n"
        f"Спин: {spin}\n"
        f"Заряд: {charge}\n\n"
        "Опорный профиль (сокращённо):\n"
        f"{base_profile_md}\n\n"
        "Требования к формату ответа:\n"
        "1) Верни ТОЛЬКО markdown, без пояснений и без кода.\n"
        "2) Обязательные разделы:\n"
        "   - ### Ежедневный прогноз: <профиль> · <дата>\n"
        "   - #### Параметры системы на день (5 метрик 0..100)\n"
        "   - #### Интерпретация по физической модели\n"
        "   - #### Профильно-специфический контур\n"
        "   - #### Окна дня\n"
        "   - #### Гипотезы дня для вечерней сверки (3 пункта)\n"
        "   - #### Протокол сверки в конце дня (2 минуты)\n"
        "3) Прогноз должен быть уникален для этого профиля и этой даты.\n"
        "4) Избегай универсальных фраз типа «прислушайтесь к себе» без конкретики.\n"
        "5) Дай конкретные проверяемые гипотезы, чтобы читатель мог сверить вечером.\n"
        "6) Объём: 1800-2600 символов.\n"
    )


def _try_deepseek_daily_markdown(profile: Profile, forecast_date: date) -> str | None:
    api_key = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
    if not api_key:
        return None

    api_url = (os.getenv("DEEPSEEK_API_URL") or "https://api.deepseek.com/chat/completions").strip()
    model = (os.getenv("DEEPSEEK_MODEL") or "deepseek-chat").strip()
    timeout_seconds = int((os.getenv("DEEPSEEK_TIMEOUT_SECONDS") or "25").strip() or "25")

    payload = {
        "model": model,
        "temperature": 0.35,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты senior-редактор сервиса «Физика знаков и куспидов». "
                    "Пишешь точно, проверяемо, без мистики и без общих формулировок."
                ),
            },
            {"role": "user", "content": _build_llm_prompt(profile, forecast_date)},
        ],
    }

    req = url_request.Request(
        api_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with url_request.urlopen(req, timeout=timeout_seconds) as resp:
            body = resp.read().decode("utf-8")
        data = json.loads(body)
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        if not content:
            return None
        return content
    except (url_error.URLError, TimeoutError, ValueError, KeyError, IndexError, TypeError):
        return None


def ensure_daily_forecast(profile: Profile, forecast_date: date) -> DailyForecast:
    content = _try_deepseek_daily_markdown(profile, forecast_date) or build_daily_markdown(profile, forecast_date)
    obj, _ = DailyForecast.objects.update_or_create(
        profile=profile,
        forecast_date=forecast_date,
        defaults={"content_markdown": content},
    )
    return obj
