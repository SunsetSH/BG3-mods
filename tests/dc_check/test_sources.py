from bg3_mods import mods
from bg3_mods.dc_check import sources


def test_language_dir_is_inside_extracted_pak() -> None:
    source = sources.LANGUAGE_SOURCES["Russian"]
    assert sources.language_dir("Russian") == source.extracted / "Localization" / "Russian"


def test_mod_language_dir_is_inside_module_folder() -> None:
    module_dir = mods.get(sources.SLUG).module_dir
    assert sources.mod_language_dir("English") == module_dir / "Localization" / "English"


def test_generated_part_is_the_localization_folder() -> None:
    path, command = mods.GENERATED[sources.SLUG]
    assert mods.get(sources.SLUG).module_dir / path == sources.mod_localization_dir()
    assert "dc_check_generate.py" in command
