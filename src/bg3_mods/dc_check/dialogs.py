"""Dialog .lsx files: player options that start a roll (ActiveRoll nodes)."""

from dataclasses import dataclass
from pathlib import Path

from bg3_mods.lsx import GameDataError, attributes, parse_xml, require

ZERO_UUID = "00000000-0000-0000-0000-000000000000"


@dataclass(frozen=True)
class RollOption:
    """One ActiveRoll node; `handles` are its option texts (one per tag-rule variant)."""

    source: Path
    node_uuid: str
    difficulty_id: str
    handles: tuple[str, ...]

    @property
    def has_dc(self) -> bool:
        """Attack and contested rolls carry the zero UUID: the game has no fixed DC for them."""
        return self.difficulty_id != ZERO_UUID


def parse_roll_options(path: Path) -> list[RollOption]:
    options: list[RollOption] = []
    for node in parse_xml(path).iter("node"):
        if node.get("id") != "node":
            continue
        values = attributes(node)
        if values.get("constructor") != "ActiveRoll":
            continue
        handles: list[str] = []
        for text in node.iter("attribute"):
            if text.get("id") != "TagText":
                continue
            handle = text.get("handle")
            if not handle:
                raise GameDataError(f"{path}: TagText without handle in {values.get('UUID')}")
            handles.append(handle)
        options.append(
            RollOption(
                source=path,
                node_uuid=require(values, "UUID", path),
                difficulty_id=require(values, "DifficultyClassID", path),
                handles=tuple(handles),
            )
        )
    return options
