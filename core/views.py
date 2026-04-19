from __future__ import annotations

import json
import re
from urllib.parse import urlencode

from django.conf import settings
from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render

from .article_loader import get_article_from_disk, load_article_stubs_from_disk
from .models import Article, Profile, Relationship
from .relationship_display import (
    LABEL_BOUND,
    LABEL_INTIMACY,
    LABEL_INTERACTION,
    LABEL_QUANTUM,
    LABEL_RESULT,
    LABEL_SYNTHESIS,
    LABEL_VULN,
    LABEL_WHY,
    humanize_relationship_field,
    physics_laws_block,
)


def _get_relationship(source_id: str, target_id: str) -> Relationship:
    """Для пары знак–куспид всегда связь «знак → куспид» (текст из MD знака), порядок выбора в UI не важен."""
    qs = Relationship.objects.select_related("source", "target")
    source = get_object_or_404(Profile, pk=source_id)
    target = get_object_or_404(Profile, pk=target_id)

    if source.kind != target.kind:
        sign, cusp = (
            (source, target) if source.kind == Profile.KIND_SIGN else (target, source)
        )
        rel = qs.filter(source=sign, target=cusp).first()
        if rel:
            return rel
        raise Http404("Связь не найдена")

    rel = qs.filter(source_id=source_id, target_id=target_id).first()
    if rel:
        return rel
    raise Http404("Связь не найдена")


def index(request: HttpRequest):
    return render(request, "core/index.html")


def about_view(request: HttpRequest):
    """Страница «О подходе» — фундамент доверия проекта."""
    return render(request, "core/about.html")


def article_list(request: HttpRequest):
    articles = list(
        Article.objects.only("slug", "title", "summary", "sort_order").order_by("sort_order", "slug")
    )
    if not articles:
        articles = load_article_stubs_from_disk()
    return render(
        request,
        "core/article_list.html",
        {"articles": articles},
    )


def article_detail(request: HttpRequest, slug: str):
    article = Article.objects.filter(slug=slug).first()
    if article is None:
        article = get_article_from_disk(slug)
    if article is None:
        raise Http404("Статья не найдена")
    canonical_url = _absolute_path_url(request, request.path)
    return render(
        request,
        "core/article_detail.html",
        {
            "article": article,
            "canonical_url": canonical_url,
        },
    )


def options_api(request: HttpRequest) -> JsonResponse:
    mode = request.GET.get("mode")
    if mode not in ("characteristic", "relationship"):
        return JsonResponse({"error": "Unsupported mode"}, status=400)
    items = [
        {"id": p.id, "label": p.display_name}
        for p in Profile.objects.all().only("id", "display_name")
    ]
    return JsonResponse({"items": items})


def relationship_targets_api(request: HttpRequest) -> JsonResponse:
    source_id = request.GET.get("source_id")
    if not source_id:
        return JsonResponse({"error": "source_id is required"}, status=400)

    rels = (
        Relationship.objects.select_related("target")
        .filter(source_id=source_id)
        .order_by("target__code")
    )
    items = [{"id": rel.target.id, "label": rel.target.display_name} for rel in rels]
    return JsonResponse({"items": items})


def _extract_field(markdown_text: str, prefix: str) -> str:
    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return ""


