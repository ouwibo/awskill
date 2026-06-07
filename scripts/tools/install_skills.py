#!/usr/bin/env python3
"""Install awskill skills into a flat AI-agent skills directory."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Tuple

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from skill_index import all_skills  # noqa: E402

TARGETS = {
    "claude": Path.home() / ".claude" / "skills",
    "codex": Path.home() / ".codex" / "skills",
}


def copy_skill(src: Path, dst: Path, force: bool) -> bool:
    if dst.exists():
        if not force:
            return False
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return True


def install_to(destination: Path, force: bool) -> Tuple[int, int]:
    destination.mkdir(parents=True, exist_ok=True)
    installed = 0
    skipped = 0
    for skill in all_skills(ROOT):
        src = ROOT / str(skill["path"])
        dst = destination / str(skill["name"])
        if copy_skill(src, dst, force):
            installed += 1
        else:
            skipped += 1
    return installed, skipped


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Install all awskill skills as a flat list.")
    parser.add_argument(
        "--target",
        choices=["claude", "codex", "all"],
        default="claude",
        help="Known destination to install into.",
    )
    parser.add_argument("--dest", type=Path, help="Custom destination directory; overrides --target.")
    parser.add_argument("--force", action="store_true", help="Replace existing installed skills.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    destinations = [args.dest] if args.dest else ([TARGETS[args.target]] if args.target != "all" else list(TARGETS.values()))

    for destination in destinations:
        installed, skipped = install_to(destination.expanduser(), args.force)
        print(f"{destination.expanduser()}: installed {installed}, skipped {skipped}, total {installed + skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
