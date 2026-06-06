#!/usr/bin/env python3
"""Generate the root skills.json install manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from skill_index import ROOT as REPO_ROOT, write_manifest  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate awskill's installable skill manifest.")
    parser.add_argument("--output", default=str(REPO_ROOT / "skills.json"), help="Manifest output path.")
    args = parser.parse_args(argv)

    output = Path(args.output)
    manifest = write_manifest(output)
    try:
        display_path = output.relative_to(REPO_ROOT)
    except ValueError:
        display_path = output
    print(f"Wrote {manifest['total']} skills to {display_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
