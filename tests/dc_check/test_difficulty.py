from pathlib import Path

import pytest

from bg3_mods.dc_check.difficulty import merge_tables, parse_difficulty_classes
from bg3_mods.lsx import GameDataError


def test_parse_difficulty_classes(fixtures: Path) -> None:
    table = parse_difficulty_classes(fixtures / "DifficultyClasses.lsx")
    assert table == {
        "fa621d38-6f83-4e42-a55c-6aa651a75d46": 10,
        "89f0acd4-346f-479d-8b7a-1a3eb5382f6d": 14,
    }


def test_parse_rejects_non_numeric_dc(tmp_path: Path) -> None:
    path = tmp_path / "dc.lsx"
    path.write_text(
        '<save><node id="DifficultyClass">'
        '<attribute id="Difficulties" value="10;12"/><attribute id="UUID" value="u"/>'
        "</node></save>",
        encoding="utf-8",
    )
    with pytest.raises(GameDataError, match="non-numeric"):
        parse_difficulty_classes(path)


def test_parse_rejects_missing_uuid(tmp_path: Path) -> None:
    path = tmp_path / "dc.lsx"
    path.write_text(
        '<save><node id="DifficultyClass"><attribute id="Difficulties" value="10"/></node></save>',
        encoding="utf-8",
    )
    with pytest.raises(GameDataError, match="'UUID' missing"):
        parse_difficulty_classes(path)


def test_merge_tables_unions_disjoint_files() -> None:
    merged = merge_tables([(Path("a"), {"x": 10}), (Path("b"), {"y": 14, "x": 10})])
    assert merged == {"x": 10, "y": 14}


def test_merge_tables_rejects_conflicting_numbers() -> None:
    with pytest.raises(GameDataError, match="is 10 in a but 12 in b"):
        merge_tables([(Path("a"), {"x": 10}), (Path("b"), {"x": 12})])
