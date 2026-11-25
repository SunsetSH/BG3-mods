from bg3_mods import paths
from bg3_mods.gamedata import Source, converted_lsx


def test_source_extracts_into_folder_named_after_pak() -> None:
    source = Source("Localization/Russian/Russian.pak", "*.loca")
    assert source.extracted == paths.UNPACKED_DIR / "Russian"


def test_stamps_differ_per_filter_of_same_pak() -> None:
    dialogs = Source("Gustav.pak", "*/Story/DialogsBinary/*")
    difficulty = Source("Gustav.pak", "*/DifficultyClasses/DifficultyClasses.lsx")
    assert dialogs.stamp != difficulty.stamp
    assert not any(part.startswith(".") for part in dialogs.stamp.relative_to(paths.ROOT).parts)


def test_converted_lsx_live_apart_from_extracted_files() -> None:
    source = Source("Gustav.pak", "*/Story/DialogsBinary/*")
    assert converted_lsx(source) == paths.UNPACKED_DIR / "lsx" / "Gustav"
