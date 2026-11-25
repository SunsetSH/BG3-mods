"""Game data DC Check reads, and where its generated localization goes.

Checked on Patch 8 Hotfix 10.
"""

from pathlib import Path

from bg3_mods import mods
from bg3_mods.gamedata import Source

SLUG = "dc_check"

# Patch8_HotFix*.pak and GustavX.pak override none of these files (listed on Patch 8 Hotfix 10).
DIFFICULTY_SOURCES = (
    Source("Shared.pak", "*/DifficultyClasses/DifficultyClasses.lsx"),
    Source("Gustav.pak", "*/DifficultyClasses/DifficultyClasses.lsx"),
)
DIALOG_SOURCES = (
    Source("Gustav.pak", "*/Story/DialogsBinary/*"),
    Source("Shared.pak", "*/Story/DialogsBinary/*"),
)
LANGUAGE_SOURCES = {
    "English": Source("Localization/English.pak", "*.loca"),
    "Russian": Source("Localization/Russian/Russian.pak", "*.loca"),
}


def language_dir(language: str) -> Path:
    """Folder with the game .loca files of a language after extraction."""
    return LANGUAGE_SOURCES[language].extracted / "Localization" / language


def mod_localization_dir() -> Path:
    return mods.get(SLUG).module_dir / "Localization"


def mod_language_dir(language: str) -> Path:
    return mod_localization_dir() / language
