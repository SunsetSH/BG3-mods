import shutil
from pathlib import Path

import pytest

from bg3_mods import mods, paths

SHIPPED = mods.discover()


def test_both_known_mods_are_found() -> None:
    assert {"dc_check", "run_speed"} <= {mod.slug for mod in SHIPPED}


@pytest.mark.parametrize("mod", SHIPPED, ids=lambda mod: mod.slug)
def test_shipped_mod_has_no_problems(mod: mods.Mod) -> None:
    assert mods.mod_problems(mod) == []


def test_shipped_mods_have_unique_uuid_and_pak() -> None:
    assert mods.registry_problems(SHIPPED) == []


def test_pak_name_comes_from_module_folder() -> None:
    assert mods.get("dc_check").pak_name == "DCCheck"
    assert mods.get("run_speed").pak_name == "RunSpeed"


def test_get_unknown_mod_raises(tmp_path: Path) -> None:
    with pytest.raises(KeyError, match="no_such"):
        mods.get("no_such", tmp_path)


def _copy(mod: mods.Mod, root: Path, slug: str) -> mods.Mod:
    shutil.copytree(mod.root, root / slug, ignore=shutil.ignore_patterns("Localization"))
    return mods.get(slug, root)


def test_duplicate_uuid_is_reported(tmp_path: Path) -> None:
    original = mods.get("run_speed")
    copy = _copy(original, tmp_path, "run_speed_copy")
    assert any("already used" in p for p in mods.registry_problems([original, copy]))


def test_missing_installation_section_is_reported(tmp_path: Path) -> None:
    copy = _copy(mods.get("run_speed"), tmp_path, "run_speed")
    readme = copy.root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace("## Установка", "## Setup"), "utf-8"
    )
    assert mods.mod_problems(copy) == [f"{readme}: section '{mods.INSTALL_HEADING}' missing"]


def test_wrong_folder_name_is_reported(tmp_path: Path) -> None:
    copy = _copy(mods.get("run_speed"), tmp_path, "run_speed")
    copy.module_dir.rename(copy.module_dir.with_name("RunSpeed"))
    assert any("Folder" in p for p in mods.mod_problems(copy))


def test_bad_slug_is_reported(tmp_path: Path) -> None:
    copy = _copy(mods.get("run_speed"), tmp_path, "Run-Speed")
    assert mods.mod_problems(copy) == [f"{copy.root}: folder name must be snake_case"]


def test_missing_generated_part_names_the_command(tmp_path: Path) -> None:
    copy = _copy(mods.get("dc_check"), tmp_path, "dc_check")
    assert mods.missing_generated(copy) == mods.GENERATED["dc_check"][1]
    assert mods.missing_generated(mods.get("run_speed")) is None


INSTALL = f"""# X

## Установка

1. `X.pak` в `{paths.PLAYER_MODS_FOLDER}`.
2. Удаление: удалить `X.pak`.

## Сборка

DWrite.dll github.com/Norbyte/bg3se
"""


def test_complete_installation_has_no_problems() -> None:
    assert mods.installation_problems(INSTALL, "X", script_extender_mod=False) == []


def test_installation_names_the_pak() -> None:
    problems = mods.installation_problems(INSTALL, "Other", script_extender_mod=False)
    assert problems == [f"'{mods.INSTALL_HEADING}' does not mention 'Other.pak'"]


def test_script_extender_steps_count_only_inside_the_section() -> None:
    problems = mods.installation_problems(INSTALL, "X", script_extender_mod=True)
    assert len(problems) == len(mods.SCRIPT_EXTENDER_TERMS)


@pytest.mark.parametrize("mod", SHIPPED, ids=lambda mod: mod.slug)
def test_mod_is_listed_in_root_readme_and_plan(mod: mods.Mod) -> None:
    readme = (paths.ROOT / "README.md").read_text(encoding="utf-8")
    plan = (paths.ROOT / "docs" / "PLAN.md").read_text(encoding="utf-8")
    assert f"](mods/{mod.slug}/README.md)" in readme
    assert f"## {mod.info.name} (`{mod.slug}`)" in plan
