"""Repository folders and the game location, shared by every mod."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS_DIR = ROOT / "mods"
PAKS_DIR = ROOT / "paks"
BUILD_DIR = ROOT / "build"
UNPACKED_DIR = ROOT / "unpacked"
TOOLS_DIR = ROOT / "tools"

DEFAULT_GAME_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3")


def game_data_dir() -> Path:
    """Game Data folder; BG3_DIR overrides the default Steam location."""
    return Path(os.environ.get("BG3_DIR", str(DEFAULT_GAME_DIR))) / "Data"


# Where the player puts every .pak; written as in Windows Explorer for README instructions.
PLAYER_MODS_FOLDER = r"%LOCALAPPDATA%\Larian Studios\Baldur's Gate 3\Mods"
