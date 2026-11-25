"""Full check: lint, format, types, tests. Exit code 0 means done."""

import subprocess
import sys

STEPS: list[tuple[str, list[str]]] = [
    ("ruff lint", ["ruff", "check", "."]),
    ("ruff format", ["ruff", "format", "--check", "."]),
    ("mypy", ["mypy"]),
    ("pytest", ["pytest"]),
]


def main() -> int:
    failed: list[str] = []
    for name, command in STEPS:
        print(f"== {name}: {' '.join(command)}", flush=True)
        if subprocess.run(command, check=False).returncode != 0:
            failed.append(name)
    if failed:
        print(f"FAILED: {', '.join(failed)}", file=sys.stderr)
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