def _truncate_plain(text: str, max_len: int = 158) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= max_len:
        return text
    cut = text[: max_len - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "…"


def _first_plain_paragraph_from_markdown(md: str) -> str:
    for raw in md.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("---"):
            continue
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        if len(line) > 20:
            return line
    return ""


def _absolute_path_url(request: HttpRequest, path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    base = getattr(settings, "PUBLIC_SITE_URL", "") or ""
    if base:
        return f"{base}{path}"
    return request.build_absolute_uri(path)


def _absolute_query_url(request: HttpRequest, query: dict[str, str]) -> str:
    q = urlencode(query)
    path = "/?" + q if q else "/"
    return _absolute_path_url(request, path if q else "/")


def _seo_payload_for_sign(request: HttpRequest, profile: Profile) -> dict:
    """Динамический SEO для основного знака (не куспид)."""
    particle = _extract_field(profile.characteristic_markdown, "- **Частица:**")
    plain = _first_plain_paragraph_from_markdown(profile.characteristic_markdown)
    gender_ru = profile.get_gender_display()
    title = f"{profile.display_name} — физико-химическая характеристика | Физика знаков и куспидов"
    if plain:
        desc = _truncate_plain(f"{profile.display_name} ({gender_ru}): {plain}")
    elif particle:
        desc = _truncate_plain(
            f"{profile.display_name}: модель «частица» — {particle}. "
            "Физико-химическая характеристика знака без шаблонной астрологии."
        )
    else:
        desc = _truncate_plain(
            f"{profile.display_name}: характеристика знака в физико-химической интерпретации "
            "(структура, взаимодействия, отношения)."
        )
    keywords = (
        f"{profile.name}, зодиак, {gender_ru}, характеристика знака, физика знаков, "
        "совместимость, физико-химическая модель"
    )
    q = {"mode": "characteristic", "profile_id": str(profile.pk)}
    canonical = _absolute_query_url(request, q)
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": canonical,
        "inLanguage": "ru",
        "isPartOf": {
            "@type": "WebSite",
            "name": "Физика знаков и куспидов",
            "url": _absolute_path_url(request, "/"),
        },
    }
    return {
        "apply": True,
        "profile_id": profile.pk,
        "title": title,
        "description": desc,
        "keywords": keywords,
        "canonical": canonical,
        "og_title": title,
        "og_description": desc,
        "twitter_title": title,
        "twitter_description": desc,
        "json_ld": json.dumps(json_ld, ensure_ascii=False),
    }


def _seo_payload_for_cusp(request: HttpRequest, profile: Profile) -> dict:
    """Динамический SEO для куспида (граница двух знаков, суперпозиция в модели)."""
    particle = _extract_field(profile.characteristic_markdown, "- **Частица:**")
    sup = _extract_field(profile.characteristic_markdown, "- **Суперпозиция куспида:**")
    plain = _first_plain_paragraph_from_markdown(profile.characteristic_markdown)
    gender_ru = profile.get_gender_display()
    title = f"{profile.display_name} — характеристика куспида | Физика знаков и куспидов"
    if plain:
        desc = _truncate_plain(f"{profile.display_name} ({gender_ru}): {plain}")
    elif sup:
        desc = _truncate_plain(f"{profile.display_name}: {sup}")
    elif particle:
        desc = _truncate_plain(
            f"{profile.display_name}: физико-химическая модель (частица: {particle}). "
            "Куспид — граница знаков и суперпозиция режимов."
        )
    else:
        desc = _truncate_plain(
            f"{profile.display_name}: характеристика куспида в физико-химической интерпретации."
        )
    keywords = (
        f"{profile.name}, куспид, {gender_ru}, граница знаков, суперпозиция, "
        "физика знаков, характеристика куспида, совместимость"
    )
    q = {"mode": "characteristic", "profile_id": str(profile.pk)}
    canonical = _absolute_query_url(request, q)
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": canonical,
        "inLanguage": "ru",
        "isPartOf": {
            "@type": "WebSite",
            "name": "Физика знаков и куспидов",
            "url": _absolute_path_url(request, "/"),
        },
    }
    return {
        "apply": True,
        "profile_id": profile.pk,
        "title": title,
        "description": desc,
        "keywords": keywords,
        "canonical": canonical,
        "og_title": title,
        "og_description": desc,
        "twitter_title": title,
        "twitter_description": desc,
        "json_ld": json.dumps(json_ld, ensure_ascii=False),
    }


def _seo_payload_for_relationship(
    request: HttpRequest, relationship: Relationship
) -> dict:
    """Динамический SEO для пары профилей (режим отношений)."""
    src = relationship.source
    tgt = relationship.target
    title = (
        f"{src.display_name} и {tgt.display_name}: отношения — "
        "физика взаимодействия | Физика знаков и куспидов"
    )
    hi = humanize_relationship_field((relationship.interaction_type or "").strip())
    hb = humanize_relationship_field((relationship.bound_state or "").strip())
    parts = [
        f"Пара «{src.display_name}» — «{tgt.display_name}».",
        f"{LABEL_INTERACTION}: {hi or 'не описано'}.",
    ]
    if hb:
        parts.append(f"{LABEL_BOUND}: {hb}.")
    rl = (relationship.result_line or "").strip()
    if rl:
        parts.append(rl)
    else:
        why = (relationship.why or "").strip()
        if why:
            parts.append(why)
    desc = _truncate_plain(" ".join(parts))
    keywords = (
        f"{src.name}, {tgt.name}, отношения знаков, совместимость, "
        "физико-химическая модель, физика знаков и куспидов"
    )
    q = {
        "mode": "relationship",
        "source_id": str(src.pk),
        "target_id": str(tgt.pk),
    }
    canonical = _absolute_query_url(request, q)
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": canonical,
        "inLanguage": "ru",
        "isPartOf": {
            "@type": "WebSite",
            "name": "Физика знаков и куспидов",
            "url": _absolute_path_url(request, "/"),
        },
    }
    return {
        "apply": True,
        "source_id": src.pk,
        "target_id": tgt.pk,
        "title": title,
        "description": desc,
        "keywords": keywords,
        "canonical": canonical,
        "og_title": title,
        "og_description": desc,
        "twitter_title": title,
        "twitter_description": desc,
        "json_ld": json.dumps(json_ld, ensure_ascii=False),
    }


