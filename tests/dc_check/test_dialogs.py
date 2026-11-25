from pathlib import Path

import pytest

from bg3_mods.dc_check.dialogs import ZERO_UUID, parse_roll_options
from bg3_mods.lsx import GameDataError


def test_parse_roll_options_takes_only_active_rolls(fixtures: Path) -> None:
    options = parse_roll_options(fixtures / "dialog_rolls.lsx")
    assert [option.node_uuid for option in options] == ["roll-with-dc", "attack-roll"]


def test_roll_option_keeps_every_text_variant(fixtures: Path) -> None:
    option = parse_roll_options(fixtures / "dialog_rolls.lsx")[0]
    assert option.handles == ("h-roll-a", "h-roll-b")
    assert option.difficulty_id == "fa621d38-6f83-4e42-a55c-6aa651a75d46"
    assert option.has_dc


def test_attack_roll_has_no_dc(fixtures: Path) -> None:
    attack = parse_roll_options(fixtures / "dialog_rolls.lsx")[1]
    assert attack.difficulty_id == ZERO_UUID
    assert not attack.has_dc


def test_text_without_handle_is_an_error(tmp_path: Path) -> None:
    path = tmp_path / "d.lsx"
    path.write_text(
        '<save><node id="node"><attribute id="constructor" value="ActiveRoll"/>'
        '<attribute id="UUID" value="n"/><attribute id="DifficultyClassID" value="u"/>'
        '<attribute id="TagText" type="TranslatedString"/></node></save>',
        encoding="utf-8",
    )
    with pytest.raises(GameDataError, match="without handle"):
        parse_roll_options(path)


def test_truncated_file_is_an_error_with_path(tmp_path: Path) -> None:
    path = tmp_path / "broken.lsx"
    path.write_text('<save><node id="node"><attribute id="val" value="', encoding="utf-8")
    with pytest.raises(GameDataError, match=r"broken\.lsx: invalid XML"):
        parse_roll_options(path)
