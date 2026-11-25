from pathlib import Path, PurePosixPath

import pytest

from bg3_mods.loca import LocaEntry, build_loca, loca_key, mod_file_name, overlay, parse_loca
from bg3_mods.lsx import GameDataError


def test_parse_loca_reads_bom_file_and_empty_text(fixtures: Path) -> None:
    entries = parse_loca(fixtures / "russian.xml")
    assert entries[0] == LocaEntry("h-roll-a", "2", "<i>Встать на колено.</i>")
    assert entries[1].text == ""


def test_parse_loca_rejects_other_root(tmp_path: Path) -> None:
    path = tmp_path / "x.xml"
    path.write_text("<save/>", encoding="utf-8")
    with pytest.raises(GameDataError, match="expected <contentList>"):
        parse_loca(path)


def test_build_loca_round_trips_markup(tmp_path: Path) -> None:
    entries = [LocaEntry("h1", "3", "(КС 10) <i>Встать</i> & уйти")]
    data = build_loca(entries)
    assert data.startswith(b'<?xml version="1.0" encoding="utf-8"?>\n<contentList>')
    assert b"&lt;i&gt;" in data
    path = tmp_path / "out.loca.xml"
    path.write_bytes(data)
    assert parse_loca(path) == entries


def test_loca_key_matches_game_and_mod_names() -> None:
    game = PurePosixPath("Gender/Female/russian_to_F.xml")
    mod = PurePosixPath("Gender/Female/russian_to_F.loca.xml")
    assert loca_key(game) == loca_key(mod) == "gender/female/russian_to_f"


def test_mod_file_name_keeps_case() -> None:
    assert mod_file_name(PurePosixPath("russian_M_to_X.xml")) == PurePosixPath(
        "russian_M_to_X.loca.xml"
    )


def test_overlay_replaces_known_handles_only() -> None:
    base = [LocaEntry("a", "1", "old"), LocaEntry("b", "2", "keep")]
    result = overlay(base, [LocaEntry("a", "5", "fixed"), LocaEntry("new", "1", "x")])
    assert result == [LocaEntry("a", "1", "fixed"), LocaEntry("b", "2", "keep")]