def _build_reference_relationship_block(relationship: Relationship) -> str:
    source = relationship.source
    target = relationship.target
    src_particle = _extract_field(source.characteristic_markdown, "- **Частица:**")
    tgt_particle = _extract_field(target.characteristic_markdown, "- **Частица:**")
    src_spin = _extract_field(source.characteristic_markdown, "- **Спин:**")
    tgt_spin = _extract_field(target.characteristic_markdown, "- **Спин:**")
    src_charge = _extract_field(source.characteristic_markdown, "- **Заряд:**")
    tgt_charge = _extract_field(target.characteristic_markdown, "- **Заряд:**")
    tgt_superposition = _extract_field(target.characteristic_markdown, "- **Суперпозиция куспида:**")

    interaction = relationship.interaction_type.strip() or "не определено"
    interaction_plain = humanize_relationship_field(interaction)

    lines = [
        "#### Эталонный расширенный разбор (физика + экспрессия)",
        "",
        f"**Кто есть кто:** `{source.display_name}` как `{src_particle}` и `{target.display_name}` как `{tgt_particle}`. "
        f"Заряды ({src_charge}, {tgt_charge}) и спины ({src_spin}, {tgt_spin}) задают доступные каналы сцепления и рассеяния.",
        "",
        f"**Почему именно это взаимодействие:** если сказать по-простому — {interaction_plain}. В формулировке модели: «{interaction}». "
        "В наблюдаемой паре это значит, что система не просто обменивается эмоцией, а ищет конфигурацию с меньшей энергией и более высокой связностью.",
        "",
        "**Интимный канал:** при сближении волновые функции перекрываются, а интенсивность контакта растёт как функция "
        "фазовой синхронизации. Когда фазы совпадают, читатель чувствует это как «необъяснимую тягу», но физически это "
        "рост вероятности связанного состояния в конкретном окне энергии.",
        "",
        "**Синтез и химия связи:** если обмен устойчив и потери на шум меньше притока, пара входит в режим, где каждая "
        "итерация делает контур плотнее. Это тот случай, когда отношения выглядят не как вспышка, а как рождение собственного "
        "малого «реактора» с долгим свечением.",
        "",
        "**Где ломается:** главные риски — декогеренция, перегрев поля и внешние высокоэнергетические удары. "
        "Они срывают настройку, и даже сильная пара может уйти из связанного состояния в рассеяние.",
    ]

    if target.kind == Profile.KIND_CUSP and tgt_superposition:
        lines.extend(
            [
                "",
                f"**Квантовая динамика куспида:** {tgt_superposition}. Пока коэффициенты α/β близки к балансу, "
                "контакт пульсирует между режимами; при коллапсе в подходящую ветвь связь резко усиливается, "
                "при коллапсе в несовместимую — гаснет, как будто поле «выключили».",
            ]
        )

    lines.extend(
        [
            "",
            "**Человеческий эффект (без мистики):** текст ощущается как «точно про меня», потому что описывает универсальные "
            "динамики близости (притяжение, устойчивость, распад) через физически понятные модели. Это и даёт сильную эмпатию "
            "без отказа от логики и законов природы.",
        ]
    )
    return "\n".join(lines)


def _build_state_poetic_block(relationship: Relationship) -> str:
    state = (relationship.bound_state or "").lower()

    if "дейтрон" in state:
        return "\n".join(
            [
                "#### Образ связанного состояния: дейтрон",
                "",
                "**Ядерное объятие:** дейтрон — это не просто ядро, а плотная связка протона и нейтрона, удержанная остаточным сильным взаимодействием. "
                "Если смотреть глубже, это динамический вальс двух нуклонов в общем потенциальном колодце, где связь живёт на грани распада и устойчивости.",
                "",
                "**Историческая роль во Вселенной:** именно дейтронный шаг `p + n -> d + γ` открывает дорогу синтезу более тяжёлых ядер. "
                "В отношениях это читается как «точка невозврата»: пара перестаёт быть просто контактом и становится источником новой структуры.",
                "",
                "**Почему это цепляет человека:** здесь есть и хрупкость, и мощь — ощущение, что связь держится не за счёт декораций, "
                "а за счёт реального энергетического сцепления, которое переживает шум и внешние удары.",
            ]
        )

    if "резонанс" in state:
        return "\n".join(
            [
                "#### Образ связанного состояния: резонансный контур",
                "",
                "Это связь, где главное — частота и фаза. Пока резонанс удержан, энергия пары растёт почти без трения; "
                "при срыве фазы даже сильные участники быстро теряют сцепление.",
            ]
        )

    if "метастабиль" in state:
        return "\n".join(
            [
                "#### Образ связанного состояния: метастабильная пара",
                "",
                "Это режим долгого удержания формы в локальном минимуме энергии: снаружи всё выглядит спокойно, "
                "но система требует тонкой термодинамической дисциплины, иначе возможен резкий срыв.",
            ]
        )

    if "связан" in state:
        return "\n".join(
            [
                "#### Образ связанного состояния: устойчивый узел",
                "",
                "Пара ведёт себя как конфигурация с пониженной энергией: чем точнее согласованы параметры, "
                "тем выше вероятность долгой связи и тем ниже утечки в рассеяние.",
            ]
        )

    return ""


