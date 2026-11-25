"""Game files extracted into unpacked/: one cache shared by every mod's generator."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from bg3_mods import divine, paths


@dataclass(frozen=True)
class Source:
    """Files matching `expression` inside `pak` (path relative to the game Data folder)."""

    pak: str
    expression: str

    @property
    def extracted(self) -> Path:
        return paths.UNPACKED_DIR / PurePosixPath(self.pak).stem

    @property
    def stamp(self) -> Path:
        slug = "".join(ch if ch.isalnum() else "_" for ch in f"{self.pak}_{self.expression}")
        return paths.UNPACKED_DIR / "stamps" / slug


def converted_lsx(source: Source) -> Path:
    return paths.UNPACKED_DIR / "lsx" / source.extracted.name


def extract(source: Source, refresh: bool, log: Callable[[str], None]) -> None:
    """Extract once; the stamp file marks a finished extraction, refresh redoes it."""
    if source.stamp.is_file() and not refresh:
        return
    package = paths.game_data_dir() / source.pak
    if not package.is_file():
        raise FileNotFoundError(f"{package} not found. Set BG3_DIR to the game folder.")
    log(f"Extracting {source.expression} from {source.pak}")
    divine.run(divine.extract_command(package, source.extracted, source.expression))
    source.stamp.parent.mkdir(parents=True, exist_ok=True)
    source.stamp.write_text(str(package), encoding="utf-8")


def convert_resources(source: Source, refresh: bool, log: Callable[[str], None]) -> Path:
    """Every extracted .lsf of `source` as .lsx under unpacked/lsx/<pak>/ (dialogs, stats, ...)."""
    target = converted_lsx(source)
    stamp = source.stamp.with_name(source.stamp.name + "_lsx")
    if refresh or not stamp.is_file():
        log(f"Converting {source.expression} of {source.pak} to lsx")
        divine.run(divine.convert_resources_command(source.extracted / "Mods", target))
        stamp.write_text(str(target), encoding="utf-8")
    return target


def convert_loca(folder: Path, refresh: bool) -> list[Path]:
    """Each .loca under folder -> .xml next to it; returns the .xml files."""
    converted: list[Path] = []
    for loca in sorted(folder.rglob("*.loca")):
        xml = loca.with_suffix(".xml")
        if refresh or not xml.is_file():
            divine.run(divine.convert_loca_command(loca, xml))
        converted.append(xml)
    return converted
