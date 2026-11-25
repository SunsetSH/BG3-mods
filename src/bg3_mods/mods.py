"""Mods of the repository: one folder per mod in mods/<slug>/, found by its meta.lsx.

Layout of a mod (see docs/adr/0006-multi-mod-repository.md):
    mods/<slug>/README.md               player-facing: features, installation, compatibility
    mods/<slug>/TESTING.md              manual in-game check list
    mods/<slug>/pak/Mods/<Pak>_<UUID>/  exactly what goes into paks/<Pak>.pak
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from bg3_mods import paths, script_extender
from bg3_mods.lsx import GameDataError
from bg3_mods.meta import ModuleInfo, read_module_info
from bg3_mods.scaffold import TODO_MARK

SLUG = re.compile(r"^[a-z][a-z0-9_]*$")
PAK_NAME = re.compile(r"^[A-Z][A-Za-z0-9]*$")
REQUIRED_DOCS = ("README.md", "TESTING.md")
# README of every mod must tell the player where the .pak goes and what else to install.
INSTALL_HEADING = "## Установка"
UNINSTALL_WORD = "Удаление"
SCRIPT_EXTENDER_TERMS = ("github.com/Norbyte/bg3se", "DWrite.dll")

# Parts of a module folder that a script generates and git ignores: slug -> (path, command).
GENERATED: Mapping[str, tuple[str, str]] = {
    "dc_check": ("Localization", "uv run python scripts/dc_check_generate.py"),
}


@dataclass(frozen=True)
class Mod:
    slug: str
    root: Path

    @property
    def pak_source(self) -> Path:
        return self.root / "pak"

    @property
    def module_dir(self) -> Path:
        """The single Mods/<Pak>_<UUID>/ folder; anything else is a layout error."""
        found = sorted(p for p in (self.pak_source / "Mods").glob("*") if p.is_dir())
        if len(found) != 1:
            raise GameDataError(
                f"{self.pak_source / 'Mods'}: expected one module folder, got {found}"
            )
        return found[0]

    @property
    def info(self) -> ModuleInfo:
        return read_module_info(self.module_dir / "meta.lsx")

    @property
    def pak_name(self) -> str:
        """`DCCheck` from the folder `DCCheck_<UUID>`."""
        return self.module_dir.name.rsplit("_", 1)[0]


def discover(mods_dir: Path = paths.MODS_DIR) -> list[Mod]:
    return [Mod(p.name, p) for p in sorted(mods_dir.iterdir()) if (p / "pak").is_dir()]


def get(slug: str, mods_dir: Path = paths.MODS_DIR) -> Mod:
    for mod in discover(mods_dir):
        if mod.slug == slug:
            return mod
    raise KeyError(f"No mod '{slug}' in {mods_dir}")


def _meta_problems(mod: Mod) -> list[str]:
    meta = mod.module_dir / "meta.lsx"
    info = mod.info
    problems = []
    if info.folder != mod.module_dir.name:
        problems.append(f"{meta}: Folder '{info.folder}' differs from '{mod.module_dir.name}'")
    if mod.module_dir.name != f"{mod.pak_name}_{info.uuid}":
        problems.append(f"{meta}: folder must be named <Pak>_{info.uuid}")
    if not PAK_NAME.match(mod.pak_name):
        problems.append(f"{meta}: pak name '{mod.pak_name}' must be PascalCase ASCII")
    if info.version64 != info.publish_version64:
        problems.append(f"{meta}: ModuleInfo and PublishVersion Version64 differ")
    return problems


def installation_section(readme: str) -> str | None:
    """Text of `## Установка` up to the next `## ` heading, or None without the section."""
    lines = readme.splitlines()
    if INSTALL_HEADING not in lines:
        return None
    body = lines[lines.index(INSTALL_HEADING) + 1 :]
    end = next((i for i, line in enumerate(body) if line.startswith("## ")), len(body))
    return "\n".join(body[:end])


def installation_problems(readme: str, pak_name: str, script_extender_mod: bool) -> list[str]:
    """What the installation section lacks: the .pak, its folder, removal, SE steps."""
    section = installation_section(readme)
    if section is None:
        return [f"section '{INSTALL_HEADING}' missing"]
    required = [f"{pak_name}.pak", paths.PLAYER_MODS_FOLDER, UNINSTALL_WORD]
    if script_extender_mod:
        required += SCRIPT_EXTENDER_TERMS
    missing = [term for term in required if term not in section]
    return [f"'{INSTALL_HEADING}' does not mention '{term}'" for term in missing]


def _doc_problems(mod: Mod) -> list[str]:
    problems = []
    for name in REQUIRED_DOCS:
        path = mod.root / name
        if not path.is_file():
            problems.append(f"{path}: missing")
        elif TODO_MARK in path.read_text(encoding="utf-8"):
            problems.append(f"{path}: template text '{TODO_MARK}' left")
    readme = mod.root / "README.md"
    if readme.is_file():
        uses_se = script_extender.uses_script_extender(mod.module_dir)
        text = readme.read_text(encoding="utf-8")
        problems += [
            f"{readme}: {problem}" for problem in installation_problems(text, mod.pak_name, uses_se)
        ]
    return problems


def mod_problems(mod: Mod) -> list[str]:
    """Layout, meta.lsx and Script Extender problems; generated parts are not required."""
    if not SLUG.match(mod.slug):
        return [f"{mod.root}: folder name must be snake_case"]
    try:
        problems = _meta_problems(mod)
    except GameDataError as error:
        return [str(error)]
    if script_extender.uses_script_extender(mod.module_dir):
        problems += script_extender.mod_problems(mod.module_dir)
    return problems + _doc_problems(mod)


def missing_generated(mod: Mod) -> str | None:
    """Command to run when a generated part of the mod is absent, else None."""
    if mod.slug not in GENERATED:
        return None
    path, command = GENERATED[mod.slug]
    return None if (mod.module_dir / path).exists() else command


def registry_problems(mods: Iterable[Mod]) -> list[str]:
    """UUIDs and pak names must be unique: the game and build/ key on them."""
    problems = []
    seen: dict[str, str] = {}
    for mod in mods:
        for key in (mod.info.uuid, mod.pak_name.lower()):
            if key in seen:
                problems.append(f"{mod.slug}: '{key}' already used by {seen[key]}")
            seen[key] = mod.slug
    return problems
