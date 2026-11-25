"""Shared helpers for Larian XML files (.lsx and .loca.xml)."""

import xml.etree.ElementTree as ET
from pathlib import Path


class GameDataError(ValueError):
    """Game file has an unexpected shape; the message names the file."""


def parse_xml(path: Path) -> ET.Element:
    try:
        return ET.parse(path).getroot()  # noqa: S314 (local game files, not network input)
    except ET.ParseError as error:
        raise GameDataError(f"{path}: invalid XML ({error})") from error


def attributes(node: ET.Element) -> dict[str, str]:
    """`<attribute id=... value=...>` children of an lsx node as id -> value."""
    return {
        attr.get("id", ""): attr.get("value", "")
        for attr in node.findall("attribute")
        if attr.get("value") is not None
    }


def require(values: dict[str, str], key: str, path: Path) -> str:
    if key not in values:
        raise GameDataError(f"{path}: attribute '{key}' missing in {sorted(values)}")
    return values[key]
