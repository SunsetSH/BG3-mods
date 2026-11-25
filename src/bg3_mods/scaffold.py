"""Files of a new mod: meta.lsx in the game's format plus README and TESTING templates."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from string import Template

from bg3_mods.meta import version64
from bg3_mods.paths import PLAYER_MODS_FOLDER

# Marks template text that the author must replace; mods.mod_problems rejects it.
TODO_MARK = "ЗАПОЛНИТЬ"
TEMPLATES = Path(__file__).resolve().parent / "templates"
XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>\n'
# meta.lsx format of the shipped mods (taken from BetterTooltips, see docs/NOTES.md).
LSX_VERSION = {"major": "4", "minor": "8", "revision": "0", "build": "10"}


@dataclass(frozen=True)
class NewMod:
    slug: str
    pak_name: str
    name: str
    description: str
    uuid: str
    author: str
    version: str = "0.1.0"

    @property
    def folder(self) -> str:
        return f"{self.pak_name}_{self.uuid}"


def _attribute(parent: ET.Element, key: str, kind: str, value: str) -> None:
    ET.SubElement(parent, "attribute", id=key, type=kind, value=value)


def build_meta(mod: NewMod) -> bytes:
    save = ET.Element("save")
    ET.SubElement(save, "version", LSX_VERSION)
    region = ET.SubElement(save, "region", id="Config")
    children = ET.SubElement(ET.SubElement(region, "node", id="root"), "children")
    ET.SubElement(children, "node", id="Conflicts")
    ET.SubElement(children, "node", id="Dependencies")
    info = ET.SubElement(children, "node", id="ModuleInfo")
    version = str(version64(mod.version))
    for key, kind, value in (
        ("Author", "LSString", mod.author),
        ("CharacterCreationLevelName", "FixedString", ""),
        ("Description", "LSString", mod.description),
        ("FileSize", "uint64", "0"),
        ("Folder", "LSString", mod.folder),
        ("LobbyLevelName", "FixedString", ""),
        ("MD5", "LSString", ""),
        ("MenuLevelName", "FixedString", ""),
        ("Name", "LSString", mod.name),
        ("NumPlayers", "uint8", "4"),
        ("PhotoBooth", "FixedString", ""),
        ("StartupLevelName", "FixedString", ""),
        ("UUID", "FixedString", mod.uuid),
        ("Version64", "int64", version),
    ):
        _attribute(info, key, kind, value)
    publish = ET.SubElement(ET.SubElement(info, "children"), "node", id="PublishVersion")
    _attribute(publish, "Version64", "int64", version)
    ET.indent(save, space="    ")
    return (XML_DECLARATION + ET.tostring(save, encoding="unicode") + "\n").encode("utf-8")


def _render(template: str, mod: NewMod) -> str:
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    return Template(text).substitute(
        todo=TODO_MARK,
        mods_folder=PLAYER_MODS_FOLDER,
        name=mod.name,
        slug=mod.slug,
        pak_name=mod.pak_name,
    )


def readme_text(mod: NewMod) -> str:
    return _render("README.md", mod)


def checklist_text(mod: NewMod) -> str:
    return _render("TESTING.md", mod)
