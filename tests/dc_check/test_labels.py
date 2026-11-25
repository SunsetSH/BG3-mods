from pathlib import Path

import pytest

from bg3_mods.dc_check.dialogs import ZERO_UUID, RollOption, parse_roll_options
from bg3_mods.dc_check.difficulty import parse_difficulty_classes
from bg3_mods.dc_check.labels import TERMS, format_label, handle_dcs, label_entries
from bg3_mods.loca import LocaEntry, parse_loca
from bg3_mods.lsx import GameDataError


def option(dc_id: str, *handles: str) -> RollOption:
    return RollOption(Path("d.lsx"), "node", dc_id, handles)


def test_handle_dcs_skips_rolls_without_dc() -> None:
    dcs = handle_dcs([option("act1", "h1"), option(ZERO_UUID, "h2")], {"act1": 10})
    assert dcs == {"h1": frozenset({10})}


def test_handle_dcs_collects_different_dcs_of_shared_text() -> None:
    dcs = handle_dcs([option("a", "h"), option("b", "h")], {"a": 5, "b": 10})
    assert dcs == {"h": frozenset({5, 10})}


def test_handle_dcs_rejects_unknown_dc() -> None:
    with pytest.raises(GameDataError, match="unknown DC missing"):
        handle_dcs([option("missing", "h")], {})


@pytest.mark.parametrize(
    ("term", "dcs", "label"),
    [("DC", [15], "(DC 15) "), ("КС", [10, 5, 10], "(КС 5/10) "), ("DC", [0], "(DC 0) ")],
)
def test_format_label(term: str, dcs: list[int], label: str) -> None:
    assert format_label(term, dcs) == label


def test_format_label_needs_a_dc() -> None:
    with pytest.raises(ValueError, match="at least one DC"):
        format_label("DC", [])


def test_label_entries_prefixes_roll_texts_only() -> None:
    entries = [LocaEntry("roll", "2", "<i>Kneel.</i>"), LocaEntry("plain", "1", "Bye.")]
    result = label_entries(entries, {"roll": frozenset({10})}, TERMS["English"])
    assert result == [LocaEntry("roll", "2", "(DC 10) <i>Kneel.</i>")]


def test_fixture_dialog_to_russian_labels(fixtures: Path) -> None:
    classes = parse_difficulty_classes(fixtures / "DifficultyClasses.lsx")
    dcs = handle_dcs(parse_roll_options(fixtures / "dialog_rolls.lsx"), classes)
    result = label_entries(parse_loca(fixtures / "russian.xml"), dcs, TERMS["Russian"])
    # h-roll-b has an empty text, h-plain is not a roll, h-attack has no DC.
    assert result == [LocaEntry("h-roll-a", "2", "(КС 10) <i>Встать на колено.</i>")]
