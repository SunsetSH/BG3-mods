"""Static checks of a mod's Script Extender files (Mods/<folder>/ScriptExtender/).

Lua can't run here (no interpreter, no game), so the checks cover what breaks loading
before any script runs: Config.json shape and Ext.Require targets.
"""

import json
import re
from pathlib import Path

BOOTSTRAP_SCRIPTS = ("BootstrapServer.lua", "BootstrapClient.lua")

_REQUIRE = re.compile(r"""Ext\.Require\(\s*["']([^"']+)["']\s*\)""")


def config_problems(config: Path) -> list[str]:
    """Problems in ScriptExtender/Config.json that stop SE from loading the Lua part."""
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{config}: unreadable ({error})"]
    if not isinstance(data, dict):
        return [f"{config}: expected a JSON object"]
    problems = []
    if not isinstance(data.get("RequiredVersion"), int):
        problems.append(f"{config}: RequiredVersion must be an integer")
    if not isinstance(data.get("ModTable"), str) or not data["ModTable"]:
        problems.append(f"{config}: ModTable must be a non-empty string")
    if "Lua" not in data.get("FeatureFlags", []):
        problems.append(f"{config}: FeatureFlags must contain 'Lua'")
    return problems


def require_problems(lua_dir: Path) -> list[str]:
    """Missing bootstrap scripts and Ext.Require paths that point at no file."""
    problems = [
        f"{lua_dir / name}: missing" for name in BOOTSTRAP_SCRIPTS if not (lua_dir / name).is_file()
    ]
    for script in sorted(lua_dir.rglob("*.lua")):
        for target in _REQUIRE.findall(script.read_text(encoding="utf-8")):
            if not (lua_dir / target).is_file():
                problems.append(f"{script}: Ext.Require target not found: {target}")
    return problems


def uses_script_extender(module_dir: Path) -> bool:
    return (module_dir / "ScriptExtender").is_dir()


def mod_problems(module_dir: Path) -> list[str]:
    extender = module_dir / "ScriptExtender"
    return config_problems(extender / "Config.json") + require_problems(extender / "Lua")
