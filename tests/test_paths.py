from pathlib import Path

import pytest

from bg3_mods import paths


def test_game_data_dir_respects_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BG3_DIR", r"D:\Games\BG3")
    assert paths.game_data_dir() == Path(r"D:\Games\BG3") / "Data"


def test_game_data_dir_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BG3_DIR", raising=False)
    assert paths.game_data_dir() == paths.DEFAULT_GAME_DIR / "Data"
