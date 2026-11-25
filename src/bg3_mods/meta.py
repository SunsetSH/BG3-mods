"""meta.lsx: module identity and version in the game's Version64 format."""

from dataclasses import dataclass
from pathlib import Path

from bg3_mods.lsx import GameDataError, attributes, parse_xml, require

_SHIFTS = (55, 47, 31, 0)
_MASKS = ((1 << 9) - 1, (1 << 8) - 1, (1 << 16) - 1, (1 << 31) - 1)


@dataclass(frozen=True)
class ModuleInfo:
    """ModuleInfo of meta.lsx; `publish_version64` comes from its PublishVersion child."""

    name: str
    folder: str
    uuid: str
    description: str
    version64: int
    publish_version64: int

    @property
    def version(self) -> str:
        return version_string(self.version64)


def version64(version: str) -> int:
    """`1.2.3` or `1.2.3.4` -> major<<55 | minor<<47 | revision<<31 | build (see docs/NOTES.md)."""
    parts = [int(part) for part in version.split(".")]
    if not 3 <= len(parts) <= 4:  # noqa: PLR2004 (semver plus optional build number)
        raise ValueError(f"expected 3 or 4 version parts, got '{version}'")
    major, minor, revision, build = [*parts, 0][:4]
    return (major << 55) | (minor << 47) | (revision << 31) | build


def version_string(value: int) -> str:
    """Inverse of version64: `1.2.3`, plus `.4` only when the build number is set."""
    major, minor, revision, build = (
        (value >> shift) & mask for shift, mask in zip(_SHIFTS, _MASKS, strict=True)
    )
    base = f"{major}.{minor}.{revision}"
    return f"{base}.{build}" if build else base


def read_module_info(path: Path) -> ModuleInfo:
    root = parse_xml(path)
    info = next((n for n in root.iter("node") if n.get("id") == "ModuleInfo"), None)
    publish = next((n for n in root.iter("node") if n.get("id") == "PublishVersion"), None)
    if info is None or publish is None:
        raise GameDataError(f"{path}: ModuleInfo or PublishVersion node missing")
    values = attributes(info)
    return ModuleInfo(
        name=require(values, "Name", path),
        folder=require(values, "Folder", path),
        uuid=require(values, "UUID", path),
        description=require(values, "Description", path),
        version64=int(require(values, "Version64", path)),
        publish_version64=int(require(attributes(publish), "Version64", path)),
    )
