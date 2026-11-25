import xml.etree.ElementTree as ET
from pathlib import Path

from bg3_mods import mods
from bg3_mods.meta import read_module_info, version64
from bg3_mods.scaffold import TODO_MARK, NewMod, build_meta, checklist_text, readme_text

NEW = NewMod(
    slug="loot_glow",
    pak_name="LootGlow",
    name="Loot Glow",
    description="Highlights loot.",
    uuid="11111111-2222-3333-4444-555555555555",
    author="SunsetSH",
)


def _create(root: Path) -> mods.Mod:
    module_dir = root / NEW.slug / "pak" / "Mods" / NEW.folder
    module_dir.mkdir(parents=True)
    (module_dir / "meta.lsx").write_bytes(build_meta(NEW))
    (root / NEW.slug / "README.md").write_text(readme_text(NEW), encoding="utf-8")
    (root / NEW.slug / "TESTING.md").write_text(checklist_text(NEW), encoding="utf-8")
    return mods.get(NEW.slug, root)


def test_meta_reads_back(tmp_path: Path) -> None:
    info = _create(tmp_path).info
    assert (info.name, info.folder, info.uuid) == ("Loot Glow", NEW.folder, NEW.uuid)
    assert info.version64 == info.publish_version64 == version64("0.1.0")


def test_meta_has_the_attributes_of_a_shipped_mod(tmp_path: Path) -> None:
    shipped = mods.get("dc_check").module_dir / "meta.lsx"
    path = _create(tmp_path).module_dir / "meta.lsx"

    assert _attribute_ids(path) == _attribute_ids(shipped)
    assert read_module_info(path).description == NEW.description


def _attribute_ids(meta: Path) -> list[tuple[str | None, str | None]]:
    root = ET.parse(meta).getroot()  # noqa: S314 (repository file, not network input)
    return [(a.get("id"), a.get("type")) for a in root.iter("attribute")]


def test_new_mod_is_valid_except_template_text(tmp_path: Path) -> None:
    problems = mods.mod_problems(_create(tmp_path))
    assert problems
    assert all(TODO_MARK in problem for problem in problems)


def test_readme_template_has_installation_section() -> None:
    assert mods.installation_problems(readme_text(NEW), NEW.pak_name, False) == []
