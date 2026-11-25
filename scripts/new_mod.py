"""Create a new mod in mods/<slug>/: meta.lsx with a fresh UUID, README and TESTING templates.

Usage: uv run python scripts/new_mod.py <slug> <PakName> "<Name in game>" "<English description>"
Example: uv run python scripts/new_mod.py loot_glow LootGlow "Loot Glow" "Highlights loot."
"""

import argparse
import sys
import uuid

from bg3_mods import mods, paths
from bg3_mods.scaffold import TODO_MARK, NewMod, build_meta, checklist_text, readme_text

AUTHOR = "SunsetSH"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slug", help="snake_case folder name in mods/, e.g. loot_glow")
    parser.add_argument("pak_name", help="PascalCase .pak and module folder prefix, e.g. LootGlow")
    parser.add_argument("name", help="name shown in the game mod manager")
    parser.add_argument("description", help="English description for meta.lsx")
    args = parser.parse_args()

    if not mods.SLUG.match(args.slug) or not mods.PAK_NAME.match(args.pak_name):
        print("slug must be snake_case, pak_name PascalCase ASCII", file=sys.stderr)
        return 1
    root = paths.MODS_DIR / args.slug
    taken = {mod.pak_name.lower() for mod in mods.discover()}
    if root.exists() or args.pak_name.lower() in taken:
        print(f"Mod {args.slug} or pak {args.pak_name} already exists", file=sys.stderr)
        return 1

    mod = NewMod(args.slug, args.pak_name, args.name, args.description, str(uuid.uuid4()), AUTHOR)
    module_dir = root / "pak" / "Mods" / mod.folder
    module_dir.mkdir(parents=True)
    (module_dir / "meta.lsx").write_bytes(build_meta(mod))
    (root / "README.md").write_text(readme_text(mod), encoding="utf-8")
    (root / "TESTING.md").write_text(checklist_text(mod), encoding="utf-8")
    print(f"Created {root} (UUID {mod.uuid}, version {mod.version})")
    print(f"Next: replace every '{TODO_MARK}' in README.md and TESTING.md, add an ADR,")
    print("a section in docs/PLAN.md and a row in the README mods table.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
