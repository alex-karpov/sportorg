"""Tests for the synthetic races with fictional personal data (``synth.PERSONAL``, Stage 2 S3).

They feed the anonymization tests and the invariant: every field of Д1 is filled with an invented
value, card numbers fall into several card types, a multi-day event spells some names differently
on different days, and one file has the old format without ``races``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts._json import as_dict, as_int, as_list, as_str
from scripts.corpus import pseudonym, racefile, synth
from tests.scripts.oracle.test_synth import REQUIRED

if TYPE_CHECKING:
    from pathlib import Path

    from scripts._json import Json

MODERN = [name for name in synth.PERSONAL if name != "personal_old_format"]


def _races(name: str) -> list[dict[str, Json]]:
    return [as_dict(r) for r in racefile.races_of(synth.PERSONAL[name]())]


@pytest.mark.parametrize("name", MODERN)
def test_personal_races_have_the_keys_legacy_requires(name: str) -> None:
    for race in _races(name):
        assert REQUIRED["race"] <= race.keys()
        assert REQUIRED["data"] <= as_dict(race["data"]).keys()
        for person in map(as_dict, as_list(race["persons"])):
            assert REQUIRED["person"] <= person.keys()
        for result in map(as_dict, as_list(race["results"])):
            assert REQUIRED["result"] <= result.keys()


@pytest.mark.parametrize("name", list(synth.PERSONAL))
def test_every_surname_is_invented(name: str) -> None:
    surnames = {
        pseudonym.normalize(as_str(as_dict(p).get("surname")))
        for race in _races(name)
        for p in as_list(race["persons"])
    }
    invented = {pseudonym.normalize(s) for s in synth.INVENTED_SURNAMES}
    assert surnames <= invented


def test_cards_cover_several_card_types() -> None:
    cards = [
        as_int(as_dict(p)["card_number"])
        for p in as_list(_races("personal_individual")[0]["persons"])
    ]
    labels = {pseudonym.card_class(c)[2] for c in cards if c > 0}
    assert len(labels) >= 6


def test_individual_fills_every_masked_field() -> None:
    race = _races("personal_individual")[0]
    data = as_dict(race["data"])
    assert all(as_str(data[k]) for k in ("title", "location", "chief_referee", "secretary", "url"))
    persons = [as_dict(p) for p in as_list(race["persons"])]
    assert any(p["birth_date"] for p in persons)
    assert any(p["comment"] for p in persons)
    assert any(p["world_code"] for p in persons)
    organizations = [as_dict(o) for o in as_list(race["organizations"])]
    assert all(o["name"] and o["region"] and o["contact"] for o in organizations)
    settings = as_dict(race["settings"])
    assert settings["live_urls"]
    assert settings["telegram_chat_id"]


def test_multi_day_spells_some_names_differently_on_different_days() -> None:
    day1, day2 = _races("personal_multi_day")
    assert as_dict(day1["data"])["race_type"] == as_dict(day2["data"])["race_type"] == 6

    def names(race: dict[str, Json]) -> set[str]:
        return {as_str(as_dict(p)["surname"]) for p in as_list(race["persons"])}

    first, second = names(day1), names(day2)
    variants = {
        (a, b)
        for a in first
        for b in second
        if a != b and pseudonym.normalize(a) == pseudonym.normalize(b)
    }
    assert len(variants) >= 2
    assert first & second


def test_old_format_has_no_races_key_and_old_field_names() -> None:
    doc = as_dict(synth.PERSONAL["personal_old_format"]())
    assert "races" not in doc
    assert doc["object"] == "Race"
    persons = [as_dict(p) for p in as_list(doc["persons"])]
    assert all("sportident_card" in p for p in persons)
    organizations = [as_dict(o) for o in as_list(doc["organizations"])]
    assert all(isinstance(o["address"], dict) for o in organizations)


def test_personal_generation_is_deterministic() -> None:
    for build in synth.PERSONAL.values():
        assert synth.dumps(build()) == synth.dumps(build())


def test_cli_writes_the_personal_races(tmp_path: Path) -> None:
    assert synth.main(["--out", str(tmp_path), "--personal"]) == 0
    assert sorted(p.stem for p in tmp_path.iterdir()) == sorted(synth.PERSONAL)
