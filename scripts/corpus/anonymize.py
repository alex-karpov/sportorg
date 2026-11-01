"""Anonymize one race file by Д1 (Stage 2 S3, TASK-8 AC #2).

Д1 (а) with the additions of ``[мейнтейнер: 2026-10-31]``, field by field (legacy ``to_dict`` /
``update_data`` [код: pysport@b548c35 sportorg/models/memory.py:96-137,601-700,1424-1477,
1615-1643], old field names [код: pysport@b548c35 sportorg/modules/backup/json.py:84-118]):

- person: ``surname``, ``name``, ``middle_name`` → person pseudonyms; ``comment`` → text;
  ``world_code``, ``national_code`` → code pseudonyms (a number stays a number with as many
  digits), empty stays empty; ``card_number`` and the old ``sportident_card`` → another number of
  the same card type; ``birth_date`` → another day of the same year (``birthday`` follows it);
  ``year`` kept.
- result: ``card_number``/``sportident_card`` as for persons; ``status_comment`` → text.
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
        "rogaine_penalty", "scores_ardf", "created_at", "result", "result_relay",
        "result_current", "start_msec", "finish_msec", "result_msec", "result_relay_msec",
        "result_current_msec", "can_win_count", "final_result_time", "order",
        "multi_day_results",
    }
)  # fmt: skip
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
_ISO_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


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
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return pseudonym.card_number(self.key, value)
        if isinstance(value, str) and value.strip().isdigit():
            return str(pseudonym.card_number(self.key, int(value)))
        if value not in (None, ""):
            self.stats["unparsed:card_number"] += 1
        return value

    def code(self, value: Json) -> Json:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return pseudonym.number_code(self.key, value)
        return self.deep("code", value)

    def birth(self, person: dict[str, Json], out: dict[str, Json]) -> None:
        value = person.get("birth_date")
        if not isinstance(value, str) or not value:
            return
        new = pseudonym.birth_date(self.key, value)
        if new is None:
            self.stats["unparsed:birth_date"] += 1
        out["birth_date"] = new
        if "birthday" in person:
            match = _ISO_DATE.match(new or "")
            out["birthday"] = f"{match[3]}.{match[2]}.{match[1]}" if match else ""
        self.stats["mask:person.birth_date"] += 1

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
                return self.card(value)
            if name in CODE_KEYS:
                return self.code(value)
            if name in {"birth_date", "birthday"}:
                return value  # replaced by ``birth`` below
            return _UNOWNED

        out = self._fields("person", item, PERSON_KEPT, handle)
        self.birth(as_dict(item), out)
        return out

    def result(self, item: Json) -> Json:
        def handle(name: str, value: Json) -> Json | _Unowned:
            if name in CARD_KEYS:
                return self.card(value)
            if name == "status_comment":
                return self.deep("text", value)
            return _UNOWNED

        return self._fields("result", item, RESULT_KEPT, handle)

    def organization(self, item: Json) -> Json:
        def handle(name: str, value: Json) -> Json | _Unowned:
            return self.deep(ORG_TEXT[name], value) if name in ORG_TEXT else _UNOWNED

        return self._fields("organization", item, ORG_KEPT, handle)

    def data(self, item: Json, index: int) -> Json:
        def handle(name: str, value: Json) -> Json | _Unowned:
            if name in DATA_NEUTRAL:
                return f"{self.neutral_id}/{index}" if value else value
            if name in DATA_PERSON:
                return self.deep("person", value)
            return _UNOWNED

        return self._fields("data", item, DATA_KEPT, handle)

    def settings(self, item: Json) -> Json:
        def handle(name: str, value: Json) -> Json | _Unowned:
            if name in CLEARED_SETTINGS:
                return _empty_like(value)
            if name in TEXT_SETTINGS:
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
