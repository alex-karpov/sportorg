"""Tests for scripts/corpus/anonymize.py: Д1 on one race file, by field (Stage 2 S3).

The invariant (the oracle gives the same results before and after) is in test_invariant.py; here
each field is checked against the rule of Д1 and its addition of 2026-10-31.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

import pytest

from scripts._json import as_dict, as_list, as_str
from scripts.corpus import anonymize, pseudonym, racefile, synth
from scripts.legacy import legacy_dir

if TYPE_CHECKING:
    from collections import Counter

    from scripts._json import Json

KEY = b"synthetic test key, not the corpus key"
NEUTRAL = "S00-0123456789ab"


def _run(doc: Json) -> anonymize.Anonymized:
    return anonymize.anonymize(doc, key=KEY, neutral_id=NEUTRAL)


def _race(doc: Json, index: int = 0) -> dict[str, Json]:
    return as_dict(racefile.races_of(doc)[index])


def _items(race: dict[str, Json], key: str) -> list[dict[str, Json]]:
    return [as_dict(item) for item in as_list(race[key])]


@pytest.fixture
def individual() -> tuple[dict[str, Json], dict[str, Json]]:
    doc = synth.personal_individual()
    return _race(doc), _race(_run(doc).doc)


def test_names_become_person_pseudonyms(
    individual: tuple[dict[str, Json], dict[str, Json]],
) -> None:
    before, after = individual
    for old, new in zip(_items(before, "persons"), _items(after, "persons"), strict=True):
        for field in ("name", "surname", "middle_name"):
            assert new[field] == pseudonym.pseudonym(KEY, "person", as_str(old[field]))


def test_empty_values_stay_empty(individual: tuple[dict[str, Json], dict[str, Json]]) -> None:
    before, after = individual
    for old, new in zip(_items(before, "persons"), _items(after, "persons"), strict=True):
        for field in ("middle_name", "comment", "world_code"):
            assert (new[field] == "") is (old[field] == "")


def test_cards_are_renumbered_alike_in_persons_and_results(
    individual: tuple[dict[str, Json], dict[str, Json]],
) -> None:
    before, after = individual
    pairs = [
        *zip(_items(before, "persons"), _items(after, "persons"), strict=True),
        *zip(_items(before, "results"), _items(after, "results"), strict=True),
    ]
    for old, new in pairs:
        card = old["card_number"]
        assert isinstance(card, int)
        assert new["card_number"] == pseudonym.card_number(KEY, card)


def test_birth_dates_keep_the_year_and_move_the_day(
    individual: tuple[dict[str, Json], dict[str, Json]],
) -> None:
    before, after = individual
    for old, new in zip(_items(before, "persons"), _items(after, "persons"), strict=True):
        if old["birth_date"] is None:
            assert new["birth_date"] is None
            continue
        assert new["birth_date"] == pseudonym.birth_date(KEY, as_str(old["birth_date"]))
        assert new.get("year") == old.get("year")


def test_birthday_follows_the_new_birth_date() -> None:
    doc = synth.personal_individual()
    person = _items(_race(doc), "persons")[0]
    person["birth_date"], person["birthday"] = "1990-05-17", "17.05.1990"
    new = _items(_race(_run(doc).doc), "persons")[0]
    year, month, day = as_str(new["birth_date"]).split("-")
    assert new["birthday"] == f"{day}.{month}.{year}"


def test_what_the_recalculation_reads_is_kept(
    individual: tuple[dict[str, Json], dict[str, Json]],
) -> None:
    before, after = individual
    for key in ("id", "groups", "courses"):
        assert after[key] == before[key]
    for old, new in zip(_items(before, "results"), _items(after, "results"), strict=True):
        assert {
            k: v
            for k, v in new.items()
            if k not in {"card_number", "status_comment", "operator_note"}
        } == {
            k: v
            for k, v in old.items()
            if k not in {"card_number", "status_comment", "operator_note"}
        }
    for old, new in zip(_items(before, "persons"), _items(after, "persons"), strict=True):
        for key in (
            "id",
            "bib",
            "group_id",
            "organization_id",
            "start_time",
            "is_out_of_competition",
        ):
            assert new[key] == old[key]


def test_race_titles_become_the_neutral_id_and_referees_pseudonyms(
    individual: tuple[dict[str, Json], dict[str, Json]],
) -> None:
    before, after = individual
    old, new = as_dict(before["data"]), as_dict(after["data"])
    for field in ("title", "short_title", "description", "location", "url"):
        assert new[field] == f"{NEUTRAL}/0"
    for field in ("chief_referee", "secretary"):
        assert new[field] == pseudonym.pseudonym(KEY, "person", as_str(old[field]))
    assert new["race_type"] == old["race_type"]


def test_settings_secrets_cleared_texts_masked_and_rules_kept(
    individual: tuple[dict[str, Json], dict[str, Json]],
) -> None:
    before, after = individual
    old, new = as_dict(before["settings"]), as_dict(after["settings"])
    assert new["live_urls"] == []
    assert new["live_url"] == new["telegram_chat_id"] == new["telegram_thread_id"] == ""
    for field in ("telegram_template", "split_template", "operator_note"):
        assert new[field] == pseudonym.pseudonym(KEY, "text", as_str(old[field]))
    assert new["time_rounding"] == old["time_rounding"]
    assert new["time_accuracy"] == old["time_accuracy"]


def test_organizations(individual: tuple[dict[str, Json], dict[str, Json]]) -> None:
    before, after = individual
    for old, new in zip(
        _items(before, "organizations"), _items(after, "organizations"), strict=True
    ):
        assert new["id"] == old["id"]
        assert new["name"] == pseudonym.pseudonym(KEY, "org", as_str(old["name"]))
        for field in ("country", "region"):
            assert new[field] == pseudonym.pseudonym(KEY, "place", as_str(old[field]))
        assert new["contact"] == pseudonym.pseudonym(KEY, "contact", as_str(old["contact"]))
        assert new["code"] == pseudonym.pseudonym(KEY, "code", as_str(old["code"]))


def test_identifiers_comments_and_status_comments(
    individual: tuple[dict[str, Json], dict[str, Json]],
) -> None:
    before, after = individual
    persons = list(zip(_items(before, "persons"), _items(after, "persons"), strict=True))
    old, new = persons[0]
    assert new["world_code"] == pseudonym.pseudonym(KEY, "code", as_str(old["world_code"]))
    assert new["comment"] == pseudonym.pseudonym(KEY, "text", as_str(old["comment"]))
    old, new = persons[1]
    assert new["national_code"] == pseudonym.number_code(KEY, 1_234_567)
    old, new = persons[2]
    assert new["national_code"] == pseudonym.pseudonym(KEY, "code", "NC-77")
    results = list(zip(_items(before, "results"), _items(after, "results"), strict=True))
    old, new = next((o, n) for o, n in results if o["status_comment"])
    assert new["status_comment"] == pseudonym.pseudonym(KEY, "text", as_str(old["status_comment"]))


def test_unknown_keys_are_masked_deep_and_counted(
    individual: tuple[dict[str, Json], dict[str, Json]],
) -> None:
    before, after = individual
    old, new = _items(before, "persons")[0], _items(after, "persons")[0]
    contact = as_dict(as_list(new["contact"])[0])
    assert contact["value"] == pseudonym.pseudonym(KEY, "text", "+7 000 000-00-08")
    assert set(contact) == set(as_dict(as_list(old["contact"])[0]))
    stats = _run(synth.personal_individual()).stats
    assert stats["unknown:person.contact"] == 1
    assert stats["unknown:result.operator_note"] == 1
    assert stats["unknown:settings.operator_note"] == 1


def test_unknown_key_names_that_are_not_identifiers_are_not_reported() -> None:
    doc = synth.personal_individual()
    _items(_race(doc), "persons")[0]["Выдумкин"] = "x"
    stats = _run(doc).stats
    assert "unknown:person.(other)" in stats
    assert not any("Выдумкин" in name for name in stats)


def test_old_format_is_masked_in_its_own_shape() -> None:
    before = as_dict(synth.personal_old_format())
    after = as_dict(_run(before).doc)
    assert "races" not in after
    old_person, new_person = _items(before, "persons")[0], _items(after, "persons")[0]
    card = old_person["sportident_card"]
    assert isinstance(card, int)
    assert new_person["sportident_card"] == pseudonym.card_number(KEY, card)
    assert "card_number" not in new_person
    assert _items(after, "results")[0]["sportident_card"] == pseudonym.card_number(KEY, card)
    org = _items(after, "organizations")[0]
    address, contact = as_dict(org["address"]), as_dict(org["contact"])
    assert as_dict(address["country"])["name"] == pseudonym.pseudonym(
        KEY, "place", "Выдуманная страна"
    )
    assert address["state"] == pseudonym.pseudonym(KEY, "place", "Небывальская область")
    assert contact["value"] == pseudonym.pseudonym(KEY, "contact", "+7 000 000-00-03")
    assert as_dict(after["settings"])["sportident_port"] == "COM3"


def test_input_is_not_changed() -> None:
    doc = synth.personal_individual()
    kept = copy.deepcopy(doc)
    _run(doc)
    assert doc == kept


def test_anonymization_is_reproducible() -> None:
    assert racefile.dumps(_run(synth.personal_multi_day()).doc) == racefile.dumps(
        _run(synth.personal_multi_day()).doc
    )


def test_locality_one_changed_record_leaves_the_others_as_before() -> None:
    """Locality (2) [мейнтейнер: 2026-11-01]: edit one person and its result, nothing else moves."""
    doc = synth.personal_individual()
    changed = copy.deepcopy(doc)
    race = _race(changed)
    person = _items(race, "persons")[3]
    person["surname"], person["card_number"], person["birth_date"] = (
        "Придумкин",
        8_000_001,
        "1980-01-02",
    )
    _items(race, "results")[3]["card_number"] = 8_000_001
    first, second = _race(_run(doc).doc), _race(_run(changed).doc)
    for key in ("persons", "results", "organizations"):
        old, new = _items(first, key), _items(second, key)
        assert [o for i, o in enumerate(old) if i != 3] == [n for i, n in enumerate(new) if i != 3]
    assert _items(first, "persons")[3] != _items(second, "persons")[3]


def test_text_round_trip_keeps_the_format() -> None:
    text = synth.dumps(synth.personal_individual())
    raw = racefile.encode(text, "cp1251")
    out, fmt, stats = anonymize.anonymize_bytes(raw, key=KEY, neutral_id=NEUTRAL)
    assert fmt == "cp1251"
    assert racefile.decode(out)[1] == "cp1251"
    assert stats["mask:person.surname"] == 10


def test_old_tokens_and_hosts_of_the_settings_are_cleared() -> None:
    """Found in the corpus as keys legacy@b548c35 no longer reads; cleared as ``live_urls`` is."""
    doc = synth.personal_individual()
    settings = as_dict(_race(doc)["settings"])
    settings |= {"live_token": "t0k3n", "teamwork_token": "t0k3n", "teamwork_host": "10.0.0.1"}
    settings["teamwork_port"] = 50010
    new = as_dict(_race(_run(doc).doc)["settings"])
    assert new["live_token"] == new["teamwork_token"] == new["teamwork_host"] == ""
    assert new["teamwork_port"] == 50010


# ---------------------------------------------------------------- status comments (C1, в)


@pytest.mark.parametrize(
    "comment",
    [
        "п.п.6.6.4",
        "пп6.6.4",
        "П.п. 3.13.12.2",
        "пп3.13.12.2 # нарушение порядка прохождения КП",
        "пп6.6.4 # спортсмен сошёл с трассы",
        "",
    ],
)
def test_a_rule_clause_status_comment_is_kept(comment: str) -> None:
    assert anonymize.status_comment(KEY, comment) == (comment, "kept")


@pytest.mark.parametrize(
    "comment", ["Снят по протесту Выдумкина", "6.6.4", "п.п.6.6.4, 3.4.6", "п.п. по протесту"]
)
def test_any_other_status_comment_is_masked(comment: str) -> None:
    masked = pseudonym.pseudonym(KEY, "text", comment)
    assert anonymize.status_comment(KEY, comment) == (masked, "masked")


def test_a_free_hint_after_a_rule_clause_is_masked_and_the_clause_kept() -> None:
    new, outcome = anonymize.status_comment(KEY, "п.п.5.4.7 # Ежиков ждал Небывалову")
    assert outcome == "hint"
    assert new == "п.п.5.4.7 # " + pseudonym.pseudonym(KEY, "text", "Ежиков ждал Небывалову")


def _shape_results() -> list[tuple[dict[str, Json], dict[str, Json]]]:
    doc = synth.personal_legacy_shape()
    out = _run(doc).doc
    pairs: list[tuple[dict[str, Json], dict[str, Json]]] = []
    for index in (0, 1):
        pairs += zip(
            _items(_race(doc, index), "results"), _items(_race(out, index), "results"), strict=True
        )
    return pairs


DERIVED = ("result", "result_relay", "result_current")


def test_a_masked_status_comment_is_masked_in_the_derived_result_strings() -> None:
    old, new = next(
        p for p in _shape_results() if p[0]["status_comment"] == synth.SHAPE_PEOPLE[1][3][1]
    )
    masked = pseudonym.pseudonym(KEY, "text", as_str(old["status_comment"]))
    assert new["status_comment"] == masked
    assert [new[key] for key in DERIVED] == [masked] * 3


def test_kept_comments_and_times_stay_in_the_derived_result_strings() -> None:
    for old, new in _shape_results():
        if old["status_comment"] in {"", "п.п.6.6.4", "пп6.6.4 # спортсмен сошёл с трассы"}:
            assert [new[key] for key in DERIVED] == [old[key] for key in DERIVED]


def test_multi_day_results_mask_each_day_field_that_is_not_kept() -> None:
    field = synth.DAY_FIELD
    for old, new in _shape_results():
        before, after = as_str(old["multi_day_results"]), as_str(new["multi_day_results"])
        assert len(after) == len(before)
        for day in range(len(before) // field):
            was, now = (
                before[day * field : (day + 1) * field],
                after[day * field : (day + 1) * field],
            )
            if was.startswith(("Снят", "п.п.5.4.7 # Еж")):
                assert now != was
                assert now.startswith(("T", "п.п.5.4.7 # T"))
            else:
                assert now == was


def test_status_comments_are_counted_by_outcome() -> None:
    stats = _run(synth.personal_legacy_shape()).stats
    assert stats["kept:result.status_comment"] == 3
    assert stats["mask:result.status_comment"] == 1
    assert stats["mask:result.status_comment_hint"] == 1
    assert stats["mask:result.result"] == 2


HINTS_FILE = legacy_dir() / "pysport" / "sportorg" / "data" / "configs" / "status_comments.txt"


@pytest.mark.skipif(not HINTS_FILE.exists(), reason="legacy not fetched: scripts.legacy fetch")
def test_the_kept_hints_are_legacys_own() -> None:
    lines = HINTS_FILE.read_text(encoding="utf-8").splitlines()
    hints = {pseudonym.normalize(line.partition("#")[2]) for line in lines if "#" in line}
    assert hints == anonymize.LEGACY_HINTS


# ---------------------------------------------------------------- other shapes (I2)


def _shaped(field: str, value: Json, index: int = 1) -> tuple[dict[str, Json], Counter[str]]:
    doc = synth.personal_individual()
    person = _items(_race(doc), "persons")[index]
    if value is None:
        person.pop(field)
    else:
        person[field] = value
    result = _run(doc)
    return _items(_race(result.doc), "persons")[index], result.stats


def test_a_card_written_as_a_float_is_renumbered_as_a_float() -> None:
    new, _ = _shaped("card_number", 212_345.0)
    assert new["card_number"] == float(pseudonym.card_number(KEY, 212_345))


@pytest.mark.parametrize("card", ["212 345", "²", 212_345.5, "C212345"])
def test_a_card_in_a_shape_legacy_cannot_read_becomes_zero(card: Json) -> None:
    new, stats = _shaped("card_number", card)
    assert new["card_number"] == 0
    assert stats["unparsed:card_number"] == 1


def test_a_birth_date_that_is_not_a_string_is_dropped() -> None:
    new, stats = _shaped("birth_date", 19_900_517)
    assert new["birth_date"] is None
    assert stats["unparsed:birth_date"] == 1


@pytest.mark.parametrize("birth_date", ["", None])
def test_birthday_is_blanked_without_a_birth_date(birth_date: str | None) -> None:
    doc = synth.personal_individual()
    person = _items(_race(doc), "persons")[1]
    person["birthday"] = "17.05.1990"
    if birth_date is None:
        person.pop("birth_date")
    else:
        person["birth_date"] = birth_date
    new = _items(_race(_run(doc).doc), "persons")[1]
    assert new["birthday"] == ""


def test_every_masked_field_is_counted() -> None:
    stats = _run(synth.personal_individual()).stats
    assert stats["mask:organization.name"] == 2
    assert stats["mask:organization.region"] == 2
    assert stats["mask:data.title"] == 1
    assert stats["mask:data.chief_referee"] == 1
    assert stats["mask:settings.telegram_template"] == 1
    assert stats["clear:settings.live_urls"] == 1
    assert stats["mask:person.card_number"] == 10
    assert stats["mask:result.card_number"] == 10
    assert stats["mask:person.world_code"] == 10


LEGACY_SOURCE = legacy_dir() / "pysport" / "sportorg"


@pytest.mark.skipif(not LEGACY_SOURCE.exists(), reason="legacy not fetched: scripts.legacy fetch")
def test_the_status_titles_are_legacys_own() -> None:
    models = (LEGACY_SOURCE / "models" / "memory.py").read_text(encoding="utf-8")
    block = models.split("class ResultStatus(_TitleType):\n", 1)[1].split("\n\n", 1)[0]
    names = [line.split("=")[0].strip() for line in block.splitlines() if "=" in line]
    english = [name.lower().capitalize().replace("_", " ") for name in names]
    po = LEGACY_SOURCE / "data" / "languages" / "ru_RU" / "LC_MESSAGES" / "sportorg.po"
    text = po.read_text(encoding="utf-8")
    russian = [text.split(f'msgid "{t}"\nmsgstr "', 1)[1].split('"', 1)[0] for t in english]
    assert set(anonymize.LEGACY_STATUS_TITLES) == set(english) | set(russian)


# ---------------------------------------------------------------- fix pass after the re-review


def _day_field_after(comment: str) -> str:
    """Day 2 of a multi-day result whose status comment (and day field) is ``comment``."""
    doc = synth.personal_legacy_shape()
    result = _items(_race(doc, 1), "results")[1]
    result["status_comment"] = comment
    result["multi_day_results"] = "0:31:00       " + f"{comment:<14}"[:14]
    new = _items(_race(_run(doc).doc, 1), "results")[1]
    return as_str(new["multi_day_results"])[synth.DAY_FIELD :]


@pytest.mark.parametrize("comment", ["89001234567", "01.02.1990", "500,123", "١٢٣٤٥", "12:34"])
def test_a_status_comment_of_digits_is_masked_in_the_day_field(comment: str) -> None:
    assert comment not in _day_field_after(comment)


@pytest.mark.parametrize("time", ["0:31:00", "10:31:00.5", "1:02:03,25", ""])
def test_a_time_stays_in_the_day_field(time: str) -> None:
    assert _day_field_after(time).rstrip(" ") == time


def test_a_numeric_code_written_as_a_float_is_renumbered_as_a_float() -> None:
    new, _ = _shaped("national_code", 1_234_567.0)
    assert new["national_code"] == float(pseudonym.number_code(KEY, 1_234_567))


@pytest.mark.parametrize("comment", ["пп 12345678", "п.п.89001234567", "пп1234"])
def test_a_long_digit_run_is_not_a_rule_clause(comment: str) -> None:
    assert anonymize.status_comment(KEY, comment)[1] == "masked"


@pytest.mark.parametrize(
    "comment", ["пп8.900.123.45.67", "п.п.123.456.789", "пп 8.123.456", "пп1.2.3.4.5.6"]
)
def test_a_dotted_number_that_is_not_a_clause_of_the_rules_is_masked(comment: str) -> None:
    assert anonymize.status_comment(KEY, comment)[1] == "masked"


@pytest.mark.parametrize("comment", ["п.п.4.6.12.7", "п.п.3.13.12.2", "пп4.3.6.6"])
def test_the_clauses_legacy_offers_are_kept(comment: str) -> None:
    assert anonymize.status_comment(KEY, comment)[1] == "kept"