def result_api(request: HttpRequest) -> JsonResponse:
    mode = request.GET.get("mode")

    if mode == "characteristic":
        profile_id = request.GET.get("profile_id")
        if not profile_id:
            return JsonResponse({"error": "profile_id is required"}, status=400)
        profile = get_object_or_404(Profile, id=profile_id)
        if profile.kind == Profile.KIND_SIGN:
            seo = _seo_payload_for_sign(request, profile)
        else:
            seo = _seo_payload_for_cusp(request, profile)
        return JsonResponse(
            {
                "title": profile.display_name,
                "type": "characteristic",
                "kind": profile.kind,
                "content_markdown": profile.characteristic_markdown,
                "seo": seo,
            }
        )

    if mode == "relationship":
        source_id = request.GET.get("source_id")
        target_id = request.GET.get("target_id")
        if not source_id or not target_id:
            return JsonResponse({"error": "source_id and target_id are required"}, status=400)
        relationship = _get_relationship(source_id, target_id)
        seo = _seo_payload_for_relationship(request, relationship)
        hi = humanize_relationship_field((relationship.interaction_type or "").strip())
        hb = humanize_relationship_field((relationship.bound_state or "").strip())
        content = [
            f"### {relationship.heading}",
            "",
            "Сначала — как обычно говорят о паре; затем короткий блок **законов и формул** как подсветка к тому же смыслу; "
            "ниже — развёрнутый текст модели, если захотите углубиться.",
            "",
        ]
        if (relationship.result_line or "").strip():
            content.append(f"- **{LABEL_RESULT}:** {relationship.result_line.strip()}")
        if getattr(relationship, "human_coda", "").strip():
            content.append(f"- **По-человечески:** {relationship.human_coda.strip()}")
        content.append("")
        content.append(f"- **{LABEL_INTERACTION}:** {hi or '—'}")
        content.append(f"- **{LABEL_BOUND}:** {hb or '—'}")
        if (relationship.why or "").strip():
            content.append(f"- **{LABEL_WHY}:** {relationship.why.strip()}")
        if (relationship.quantum_dynamics or "").strip():
            content.append(f"- **{LABEL_QUANTUM}:** {relationship.quantum_dynamics.strip()}")
        if (relationship.intimacy or "").strip():
            content.append(f"- **{LABEL_INTIMACY}:** {relationship.intimacy.strip()}")
        if (relationship.synthesis or "").strip():
            content.append(f"- **{LABEL_SYNTHESIS}:** {relationship.synthesis.strip()}")
        if (relationship.vulnerabilities or "").strip():
            content.append(f"- **{LABEL_VULN}:** {relationship.vulnerabilities.strip()}")
        content.append("")
        content.append(
            physics_laws_block(
                interaction_raw=(relationship.interaction_type or "").strip(),
                bound_raw=(relationship.bound_state or "").strip(),
                result_line=(relationship.result_line or "").strip(),
                human_coda=(getattr(relationship, "human_coda", "") or "").strip(),
                why=(relationship.why or "").strip(),
                quantum=(relationship.quantum_dynamics or "").strip(),
                intimacy=(relationship.intimacy or "").strip(),
                synthesis=(relationship.synthesis or "").strip(),
                vulnerabilities=(relationship.vulnerabilities or "").strip(),
            )
        )
        content.extend(
            [
                "",
                _build_state_poetic_block(relationship),
                "",
                "#### Расширенная физико-химическая интерпретация",
                relationship.enriched_text,
                "",
                _build_reference_relationship_block(relationship),
            ]
        )
        return JsonResponse(
            {
                "title": f"{relationship.source.display_name} -> {relationship.target.display_name}",
                "type": "relationship",
                "kind": None,
                "content_markdown": "\n".join(content),
                "seo": seo,
            }
        )

    return JsonResponse({"error": "Unsupported mode"}, status=400)
