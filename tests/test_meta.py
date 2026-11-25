from pathlib import Path

import pytest

from bg3_mods.lsx import GameDataError
from bg3_mods.meta import read_module_info, version64, version_string


def test_version64_matches_notes_formula() -> None:
    assert version64("0.1.0") == 140737488355328
    assert version64("1.2.3.4") == (1 << 55) | (2 << 47) | (3 << 31) | 4


def test_version64_rejects_short_version() -> None:
    with pytest.raises(ValueError, match="3 or 4 version parts"):
        version64("1.0")


@pytest.mark.parametrize("version", ["0.1.0", "1.0.0", "2.13.400", "1.2.3.4"])
def test_version_string_inverts_version64(version: str) -> None:
    assert version_string(version64(version)) == version


def test_read_module_info_requires_publish_version(tmp_path: Path) -> None:
    path = tmp_path / "meta.lsx"
    path.write_text(
        '<save><node id="ModuleInfo"><attribute id="Version64" value="1"/></node></save>',
        encoding="utf-8",
    )
    with pytest.raises(GameDataError, match="PublishVersion"):
        read_module_info(path)


def test_read_module_info_names_missing_attribute(tmp_path: Path) -> None:
    path = tmp_path / "meta.lsx"
    path.write_text(
        '<save><node id="ModuleInfo"><attribute id="Name" value="X"/>'
        '<children><node id="PublishVersion"><attribute id="Version64" value="1"/></node>'
        "</children></node></save>",
        encoding="utf-8",
    )
    with pytest.raises(GameDataError, match="'Folder' missing"):
        read_module_info(path)
