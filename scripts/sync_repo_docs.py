#!/usr/bin/env python3
"""Sync docs from the OptoFly ecosystem's component repos into docs/repos/.

Run before `mkdocs serve` or `mkdocs build` — the copied content is
gitignored and regenerated fresh every time, so it never drifts from the
source repos and is never committed here.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_REPOS = REPO_ROOT / "docs" / "repos"

# (github repo name, relative source path to copy, relative dest path under docs/repos/)
SYNC_TARGETS = [
    ("optofly", "docs", "optofly", {"superpowers"}),
    ("liquid-lens-calibration", "README.md", "liquid-lens-calibration/README.md", None),
    ("basler-charuco-calibrator", "README.md", "basler-charuco-calibrator/README.md", None),
    ("optotune-lens", "README.md", "optotune-lens/README.md", None),
    ("ximea-py", "README.md", "ximea-py/README.md", None),
    ("ximea-py", "examples", "ximea-py/examples", None),
]


def clone_shallow(repo_name: str, dest: Path) -> None:
    url = f"https://github.com/mpinb/{repo_name}.git"
    subprocess.run(
        ["git", "clone", "--depth", "1", url, str(dest)],
        check=True,
        timeout=120,
    )


def copy_target(src_root: Path, rel_src: str, rel_dest: Path, exclude_dirs: set[str] | None) -> None:
    src = src_root / rel_src
    dest = DOCS_REPOS / rel_dest
    if src.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if exclude_dirs and item.name in exclude_dirs:
                continue
            target = dest / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def main() -> int:
    if DOCS_REPOS.exists():
        shutil.rmtree(DOCS_REPOS)
    DOCS_REPOS.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        cloned: set[str] = set()
        for repo_name, rel_src, rel_dest, exclude_dirs in SYNC_TARGETS:
            clone_dest = tmp_path / repo_name
            try:
                if repo_name not in cloned:
                    print(f"Cloning {repo_name}...")
                    clone_shallow(repo_name, clone_dest)
                    cloned.add(repo_name)
                copy_target(clone_dest, rel_src, Path(rel_dest), exclude_dirs)
            except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
                raise RuntimeError(f"failed to sync docs from {repo_name}: {exc}") from exc
            print(f"  -> docs/repos/{rel_dest}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
