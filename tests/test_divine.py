from pathlib import Path

from bg3_mods import divine


def test_pack_command_targets_bg3() -> None:
    command = divine.pack_command(Path("src"), Path("out.pak"))
    assert command[0] == str(divine.DIVINE)
    assert command[command.index("--game") + 1] == "bg3"
    assert command[command.index("--action") + 1] == "create-package"


def test_extract_command_adds_filter_only_when_given() -> None:
    without = divine.extract_command(Path("a.pak"), Path("out"), None)
    with_filter = divine.extract_command(Path("a.pak"), Path("out"), "*.lsx")
    assert "--expression" not in without
    assert with_filter[-2:] == ["--expression", "*.lsx"]


def test_parse_listing_skips_log_lines() -> None:
    output = "[INFO] Opening package\nMods/X/meta.lsx\t1842\t0\nPublic/X/a.lsx\t10\t0\n"
    assert divine.parse_listing(output) == ["Mods/X/meta.lsx", "Public/X/a.lsx"]


def test_parse_listing_empty_package() -> None:
    assert divine.parse_listing("[INFO] Opening package\n") == []


def test_convert_resources_command_is_lsf_to_lsx() -> None:
    command = divine.convert_resources_command(Path("in"), Path("out"))
    assert command[command.index("--action") + 1] == "convert-resources"
    assert command[command.index("--input-format") + 1] == "lsf"
    assert command[command.index("--output-format") + 1] == "lsx"


def test_convert_loca_command_passes_paths() -> None:
    command = divine.convert_loca_command(Path("a.loca"), Path("a.xml"))
    assert command[command.index("--action") + 1] == "convert-loca"
    assert command[-4:] == ["--source", "a.loca", "--destination", "a.xml"]
