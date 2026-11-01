"""Anonymize one race file by Д1 (Stage 2 S3, TASK-8 AC #2).

Д1 (а) with the additions of ``[мейнтейнер: 2026-10-31]``, field by field (legacy ``to_dict`` /
``update_data`` [код: pysport@b548c35 sportorg/models/memory.py:96-137,601-700,1424-1477,
1615-1643], old field names [код: pysport@b548c35 sportorg/modules/backup/json.py:84-118]):

- person: ``surname``, ``name``, ``middle_name`` → person pseudonyms; ``comment`` → text;
  ``world_code``, ``national_code`` → code pseudonyms (a number stays a number with as many
  digits), empty stays empty; ``card_number`` and the old ``sportident_card`` → another number of
  the same card type; ``birth_date`` → another day of the same year (``birthday`` follows it);
  ``year`` kept.
- result: ``card_number``/``sportident_card`` as for persons; ``status_comment`` kept when it is
  a rule clause (``п.п.6.6.4``, ``пп6.6.4``), alone or with one of legacy's hints after ``#``; a
  clause with any other hint keeps the clause and masks the hint; anything else → text
  ``[мейнтейнер: 2026-11-01]``. Legacy copies the comment into ``result``, ``result_relay``,
  ``result_current`` and, cut to 14 characters per day, ``multi_day_results``, and never reads
  them back [код: pysport@b548c35 sportorg/models/memory.py:480-490,650-747,969-973]: they get
  the masked comment where they hold it, times and kept comments stay.
- organization: ``name`` → org; ``country``, ``region`` and the old ``address`` → place;
  ``contact`` → contact; ``code`` → code.
- race data: ``title``, ``short_title``, ``description``, ``location``, ``url`` → the neutral id
  ``<file id>/<race index>``; ``chief_referee``, ``secretary`` → person pseudonyms.
- settings: ``live_urls``, ``live_url``, ``live_token``, ``telegram_chat_id``,
  ``telegram_thread_id``, ``teamwork_token``, ``teamwork_host`` cleared
  [код: pysport@b548c35 sportorg/gui/dialogs/live_dialog.py:201, telegram_dialog.py:140];
  ``telegram_template``, ``split_template`` (free text, a path) → text.
- kept: ids, bibs, groups, courses, controls, punches, times, statuses and every setting legacy
  reads (``LEGACY_SETTINGS``), because the recalculation depends on them.
- a key this module does not know, in a person, result, organization, race, its data, its
  settings or the file: legacy does not read it, so every string inside it becomes a text
  pseudonym (keys of nested objects kept); counted as ``unknown:<object>.<key>``.

Strings are masked through ``scripts.corpus.pseudonym``: a function of the key and the value only,
so the output of one record or one file never depends on another (locality).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

from scripts._json import as_dict, as_list, parse_json
from scripts.corpus import pseudonym, racefile

if TYPE_CHECKING:
    from collections.abc import Callable

    from scripts._json import Json
    from scripts.corpus.pseudonym import Kind

# Setting keys legacy reads [код: pysport@b548c35 sportorg (grep get_setting/set_setting)] and the
# old names it migrates [код: pysport@b548c35 sportorg/modules/backup/json.py:105-118].
LEGACY_SETTINGS: Final = frozenset(
    {
        "credit_time_cp", "credit_time_enabled", "handicap_dsq_offset", "handicap_interval",
        "handicap_max_gap", "handicap_mode", "handicap_second_start", "handicap_start",
        "ignore_punches_before_start", "is_corridor_minute_number", "is_corridor_order_number",
        "is_fixed_number_interval", "is_fixed_start_interval", "is_mix_groups",
        "is_split_regions", "is_split_start_groups", "is_split_teams",
        "is_start_preparation_draw", "is_start_preparation_numbers",
        "is_start_preparation_reserve", "is_start_preparation_time", "live_cp_code",
        "live_cp_enabled", "live_cp_finish_enabled", "live_cp_split_codes",
        "live_cp_splits_enabled", "live_enabled", "live_results_enabled",
        "live_sending_all_controls", "marked_route_dont_dsq", "marked_route_if_counting_lap",
        "marked_route_if_station_check", "marked_route_max_penalty_by_cp", "marked_route_mode",
        "marked_route_penalty_lap_station_code", "marked_route_penalty_time", "numbers_first",
        "numbers_interval", "penalty_extra_cp", "print_margin_bottom", "print_margin_left",
        "print_margin_right", "print_margin_top", "punch_system", "readout_duplicate_timeout",
        "relay_next_number", "reserve_count", "reserve_percent", "reserve_prefix",
        "result_processing_fixed_score_value", "result_processing_mode",
        "result_processing_score_mode", "result_processing_scores_max_overrun_time",
        "result_processing_scores_minute_penalty", "score_formula", "score_list",
        "score_team_limit", "score_use_team_limit", "scores_array", "scores_formula",
        "scores_mode", "split_printout", "start_first_time", "start_interval",
        "start_one_minute_qty", "system_assign_chip_reading", "system_assignment_mode",
        "system_duplicate_chip_processing", "system_finish_cp_number", "system_finish_source",
        "system_missed_finish", "system_port", "system_start_cp_number", "system_start_source",
        "system_zero_time", "telegram_enabled", "telegram_parse_mode", "time_accuracy",
        "time_format_24", "time_rounding",
        "sportident_zero_time", "sportident_start_source", "sportident_start_cp_number",
        "sportident_finish_source", "sportident_finish_cp_number",
        "sportident_assign_chip_reading", "sportident_assignment_mode", "sportident_port",
    }
)  # fmt: skip
# Д1: live_urls, telegram_chat_id; by its addition (fields not in the list follow the same rules)
# the other ids, tokens and hosts of broadcasts, among them keys of older versions found in the
# corpus that legacy@b548c35 no longer reads (live_token, teamwork_token, teamwork_host).
CLEARED_SETTINGS: Final = frozenset(
    {
        "live_urls", "live_url", "live_token", "telegram_chat_id", "telegram_thread_id",
        "teamwork_token", "teamwork_host",
    }
)  # fmt: skip
TEXT_SETTINGS: Final = frozenset({"telegram_template", "split_template"})
PERSON_KEPT: Final = frozenset(
    {
        "object", "id", "bib", "year", "group_id", "organization_id", "qual",
        "is_out_of_competition", "is_paid", "is_rented_card", "is_personal", "start_time",
        "start_group", "sex", "is_rented_sportident_card",
    }
)  # fmt: skip
PERSON_TEXT: Final[dict[str, Kind]] = {
    "name": "person",
    "surname": "person",
    "middle_name": "person",
    "comment": "text",
}
RESULT_KEPT: Final = frozenset(
    {
        "object", "id", "bib", "system_type", "person_id", "days", "start_time", "finish_time",
        "diff", "diff_scores", "penalty_time", "credit_time", "status", "penalty_laps", "place",
        "assigned_rank", "splits", "card_battery_level", "speed", "scores", "rogaine_score",
        "rogaine_penalty", "scores_ardf", "created_at", "start_msec", "finish_msec",
        "result_msec", "result_relay_msec", "result_current_msec", "can_win_count",
        "final_result_time", "order",
    }
)  # fmt: skip
# strings legacy derives from the status comment on save and never reads
RESULT_SHOWN: Final = frozenset({"result", "result_relay", "result_current"})
MULTI_DAY: Final = "multi_day_results"
RESULT_DERIVED: Final = RESULT_SHOWN | {MULTI_DAY}
DAY_FIELD: Final = 14  # [код: pysport@b548c35 sportorg/models/memory.py:969-973]
# what legacy writes into ``result`` for a status other than OK without a comment: the status
# title, in English or translated [код: pysport@b548c35 sportorg/models/memory.py:45-53,74-93,
# 702-706; sportorg/data/languages/ru_RU/LC_MESSAGES/sportorg.po], checked by a test
LEGACY_STATUS_TITLES: Final = (
    "None", "Ok", "Finished", "Disqualified", "Missing punch", "Did not finish", "Active",
    "Inactive", "Overtime", "Sporting withdrawal", "Not competing", "Moved", "Moved up",
    "Did not start", "Did not enter", "Cancelled", "Restored", "Miss penalty lap",
    "Multi day issue",
    "-", "Оk", "Финишировал", "ДИСКВ.", "Непр. отметка", "СОШЕЛ", "Активный", "Неактивный",
    "ПРЕВЫШЕНО КВ", "Проведена жеребьевка", "Вне конкурса", "Перемещен", "Перемещен наверх",
    "НЕ СТАРТ.", "Не заявлен", "Заявка отменена", "Восстановлен", "Пропущен штрафной круг",
    "Не все дни",
)  # fmt: skip
# the hints legacy offers after a rule clause, normalized
# [код: pysport@b548c35 sportorg/data/configs/status_comments.txt:1-21]
LEGACY_HINTS: Final = frozenset(
    pseudonym.normalize(hint)
    for hint in (
        "нарушение порядка прохождения КП",
        "непрохождение имеющихся на трассе обозначенных участков",
        "не произвел считывание информации на финише",
        "получил преимущество в занятом месте от неаккуратной отметки",
        "контрольная карточка показывает, что нарушил заданный порядок прохождения КП",
        "не сдал на финише контрольную карточку",
        "спортсмен покинул зону изоляции до установленного времени",
        (
            "тренер или специалист, работающий с командой, покинул зону изоляции до "
            "установленного времени"
        ),
        "не начал прохождение трассы по ВБ с начального КП",
        "не прошел через последний (финишный) обязательный КП",
        "взял меньшее число КП, чем задано для возрастной категории",
        "не прошел назначенное число штрафных кругов",
        "хотя бы одна отметка на базовом КП отсутствует (МТ вариант А)",
        "хотя бы одна отметка на базовом КП отсутствует (МТ вариант Б)",
        (
            "хотя бы одна отметка крестом соответствующего цвета или специальным компостером "
            "отсутствует"
        ),
        "отсутствует отметка хотя бы на одной ТПР",
        "отсутствует отметка хотя бы одного истинного КП",
        "превышение контрольного времени",
        "нарушение целостности защиты оборотной стороны спортивной карты",
        "спортсмен сошел с трассы",
        "спортсмен не стартовал",
    )
)
# ``п.п.6.6.4``, ``пп6.6.4``, ``п. п. 6.6.4`` [мейнтейнер: 2026-11-01]
_CLAUSE = re.compile(r"п\.?\s?п\.?\s?\d+(?:\.\d+)*\.?", re.IGNORECASE)
_TIME_FIELD = re.compile(r"[\d:.,]*")
ORG_KEPT: Final = frozenset({"object", "id", "count_person", "count_finished", "sex"})
ORG_TEXT: Final[dict[str, Kind]] = {
    "name": "org",
    "country": "place",
    "region": "place",
    "address": "place",
    "contact": "contact",
    "code": "code",
}
DATA_NEUTRAL: Final = frozenset({"title", "short_title", "description", "location", "url"})
DATA_PERSON: Final = frozenset({"chief_referee", "secretary"})
DATA_KEPT: Final = frozenset({"race_type", "start_datetime", "end_datetime", "relay_leg_count"})
RACE_KEPT: Final = frozenset({"object", "id", "groups", "courses"})
FILE_KEPT: Final = frozenset({"version", "current_race"})
CARD_KEYS: Final = frozenset({"card_number", "sportident_card"})
CODE_KEYS: Final = frozenset({"world_code", "national_code"})
_IDENTIFIER = re.compile(r"[a-z_][a-z0-9_]{0,40}")
_ISO_DATE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")
_ASCII_DIGITS = re.compile(r"[0-9]+")


def status_comment_free_text(value: str, *, cut: bool = False) -> str | None:
    """The part of a status comment to mask: ``None`` (a rule clause), the hint, or all of it.

    ``cut``: ``value`` is a day field of ``multi_day_results``, so a hint may be cut short.
    """
    clause, sharp, hint = value.partition("#")
    if not value.strip():
        return None
    if not _CLAUSE.fullmatch(clause.strip()):
        return value
    if not sharp or not hint.strip():
        return None
    known = pseudonym.normalize(hint)
    if known in LEGACY_HINTS or (cut and any(h.startswith(known) for h in LEGACY_HINTS)):
        return None
    return hint


def status_comment(key: bytes, value: str, *, cut: bool = False) -> tuple[str, str]:
    """``(new value, outcome)``; outcome ``kept``, ``hint`` (clause kept) or ``masked``."""
    free = status_comment_free_text(value, cut=cut)
    if free is None:
        return value, "kept"
    if free == value:
        return pseudonym.pseudonym(key, "text", value), "masked"
    clause = value.partition("#")[0]
    return f"{clause}# {pseudonym.pseudonym(key, 'text', free.strip())}", "hint"


class _Unowned:
    """What a ``handle`` returns for a key its object does not know (``None`` is a value)."""


_UNOWNED: Final = _Unowned()


@dataclass(frozen=True, slots=True)
class Anonymized:
    doc: Json
    stats: Counter[str] = field(default_factory=Counter[str])


def _empty_like(value: Json) -> Json:
    if isinstance(value, list):
        return []
    if isinstance(value, dict):
        return {}
    if isinstance(value, str):
        return ""
    return None


class _Masker:
    def __init__(self, key: bytes, neutral_id: str) -> None:
        self.key: bytes = key
        self.neutral_id: str = neutral_id
        self.stats: Counter[str] = Counter()

    # ------------------------------------------------------------ values

    def deep(self, kind: Kind, value: Json) -> Json:
        """Every string inside ``value`` as a pseudonym; keys, numbers and nulls kept."""
        if isinstance(value, str):
            return pseudonym.pseudonym(self.key, kind, value)
        if isinstance(value, list):
            return [self.deep(kind, item) for item in value]
        if isinstance(value, dict):
            return {k: self.deep(kind, v) for k, v in value.items()}
        return value

    def card(self, value: Json) -> Json:
        """Another number in the shape legacy reads (``int(value)``); any other shape → 0."""
        if isinstance(value, bool) or value is None or value == "":
            return value
        if isinstance(value, int):
            return pseudonym.card_number(self.key, value)
        if isinstance(value, float) and value.is_integer():
            return float(pseudonym.card_number(self.key, int(value)))
        if isinstance(value, str) and _ASCII_DIGITS.fullmatch(value.strip()):
            return str(pseudonym.card_number(self.key, int(value)))
        self.stats["unparsed:card_number"] += 1
        return 0

    def code(self, value: Json) -> Json:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return pseudonym.number_code(self.key, value)
        return self.deep("code", value)

    def birth(self, person: dict[str, Json], out: dict[str, Json]) -> None:
        """``birth_date`` moved within its year; ``birthday`` (written, never read) follows it."""
        value = person.get("birth_date")
        new: str | None = None
        if isinstance(value, str) and value:
            new = pseudonym.birth_date(self.key, value)
            self.stats["mask:person.birth_date"] += 1
        if value not in (None, "") and new is None:
            self.stats["unparsed:birth_date"] += 1
        if "birth_date" in person:
            out["birth_date"] = new if value not in (None, "") else value
        if "birthday" in person:
            match = _ISO_DATE.match(new or "")
            out["birthday"] = f"{match[3]}.{match[2]}.{match[1]}" if match else ""
            self.stats["mask:person.birthday"] += 1

    def unknown(self, where: str, name: str, value: Json) -> Json:
        label = name if _IDENTIFIER.fullmatch(name) else "(other)"
        self.stats[f"unknown:{where}.{label}"] += 1
        return self.deep("text", value)

    # ------------------------------------------------------------ objects

    def _fields(
        self,
        where: str,
        item: Json,
        kept: frozenset[str],
        handle: Callable[[str, Json], Json | _Unowned],
    ) -> dict[str, Json]:
        """``handle(key, value)``: the masked value, or ``_UNOWNED`` for a key it does not own."""
        out: dict[str, Json] = {}
        for name, value in as_dict(item).items():
            if name in kept:
                out[name] = value
                continue
            masked = handle(name, value)
            out[name] = self.unknown(where, name, value) if isinstance(masked, _Unowned) else masked
        return out

    def person(self, item: Json) -> Json:
        def handle(name: str, value: Json) -> Json | _Unowned:
            if name in PERSON_TEXT:
                self.stats[f"mask:person.{name}"] += 1
                return self.deep(PERSON_TEXT[name], value)
            if name in CARD_KEYS:
                self.stats[f"mask:person.{name}"] += 1
                return self.card(value)
            if name in CODE_KEYS:
                self.stats[f"mask:person.{name}"] += 1
                return self.code(value)
            if name in {"birth_date", "birthday"}:
                return value  # replaced by ``birth`` below
            return _UNOWNED

        out = self._fields("person", item, PERSON_KEPT, handle)
        self.birth(as_dict(item), out)
        return out

    def day_field(self, field: str) -> str:
        text = field.rstrip(" ")
        if _TIME_FIELD.fullmatch(text):
            return field
        new, outcome = status_comment(self.key, text, cut=True)
        return field if outcome == "kept" else f"{new}{' ' * DAY_FIELD}"[:DAY_FIELD]

    def derived(self, name: str, value: Json, comment: tuple[str, str] | None) -> Json:
        if not isinstance(value, str):
            return value
        if name == MULTI_DAY:
            fields = (value[i : i + DAY_FIELD] for i in range(0, len(value), DAY_FIELD))
            new = "".join(self.day_field(field) for field in fields)
        else:
            new = comment[1] if comment and value == comment[0] else value
        if new != value:
            self.stats[f"mask:result.{name}"] += 1
        return new

    def result(self, item: Json) -> Json:
        original = as_dict(item).get("status_comment")
        comment: tuple[str, str] | None = None
        if isinstance(original, str) and original.strip():
            new, outcome = status_comment(self.key, original)
            prefix = "kept" if outcome == "kept" else "mask"
            suffix = "_hint" if outcome == "hint" else ""
            self.stats[f"{prefix}:result.status_comment{suffix}"] += 1
            comment = (original, new)

        def handle(name: str, value: Json) -> Json | _Unowned:
            if name in CARD_KEYS:
                self.stats[f"mask:result.{name}"] += 1
                return self.card(value)
            if name == "status_comment":
                return comment[1] if comment else self.deep("text", value)
            if name in RESULT_DERIVED:
                return self.derived(name, value, comment)
            return _UNOWNED

        return self._fields("result", item, RESULT_KEPT, handle)

    def organization(self, item: Json) -> Json:
        def handle(name: str, value: Json) -> Json | _Unowned:
            if name not in ORG_TEXT:
                return _UNOWNED
            self.stats[f"mask:organization.{name}"] += 1
            return self.deep(ORG_TEXT[name], value)

        return self._fields("organization", item, ORG_KEPT, handle)

    def data(self, item: Json, index: int) -> Json:
        def handle(name: str, value: Json) -> Json | _Unowned:
            if name in DATA_NEUTRAL:
                self.stats[f"mask:data.{name}"] += 1
                return f"{self.neutral_id}/{index}" if value else value
            if name in DATA_PERSON:
                self.stats[f"mask:data.{name}"] += 1
                return self.deep("person", value)
            return _UNOWNED

        return self._fields("data", item, DATA_KEPT, handle)

    def settings(self, item: Json) -> Json:
        def handle(name: str, value: Json) -> Json | _Unowned:
            if name in CLEARED_SETTINGS:
                self.stats[f"clear:settings.{name}"] += 1
                return _empty_like(value)
            if name in TEXT_SETTINGS:
                self.stats[f"mask:settings.{name}"] += 1
                return self.deep("text", value)
            return _UNOWNED

        return self._fields("settings", item, LEGACY_SETTINGS, handle)

    def race(self, item: Json, index: int) -> Json:
        lists: dict[str, Callable[[Json], Json]] = {
            "persons": self.person,
            "results": self.result,
            "organizations": self.organization,
        }

        def handle(name: str, value: Json) -> Json | _Unowned:
            if name in lists:
                return [lists[name](entry) for entry in as_list(value)]
            if name == "data":
                return self.data(value, index)
            if name == "settings":
                return self.settings(value)
            return _UNOWNED

        return self._fields("race", item, RACE_KEPT, handle)

    def file(self, doc: Json) -> Json:
        if isinstance(doc, list):
            return [self.race(item, i) for i, item in enumerate(doc)]
        if "races" not in as_dict(doc):
            return self.race(doc, 0)

        def handle(name: str, value: Json) -> Json | _Unowned:
            if name == "races":
                return [self.race(item, i) for i, item in enumerate(as_list(value))]
            return _UNOWNED

        return self._fields("file", doc, FILE_KEPT, handle)


def anonymize(doc: Json, *, key: bytes, neutral_id: str) -> Anonymized:
    """A new document; ``doc`` is not changed."""
    masker = _Masker(key, neutral_id)
    return Anonymized(masker.file(doc), masker.stats)


def anonymize_bytes(raw: bytes, *, key: bytes, neutral_id: str) -> tuple[bytes, str, Counter[str]]:
    """Anonymized bytes of a race file in its own format (gzip, UTF-8 or cp1251)."""
    text, fmt = racefile.decode(raw)
    result = anonymize(parse_json(text), key=key, neutral_id=neutral_id)
    return racefile.encode(racefile.dumps(result.doc), fmt), fmt, result.stats
