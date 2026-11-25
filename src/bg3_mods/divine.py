"""Thin wrapper over LSLib's Divine CLI: command lines and runs."""

import subprocess
from pathlib import Path

from bg3_mods.paths import TOOLS_DIR

DIVINE = TOOLS_DIR / "lslib" / "Packed" / "Tools" / "Divine.exe"


def pack_command(source: Path, destination: Path) -> list[str]:
    return [
        str(DIVINE),
        "--game", "bg3",
        "--action", "create-package",
        "--source", str(source),
        "--destination", str(destination),
    ]  # fmt: skip


def extract_command(package: Path, destination: Path, expression: str | None) -> list[str]:
    command = [
        str(DIVINE),
        "--game", "bg3",
        "--action", "extract-package",
        "--source", str(package),
        "--destination", str(destination),
    ]  # fmt: skip
    if expression:
        command += ["--expression", expression]
    return command


def convert_resources_command(source: Path, destination: Path) -> list[str]:
    """Batch-convert every .lsf under source into .lsx under destination, keeping the tree."""
    return [
        str(DIVINE),
        "--game", "bg3",
        "--action", "convert-resources",
        "--source", str(source),
        "--destination", str(destination),
        "--input-format", "lsf",
        "--output-format", "lsx",
    ]  # fmt: skip


def convert_loca_command(source: Path, destination: Path) -> list[str]:
    """Convert one .loca file to .xml (the direction follows the file extensions)."""
    return [
        str(DIVINE),
        "--game", "bg3",
        "--action", "convert-loca",
        "--source", str(source),
        "--destination", str(destination),
    ]  # fmt: skip


def list_command(package: Path) -> list[str]:
    return [str(DIVINE), "--game", "bg3", "--action", "list-package", "--source", str(package)]


def parse_listing(output: str) -> list[str]:
    """Paths from `list-package` output; lines are `path<TAB>size<TAB>crc`, log lines start '['."""
    return [
        line.split("\t", 1)[0]
        for line in output.splitlines()
        if "\t" in line and not line.startswith("[")
    ]


def _ensure_divine() -> None:
    if not DIVINE.is_file():
        msg = f"Divine.exe not found at {DIVINE}. Run: uv run python scripts/setup_tools.py"
        raise FileNotFoundError(msg)


def run(command: list[str]) -> None:
    _ensure_divine()
    subprocess.run(command, check=True)  # noqa: S603 (argument list, no shell)


def list_package(package: Path) -> list[str]:
    _ensure_divine()
    result = subprocess.run(  # noqa: S603 (argument list, no shell)
        list_command(package), check=True, capture_output=True, text=True
    )
    return parse_listing(result.stdout)
