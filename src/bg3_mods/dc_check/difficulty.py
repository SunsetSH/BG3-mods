"""DifficultyClasses.lsx: DC UUID -> number.

The table is split over several files (Shared, SharedDev, GustavDev), each holds its own
rows, so the tables are merged. See docs/NOTES.md.
"""

from collections.abc import Iterable
from pathlib import Path

from bg3_mods.lsx import GameDataError, attributes, parse_xml, require


def parse_difficulty_classes(path: Path) -> dict[str, int]:
    table: dict[str, int] = {}
    for node in parse_xml(path).iter("node"):
        if node.get("id") != "DifficultyClass":
            continue
        values = attributes(node)
        uuid = require(values, "UUID", path)
        raw = require(values, "Difficulties", path)
        if not raw.isdigit():
            raise GameDataError(f"{path}: DC {uuid} has non-numeric Difficulties '{raw}'")
        table[uuid] = int(raw)
    return table


def merge_tables(tables: Iterable[tuple[Path, dict[str, int]]]) -> dict[str, int]:
    """Union of tables; the same UUID with different numbers is an error."""
    merged: dict[str, int] = {}
    origin: dict[str, Path] = {}
    for path, table in tables:
        for uuid, dc in table.items():
            if uuid in merged and merged[uuid] != dc:
                raise GameDataError(
                    f"DC {uuid} is {merged[uuid]} in {origin[uuid]} but {dc} in {path}"
                )
            merged[uuid] = dc
            origin.setdefault(uuid, path)
    return merged
