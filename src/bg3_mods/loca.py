"""Localization XML (`<contentList><content contentuid version>text</content>`)."""

import xml.etree.ElementTree as ET
from collections.abc import Iterable
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

from bg3_mods.lsx import GameDataError, parse_xml

MOD_SUFFIX = ".loca.xml"
XML_DECLARATION = '<?xml version="1.0" encoding="utf-8"?>\n'


@dataclass(frozen=True)
class LocaEntry:
    handle: str
    version: str
    text: str


def parse_loca(path: Path) -> list[LocaEntry]:
    root = parse_xml(path)
    if root.tag != "contentList":
        raise GameDataError(f"{path}: expected <contentList>, got <{root.tag}>")
    entries: list[LocaEntry] = []
    for content in root.findall("content"):
        handle = content.get("contentuid")
        version = content.get("version")
        if not handle or not version:
            raise GameDataError(f"{path}: <content> without contentuid or version")
        entries.append(LocaEntry(handle, version, content.text or ""))
    return entries


def build_loca(entries: Iterable[LocaEntry]) -> bytes:
    root = ET.Element("contentList")
    for entry in entries:
        content = ET.SubElement(root, "content", contentuid=entry.handle, version=entry.version)
        content.text = entry.text
    ET.indent(root, space="\t")
    # Same declaration as the game files; ElementTree would write single quotes.
    return (XML_DECLARATION + ET.tostring(root, encoding="unicode") + "\n").encode("utf-8")


def _stem(name: str) -> str:
    for suffix in (MOD_SUFFIX, ".xml", ".loca"):
        if name.lower().endswith(suffix):
            return name[: -len(suffix)]
    return name


def loca_key(relative: PurePosixPath) -> str:
    """Case-insensitive name shared by `russian.xml`, `russian.loca`, `russian.loca.xml`."""
    return str(relative.parent / _stem(relative.name)).lower()


def mod_file_name(relative: PurePosixPath) -> PurePosixPath:
    """Game file `Gender/Female/russian_to_F.xml` -> mod file `.../russian_to_F.loca.xml`."""
    return relative.parent / (_stem(relative.name) + MOD_SUFFIX)


def overlay(base: list[LocaEntry], overrides: Iterable[LocaEntry]) -> list[LocaEntry]:
    """Texts from `overrides` replace base texts with the same handle; new handles are ignored."""
    texts = {entry.handle: entry for entry in overrides}
    return [
        replace(entry, text=texts[entry.handle].text) if entry.handle in texts else entry
        for entry in base
    ]
