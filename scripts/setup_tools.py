"""Download LSLib (Divine CLI) into tools/lslib and verify its SHA256."""

import hashlib
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

LSLIB_VERSION = "v1.20.4"
LSLIB_URL = (
    f"https://github.com/Norbyte/lslib/releases/download/{LSLIB_VERSION}/"
    f"ExportTool-{LSLIB_VERSION}.zip"
)
LSLIB_SHA256 = "5e02368fb8acafda9b45acba37a3f3bf507fc3d65a083a159abbeab06337190e"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "tools" / "lslib"
STAMP = TARGET / "VERSION"


def main() -> int:
    if STAMP.is_file() and STAMP.read_text(encoding="utf-8").strip() == LSLIB_VERSION:
        print(f"LSLib {LSLIB_VERSION} already in {TARGET}")
        return 0

    print(f"Downloading {LSLIB_URL}")
    with urllib.request.urlopen(LSLIB_URL, timeout=120) as response:
        payload: bytes = response.read()

    digest = hashlib.sha256(payload).hexdigest()
    if digest != LSLIB_SHA256:
        print(f"SHA256 mismatch: expected {LSLIB_SHA256}, got {digest}", file=sys.stderr)
        return 1

    TARGET.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for member in archive.namelist():
            resolved = (TARGET / member).resolve()
            if not resolved.is_relative_to(TARGET.resolve()):
                print(f"Unsafe path in archive: {member}", file=sys.stderr)
                return 1
        archive.extractall(TARGET)

    STAMP.write_text(LSLIB_VERSION, encoding="utf-8")
    divine = next(TARGET.rglob("Divine.exe"), None)
    print(f"LSLib {LSLIB_VERSION} ready: {divine}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
