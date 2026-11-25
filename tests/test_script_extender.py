import json
from pathlib import Path

from bg3_mods import script_extender


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _mod(tmp_path: Path, config: object, scripts: dict[str, str]) -> Path:
    _write(tmp_path / "ScriptExtender" / "Config.json", json.dumps(config))
    for name, text in scripts.items():
        _write(tmp_path / "ScriptExtender" / "Lua" / name, text)
    return tmp_path


VALID_CONFIG = {"RequiredVersion": 34, "ModTable": "RunSpeed", "FeatureFlags": ["Lua"]}
VALID_SCRIPTS = {
    "BootstrapServer.lua": 'Ext.Require("Server/Speed.lua")\n',
    "BootstrapClient.lua": "Ext.Require('Client/Window.lua')\n",
    "Server/Speed.lua": 'local Speed = Ext.Require("Shared/Speed.lua")\n',
    "Client/Window.lua": "",
    "Shared/Speed.lua": "",
}


def test_detects_script_extender_folder(tmp_path: Path) -> None:
    assert not script_extender.uses_script_extender(tmp_path)
    _mod(tmp_path, VALID_CONFIG, VALID_SCRIPTS)
    assert script_extender.uses_script_extender(tmp_path)


def test_valid_mod_has_no_problems(tmp_path: Path) -> None:
    assert script_extender.mod_problems(_mod(tmp_path, VALID_CONFIG, VALID_SCRIPTS)) == []


def test_reports_missing_require_target(tmp_path: Path) -> None:
    scripts = {k: v for k, v in VALID_SCRIPTS.items() if k != "Shared/Speed.lua"}
    problems = script_extender.mod_problems(_mod(tmp_path, VALID_CONFIG, scripts))
    assert len(problems) == 1
    assert "Shared/Speed.lua" in problems[0]


def test_reports_missing_bootstrap(tmp_path: Path) -> None:
    scripts = {k: v for k, v in VALID_SCRIPTS.items() if k != "BootstrapClient.lua"}
    problems = script_extender.mod_problems(_mod(tmp_path, VALID_CONFIG, scripts))
    assert problems == [f"{tmp_path / 'ScriptExtender' / 'Lua' / 'BootstrapClient.lua'}: missing"]


def test_reports_config_without_lua_flag_and_bad_types(tmp_path: Path) -> None:
    config = {"RequiredVersion": "34", "ModTable": "", "FeatureFlags": []}
    problems = script_extender.mod_problems(_mod(tmp_path, config, VALID_SCRIPTS))
    assert len(problems) == 3
    assert any("RequiredVersion" in p for p in problems)
    assert any("ModTable" in p for p in problems)
    assert any("FeatureFlags" in p for p in problems)


def test_reports_unreadable_config(tmp_path: Path) -> None:
    _write(tmp_path / "Config.json", "{not json")
    problems = script_extender.config_problems(tmp_path / "Config.json")
    assert len(problems) == 1
    assert "unreadable" in problems[0]
