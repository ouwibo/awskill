#!/usr/bin/env python3
"""Export all category-nested skills into one flat skills directory."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from skill_index import all_skills, write_manifest  # noqa: E402


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Copy every skill out of category folders into one flat directory.")
    parser.add_argument("--dest", type=Path, default=ROOT / "dist" / "skills", help="Flat export directory.")
    parser.add_argument("--clean", action="store_true", help="Delete the destination before exporting.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    dest = args.dest.expanduser()
    if args.clean and dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    copied = 0
    for skill in all_skills(ROOT):
        src = ROOT / str(skill["path"])
        target = dest / str(skill["name"])
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(src, target)
        copied += 1

    manifest = write_manifest(dest / "skills.json")
    print(f"Exported {copied} skills to {dest}")
    print(f"Wrote flat manifest with {manifest['total']} entries to {dest / 'skills.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
