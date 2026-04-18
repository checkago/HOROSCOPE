"""Парсинг гороскопов и загрузка в БД (общий код для MD и JSON)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from django.core.management.base import CommandError

from core.models import Profile, Relationship


def normalize_name(name: str) -> str:
    return name.replace("_", " ").strip()


def value_after_prefix(line: str, prefix: str) -> str:
    return line[len(prefix) :].strip()


def parse_profile(md_text: str) -> Tuple[str, str, str]:
    parts = md_text.split("## Часть 2.", maxsplit=1)
    if len(parts) != 2:
        raise ValueError("Не найден раздел '## Часть 2.'")
    part1 = parts[0].strip()

    first_line = part1.splitlines()[0].strip()
    if not first_line.startswith("# ") or " — " not in first_line:
        raise ValueError("Некорректный заголовок профиля")

    title = first_line[2:]
    name, gender_ru = [x.strip() for x in title.split(" — ", maxsplit=1)]
    return normalize_name(name), gender_ru, part1


def parse_particle_triplet(part1: str) -> Tuple[str, str, str]:
    particle = charge = spin = ""
    for line in part1.splitlines():
        line = line.strip()
        if line.startswith("- **Частица:**"):
            particle = value_after_prefix(line, "- **Частица:**")
        elif line.startswith("- **Заряд:**"):
            charge = value_after_prefix(line, "- **Заряд:**")
        elif line.startswith("- **Спин:**"):
            spin = value_after_prefix(line, "- **Спин:**")
    return particle, charge, spin


def parse_relation_blocks(md_text: str) -> List[Dict[str, str]]:
    if "## Часть 2." not in md_text:
        return []
    body = md_text.split("## Часть 2.", maxsplit=1)[1]
    chunks = body.split("### С ")

    parsed: List[Dict[str, str]] = []
    for chunk in chunks[1:]:
        lines = [line.rstrip() for line in chunk.strip().splitlines()]
        heading_raw = lines[0].strip()
        heading = f"С {heading_raw}"

        row: Dict[str, str] = {
            "heading": heading,
            "target_header": heading_raw,
            "interaction_type": "",
            "bound_state": "",
            "why": "",
            "quantum_dynamics": "",
            "intimacy": "",
            "synthesis": "",
            "vulnerabilities": "",
            "result_line": "",
            "human_coda": "",
        }

        for line in lines[1:]:
            line = line.strip()
            if line.startswith("- **Тип взаимодействия:**"):
                row["interaction_type"] = value_after_prefix(line, "- **Тип взаимодействия:**")
            elif line.startswith("- **Связанное состояние:**"):
                row["bound_state"] = value_after_prefix(line, "- **Связанное состояние:**")
            elif line.startswith("- **Почему именно так (физика):**"):
                row["why"] = value_after_prefix(line, "- **Почему именно так (физика):**")
            elif line.startswith("- **Квантовая динамика куспида:**"):
                row["quantum_dynamics"] = value_after_prefix(line, "- **Квантовая динамика куспида:**")
            elif line.startswith("- **Интим (физика):**"):
                row["intimacy"] = value_after_prefix(line, "- **Интим (физика):**")
            elif line.startswith("- **Ядерный синтез / Химия:**"):
                row["synthesis"] = value_after_prefix(line, "- **Ядерный синтез / Химия:**")
            elif line.startswith("- **Уязвимости:**"):
                row["vulnerabilities"] = value_after_prefix(line, "- **Уязвимости:**")
            elif line.startswith("- **Итог одной фразой:**"):
                row["result_line"] = value_after_prefix(line, "- **Итог одной фразой:**")
            elif line.startswith("- **По-человечески:**"):
                row["human_coda"] = value_after_prefix(line, "- **По-человечески:**")

        parsed.append(row)
    return parsed


def parse_target(target_header: str) -> Tuple[str, str]:
    if "-" not in target_header:
        raise ValueError(f"Некорректный заголовок связи: {target_header}")
    gender_token, name = target_header.split("-", maxsplit=1)
    gender = "female" if "Женщиной" in gender_token else "male"
    return normalize_name(name), gender


HADRON_KEYWORDS = ("протон", "нейтрон", "дейтрон", "тритон", "альфа-частица", "барион", "пи-мезон")
LEPTON_KEYWORDS = ("электрон", "позитрон", "мюон", "тау", "нейтрино", "антинейтрино", "бета-частица")


def classify_particle(particle: str) -> str:
    low = particle.lower()
    if any(k in low for k in HADRON_KEYWORDS):
        return "hadron"
    if any(k in low for k in LEPTON_KEYWORDS):
        return "lepton"
    if "фотон" in low:
        return "photon"
    if "бозон" in low:
        return "boson"
    return "quasi"


def em_interaction(charge_a: str, charge_b: str) -> str:
    if not charge_a or not charge_b:
        return "Электромагнитный канал не определён однозначно."
    if charge_a.startswith("+") and charge_b.startswith("-") or charge_a.startswith("-") and charge_b.startswith("+"):
        return "Кулоновское притяжение: разноимённые заряды снижают потенциальную энергию и тянут систему к связанному состоянию."
    if charge_a == "0" and charge_b == "0":
        return "Прямого кулоновского притяжения нет: взаимодействие идёт через поляризацию, обмен и более слабые каналы."
    if charge_a == "0" or charge_b == "0":
        return "Один компонент нейтрален: ЭМ-канал ограничен, но возможны индуцированные дипольные и орбитальные эффекты."
    return "Кулоновское отталкивание: одинаковый знак заряда повышает барьер сближения."


def strong_interaction(class_a: str, class_b: str) -> str:
    if class_a == "hadron" and class_b == "hadron":
        return "Сильное взаимодействие физически допустимо: на фемтометровых расстояниях возможен обмен мезонами и ядерное сцепление."
    return "Сильный канал либо закрыт, либо вторичен: система опирается на ЭМ/слабые/коллективные эффекты."


def weak_interaction(class_a: str, class_b: str) -> str:
    if "lepton" in (class_a, class_b):
        return "Слабое взаимодействие релевантно: разрешены процессы смены аромата/состояния и медленные перестройки через слабый ток."
    return "Слабый канал фоновый: влияет на долгую эволюцию, но не доминирует в моменте связи."


def quantum_math_note(target: Profile) -> str:
    if target.kind != Profile.KIND_CUSP:
        return "Математически устойчивость пары описывается корреляцией фаз и минимизацией энергии связанного состояния."
    return (
        "Куспид описывается суперпозицией |ψ⟩ = α|A⟩ + β|B⟩ (α² + β² = 1): "
        "вероятность конкретного поведенческого режима задаётся коэффициентами Born rule."
    )


def build_enriched_text(source: Profile, target: Profile, rel: Dict[str, str]) -> str:
    s_particle, s_charge, s_spin = parse_particle_triplet(source.characteristic_markdown)
    t_particle, t_charge, t_spin = parse_particle_triplet(target.characteristic_markdown)
    s_class = classify_particle(s_particle)
    t_class = classify_particle(t_particle)

    line1 = (
        f"Система `{source.display_name} -> {target.display_name}` трактуется как взаимодействие `{s_particle}` и `{t_particle}`. "
        f"{em_interaction(s_charge, t_charge)} "
        f"По спинам ({s_spin} и {t_spin}) совместимость связанного состояния определяется правилами сложения момента и доступными каналами рассеяния."
    )
    line2 = (
        f"{strong_interaction(s_class, t_class)} {weak_interaction(s_class, t_class)} "
        f"В терминах модели связи это объясняет, почему в описании стоит `{rel['interaction_type']}` и `{rel['bound_state']}`: "
        "это не произвольная метафора, а выбор наиболее физически правдоподобного доминирующего канала."
    )
    hc = rel.get("human_coda", "").strip()
    human_tail = f" Бытовой итог без формул: {hc}" if hc else ""
    line3 = (
        f"{quantum_math_note(target)} На уровне химической аналогии `{rel['synthesis']}` читается как результат конкуренции "
        "между образованием связи и её распадом через барьерные процессы. "
        f"Поэтому уязвимость `{rel['vulnerabilities']}` напрямую связана с потерей когерентности, а итог `{rel['result_line']}` "
        f"фиксирует наблюдаемую динамику системы.{human_tail}"
    )
    return "\n\n".join([line1, line2, line3])


def _create_relationship(source: Profile, target: Profile, rel_data: Dict[str, str]) -> None:
    Relationship.objects.create(
        source=source,
        target=target,
        heading=rel_data["heading"],
        interaction_type=rel_data["interaction_type"],
        bound_state=rel_data["bound_state"],
        why=rel_data["why"],
        quantum_dynamics=rel_data["quantum_dynamics"],
        intimacy=rel_data["intimacy"],
        synthesis=rel_data["synthesis"],
        vulnerabilities=rel_data["vulnerabilities"],
        result_line=rel_data["result_line"],
        human_coda=rel_data["human_coda"],
        enriched_text=build_enriched_text(source, target, rel_data),
    )


def run_md_import(base_dir: Path) -> Tuple[int, int]:
    files = sorted(base_dir.glob("[0-9][0-9]_*.md"))
    if not files:
        raise CommandError("Не найдены MD-файлы вида [0-9][0-9]_*.md")

    Relationship.objects.all().delete()
    Profile.objects.all().delete()

    profiles_map: Dict[Tuple[str, str], Profile] = {}

    for path in files:
        md_text = path.read_text(encoding="utf-8")
        name, gender_ru, part1 = parse_profile(md_text)
        code = path.name.split("_", 1)[0]
        kind = Profile.KIND_CUSP if "Куспид" in name else Profile.KIND_SIGN
        gender = Profile.GENDER_MALE if gender_ru == "Мужчина" else Profile.GENDER_FEMALE

        profile = Profile.objects.create(
            code=code,
            name=name,
            display_name=f"{name} — {gender_ru}",
            kind=kind,
            gender=gender,
            source_file=path.name,
            characteristic_markdown=part1,
        )
        profiles_map[(name, gender)] = profile

    for path in files:
        md_text = path.read_text(encoding="utf-8")
        source_name, source_gender_ru, _ = parse_profile(md_text)
        source_gender = Profile.GENDER_MALE if source_gender_ru == "Мужчина" else Profile.GENDER_FEMALE
        source = profiles_map[(source_name, source_gender)]

        for rel_data in parse_relation_blocks(md_text):
            target_name, target_gender = parse_target(rel_data["target_header"])
            target = profiles_map.get((target_name, target_gender))
            if not target:
                raise CommandError(f"Не найден target: {target_name} ({target_gender})")
            _create_relationship(source, target, rel_data)

    return Profile.objects.count(), Relationship.objects.count()


def _rel_dict_from_json(obj: Dict[str, Any]) -> Dict[str, str]:
    th = str(obj["target_header"]).strip()
    return {
        "heading": f"С {th}",
        "target_header": th,
        "interaction_type": str(obj.get("interaction_type", "")).strip(),
        "bound_state": str(obj.get("bound_state", "")).strip(),
        "why": str(obj.get("why", "")).strip(),
        "quantum_dynamics": str(obj.get("quantum_dynamics", "")).strip(),
        "intimacy": str(obj.get("intimacy", "")).strip(),
        "synthesis": str(obj.get("synthesis", "")).strip(),
        "vulnerabilities": str(obj.get("vulnerabilities", "")).strip(),
        "result_line": str(obj.get("result_line", "")).strip(),
        "human_coda": str(obj.get("human_coda", "")).strip(),
    }


def run_json_import(base_dir: Path) -> Tuple[int, int]:
    """Файлы [0-9][0-9]_*.json — см. документацию в import_horoscope_json.Command."""
    files = sorted(base_dir.glob("[0-9][0-9]_*.json"))
    if not files:
        raise CommandError("Не найдены JSON-файлы вида [0-9][0-9]_*.json")

    Relationship.objects.all().delete()
    Profile.objects.all().delete()

    profiles_map: Dict[Tuple[str, str], Profile] = {}

    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        name = normalize_name(str(data["name"]).strip())
        gender_ru = str(data["gender_ru"]).strip()
        part1 = str(data["characteristic_markdown"]).strip()
        code = str(data.get("code") or path.name.split("_", 1)[0]).strip()
        source_file = str(data.get("source_file", path.name)).strip()

        if "relationships" not in data or not isinstance(data["relationships"], list):
            raise CommandError(f"{path.name}: нет списка relationships")

        kind = Profile.KIND_CUSP if "Куспид" in name else Profile.KIND_SIGN
        gender = Profile.GENDER_MALE if gender_ru == "Мужчина" else Profile.GENDER_FEMALE

        profile = Profile.objects.create(
            code=code,
            name=name,
            display_name=f"{name} — {gender_ru}",
            kind=kind,
            gender=gender,
            source_file=source_file,
            characteristic_markdown=part1,
        )
        profiles_map[(name, gender)] = profile

    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        name = normalize_name(str(data["name"]).strip())
        gender_ru = str(data["gender_ru"]).strip()
        source_gender = Profile.GENDER_MALE if gender_ru == "Мужчина" else Profile.GENDER_FEMALE
        source = profiles_map[(name, source_gender)]

        for i, obj in enumerate(data["relationships"]):
            if not isinstance(obj, dict):
                raise CommandError(f"{path.name}: relationships[{i}] не объект")
            if "target_header" not in obj:
                raise CommandError(f"{path.name}: relationships[{i}] без target_header")
            rel_data = _rel_dict_from_json(obj)
            target_name, target_gender = parse_target(rel_data["target_header"])
            target = profiles_map.get((target_name, target_gender))
            if not target:
                raise CommandError(f"{path.name}: не найден target {target_name} ({target_gender})")
            _create_relationship(source, target, rel_data)

    return Profile.objects.count(), Relationship.objects.count()
