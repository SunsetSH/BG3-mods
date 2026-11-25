"""Generate the mod localization: roll option texts with the DC in front.

Extracts and converts the needed game files into unpacked/ (cached, --refresh redoes it),
then writes mods/dc_check/pak/Mods/<folder>/Localization/<Language>/*.loca.xml.

Usage: uv run python scripts/dc_check_generate.py [--refresh] [--base-pak PATH.pak]
--base-pak takes option texts from a translation mod (for example Fixed Russian translation),
so a personal build keeps its fixes. Load DC Check after that mod.
"""

import argparse
import shutil
import sys
from collections.abc import Iterable
from pathlib import Path, PurePosixPath

from bg3_mods import divine, paths
from bg3_mods.dc_check import sources
from bg3_mods.dc_check.dialogs import RollOption, parse_roll_options
from bg3_mods.dc_check.difficulty import merge_tables, parse_difficulty_classes
from bg3_mods.dc_check.labels import TERMS, handle_dcs, label_entries
from bg3_mods.gamedata import convert_loca, convert_resources, extract
from bg3_mods.loca import LocaEntry, build_loca, loca_key, mod_file_name, overlay, parse_loca
from bg3_mods.lsx import GameDataError


def log(message: str) -> None:
    print(message, flush=True)


def load_options(refresh: bool) -> list[RollOption]:
    options: list[RollOption] = []
    for source in sources.DIALOG_SOURCES:
        extract(source, refresh, log)
        for path in sorted(convert_resources(source, refresh, log).rglob("*.lsx")):
            try:
                options += parse_roll_options(path)
            except GameDataError as error:
                # LSLib 1.20.4 writes a few cinematic dialogs truncated, see docs/NOTES.md.
                print(f"WARNING: skipped dialog: {error}", file=sys.stderr)
    return options


def load_difficulty(refresh: bool) -> dict[str, int]:
    tables: list[tuple[Path, dict[str, int]]] = []
    for source in sources.DIFFICULTY_SOURCES:
        extract(source, refresh, log)
        for path in sorted(source.extracted.rglob("DifficultyClasses.lsx")):
            tables.append((path, parse_difficulty_classes(path)))
    if not tables:
        raise GameDataError("No DifficultyClasses.lsx found in the game data")
    return merge_tables(tables)


def load_base_texts(base_pak: Path, language: str) -> dict[str, list[LocaEntry]]:
    """loca_key -> entries of a translation mod's files for one language."""
    target = paths.UNPACKED_DIR / "base" / base_pak.stem
    divine.run(divine.extract_command(base_pak, target, "*Localization*"))
    convert_loca(target, refresh=False)
    texts: dict[str, list[LocaEntry]] = {}
    for folder in target.glob(f"**/Localization/{language}"):
        for path in folder.rglob("*.xml"):
            relative = PurePosixPath(path.relative_to(folder).as_posix())
            texts[loca_key(relative)] = parse_loca(path)
    return texts


def write_language(
    language: str,
    dcs: dict[str, frozenset[int]],
    game_files: Iterable[Path],
    base: dict[str, list[LocaEntry]],
) -> set[str]:
    """Writes the mod files of one language; returns the handles that got a label."""
    folder = sources.language_dir(language)
    labelled: set[str] = set()
    for path in game_files:
        relative = PurePosixPath(path.relative_to(folder).as_posix())
        entries = overlay(parse_loca(path), base.get(loca_key(relative), []))
        result = label_entries(entries, dcs, TERMS[language])
        if not result:
            continue
        target = sources.mod_language_dir(language) / mod_file_name(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(build_loca(result))
        labelled.update(entry.handle for entry in result)
        print(f"  {language}/{mod_file_name(relative)}: {len(result)} texts")
    return labelled


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="re-extract game data")
    parser.add_argument("--base-pak", type=Path, help="translation mod .pak to take texts from")
    args = parser.parse_args()
    if args.base_pak and not args.base_pak.is_file():
        print(f"Not found: {args.base_pak}", file=sys.stderr)
        return 1

    try:
        classes = load_difficulty(args.refresh)
        options = load_options(args.refresh)
        dcs = handle_dcs(options, classes)
    except (GameDataError, FileNotFoundError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    without_dc = sum(1 for option in options if not option.has_dc)
    print(f"DC classes: {len(classes)}; roll options: {len(options)} ({without_dc} without DC)")
    print(f"Option texts with a DC: {len(dcs)}")

    shutil.rmtree(sources.mod_localization_dir(), ignore_errors=True)
    for language, source in sources.LANGUAGE_SOURCES.items():
        extract(source, args.refresh, log)
        game_files = convert_loca(sources.language_dir(language), args.refresh)
        base = load_base_texts(args.base_pak, language) if args.base_pak else {}
        labelled = write_language(language, dcs, game_files, base)
        missing = len(dcs.keys() - labelled)
        print(f"{language}: {len(labelled)} texts labelled, {missing} have no text in game files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
