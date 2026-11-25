"""DC labels: which option texts get one and how the label reads."""

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import replace

from bg3_mods.dc_check.dialogs import RollOption
from bg3_mods.loca import LocaEntry
from bg3_mods.lsx import GameDataError

# Abbreviations the game itself uses on the roll screen: handle hd45a9fec... "DC [1]" / "КС [1]".
TERMS: Mapping[str, str] = {"English": "DC", "Russian": "КС"}


def handle_dcs(
    options: Iterable[RollOption], classes: Mapping[str, int]
) -> dict[str, frozenset[int]]:
    """Option text handle -> every DC it is rolled against. Options without a DC are skipped."""
    result: dict[str, set[int]] = defaultdict(set)
    for option in options:
        if not option.has_dc:
            continue
        if option.difficulty_id not in classes:
            raise GameDataError(
                f"{option.source}: node {option.node_uuid} uses unknown DC {option.difficulty_id}"
            )
        for handle in option.handles:
            result[handle].add(classes[option.difficulty_id])
    return {handle: frozenset(dcs) for handle, dcs in result.items()}


def format_label(term: str, dcs: Iterable[int]) -> str:
    """`(DC 15) `; a text shared by checks with different DCs gets `(DC 5/10) `."""
    values = "/".join(str(dc) for dc in sorted(set(dcs)))
    if not values:
        raise ValueError("format_label needs at least one DC")
    return f"({term} {values}) "


def label_entries(
    entries: Iterable[LocaEntry], dcs_by_handle: Mapping[str, frozenset[int]], term: str
) -> list[LocaEntry]:
    """Entries whose handle is a roll option, with the DC label in front of the text."""
    return [
        replace(entry, text=format_label(term, dcs_by_handle[entry.handle]) + entry.text)
        for entry in entries
        if entry.handle in dcs_by_handle and entry.text.strip()
    ]
