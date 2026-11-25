"""Extract a game .pak from the BG3 Data folder into unpacked/<pak name>/.

Usage: uv run python scripts/unpack_game.py <Pak.pak> [glob filter]
Example: uv run python scripts/unpack_game.py Gustav.pak "*DifficultyClasses*"
"""

import argparse
import sys

from bg3_mods import divine, paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pak", help="file name inside the game Data folder, e.g. Gustav.pak")
    parser.add_argument("expression", nargs="?", help="glob filter for files inside the pak")
    args = parser.parse_args()

    package = paths.game_data_dir() / args.pak
    if not package.is_file():
        print(f"Not found: {package}. Set BG3_DIR if the game lives elsewhere.", file=sys.stderr)
        return 1
    destination = paths.UNPACKED_DIR / package.stem
    divine.run(divine.extract_command(package, destination, args.expression))
    print(f"Extracted to: {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
