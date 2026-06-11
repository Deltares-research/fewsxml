import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Backward-compatible entry point; prefer running `python -m pytest`."""
    tests_dir = Path(__file__).resolve().parent
    project_root = tests_dir.parents[1]
    return subprocess.run(
        [sys.executable, "-m", "pytest", str(tests_dir), *sys.argv[1:]],
        cwd=project_root,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
