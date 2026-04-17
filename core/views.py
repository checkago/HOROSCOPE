from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Profile, Relationship


def index(request: HttpRequest):
    return render(request, "core/index.html")


def options_api(request: HttpRequest) -> JsonResponse:
    mode = request.GET.get("mode")

    if mode == "characteristic":
        items = [
            {"id": p.id, "label": p.display_name}
            for p in Profile.objects.all().only("id", "display_name")
        ]
        return JsonResponse({"items": items})

    if mode == "relationship":
        items = [
            {"id": p.id, "label": p.display_name}
            for p in Profile.objects.all().only("id", "display_name")
        ]
        return JsonResponse({"items": items})

    return JsonResponse({"error": "Unsupported mode"}, status=400)


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
    if source.name == "Лев" and target.name == "Куспид Водолей-Рыбы":
        # Эталонное правило из основного промта.
        interaction = "сильное (коллапс суперпозиции)"

    lines = [
        "#### Эталонный расширенный разбор (физика + экспрессия)",
        "",
        f"**Кто есть кто:** `{source.display_name}` как `{src_particle}` и `{target.display_name}` как `{tgt_particle}`. "
        f"Заряды ({src_charge}, {tgt_charge}) и спины ({src_spin}, {tgt_spin}) задают доступные каналы сцепления и рассеяния.",
        "",
        f"**Почему именно это взаимодействие:** доминирует `{interaction}`; в наблюдаемой паре это означает, что "
        "система не просто обменивается эмоцией, а физически ищет конфигурацию с меньшей энергией и более высокой связностью.",
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


def result_api(request: HttpRequest) -> JsonResponse:
    mode = request.GET.get("mode")

    if mode == "characteristic":
        profile_id = request.GET.get("profile_id")
        if not profile_id:
            return JsonResponse({"error": "profile_id is required"}, status=400)
        profile = get_object_or_404(Profile, id=profile_id)
        return JsonResponse(
            {
                "title": profile.display_name,
                "type": "characteristic",
                "content_markdown": profile.characteristic_markdown,
            }
        )

    if mode == "relationship":
        source_id = request.GET.get("source_id")
        target_id = request.GET.get("target_id")
        if not source_id or not target_id:
            return JsonResponse({"error": "source_id and target_id are required"}, status=400)
        relationship = get_object_or_404(
            Relationship.objects.select_related("source", "target"),
            source_id=source_id,
            target_id=target_id,
        )
        content = [
            f"### {relationship.heading}",
            "",
            f"- **Тип взаимодействия:** {relationship.interaction_type}",
            f"- **Связанное состояние:** {relationship.bound_state}",
        ]
        if relationship.why:
            content.append(f"- **Почему именно так (физика):** {relationship.why}")
        if relationship.quantum_dynamics:
            content.append(f"- **Квантовая динамика куспида:** {relationship.quantum_dynamics}")
        content.extend(
            [
                f"- **Интим (физика):** {relationship.intimacy}",
                f"- **Ядерный синтез / Химия:** {relationship.synthesis}",
                f"- **Уязвимости:** {relationship.vulnerabilities}",
                f"- **Итог одной фразой:** {relationship.result_line}",
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
                "content_markdown": "\n".join(content),
            }
        )

    return JsonResponse({"error": "Unsupported mode"}, status=400)
