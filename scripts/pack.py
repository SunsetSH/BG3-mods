"""Pack a mod into paks/<Pak>.pak and create a ZIP in build/ for upload.

Usage: uv run python scripts/pack.py <slug>   (a folder in mods/, e.g. dc_check)
Divine skips every file whose absolute path has a dot-folder (the repo lives in H:\\.pet\\),
so the mod source is staged into the system temp folder first. See docs/NOTES.md.
"""

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from bg3_mods import divine, mods, paths


def pack(source: Path, pak_name: str, version: str) -> int:
    destination = paths.PAKS_DIR / pak_name
    expected = sorted(p.relative_to(source).as_posix() for p in source.rglob("*") if p.is_file())

    with tempfile.TemporaryDirectory(prefix="bg3mod_") as temp:
        staged = Path(temp) / "mod"
        if any(part.startswith(".") for part in staged.parts):
            print(f"Temp path has a dot-folder, Divine will skip it: {staged}", file=sys.stderr)
            return 1
        shutil.copytree(source, staged)
        staged_pak = Path(temp) / pak_name
        divine.run(divine.pack_command(staged, staged_pak))
        packed = sorted(divine.list_package(staged_pak))
        if packed != expected:
            print(
                f"Package content mismatch.\nexpected: {expected}\npacked:   {packed}",
                file=sys.stderr,
            )
            return 1
        paths.PAKS_DIR.mkdir(exist_ok=True)
        shutil.copyfile(staged_pak, destination)

    print(f"Packed {len(packed)} file(s): {destination}")

    paths.BUILD_DIR.mkdir(exist_ok=True)
    archive = paths.BUILD_DIR / f"{Path(pak_name).stem}-{version}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.write(destination, pak_name)
    print(f"Upload archive: {archive}")
    return 0


def pack_mod(mod: mods.Mod) -> int:
    problems = mods.mod_problems(mod)
    if problems:
        print(f"Mod {mod.slug} is broken:\n" + "\n".join(problems), file=sys.stderr)
        return 1
    command = mods.missing_generated(mod)
    if command:
        print(f"Generated files of {mod.slug} are missing. Run: {command}", file=sys.stderr)
        return 1
    return pack(mod.pak_source, f"{mod.pak_name}.pak", mod.info.version)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    slugs = [mod.slug for mod in mods.discover()]
    parser.add_argument("mod", choices=slugs, help="folder in mods/")
    args = parser.parse_args()
    return pack_mod(mods.get(args.mod))


if __name__ == "__main__":
    sys.exit(main())
