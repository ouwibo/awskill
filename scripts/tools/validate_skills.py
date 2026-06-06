#!/usr/bin/env python3
"""Validate awskill repository metadata and skill files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from skill_index import REQUIRED_FRONTMATTER_FIELDS, all_skills, category_counts, iter_skill_dirs, parse_frontmatter  # noqa: E402


def validate_skill(skill_dir):
    issues = []
    skill_md = skill_dir / "SKILL.md"
    frontmatter, body, error = parse_frontmatter(skill_md)
    if error:
        issues.append(error)
        return issues

    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in frontmatter or not frontmatter[field]:
            issues.append(f"missing required frontmatter field: {field}")

    if body and body.lstrip().startswith("---\n"):
        issues.append("contains duplicate frontmatter block after the header")

    display_json = skill_dir / "DISPLAY.json"
    if display_json.exists():
        try:
            json.loads(display_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid DISPLAY.json: {exc}")

    return issues


def validate_manifest(skills):
    manifest_path = ROOT / "skills.json"
    if not manifest_path.exists():
        return ["missing root skills.json manifest; run scripts/tools/generate_manifest.py"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid skills.json: {exc}"]

    issues = []
    if manifest.get("total") != len(skills):
        issues.append(f"skills.json total is {manifest.get('total')}, expected {len(skills)}")
    manifest_names = [skill.get("name") for skill in manifest.get("skills", [])]
    actual_names = [skill["name"] for skill in skills]
    if sorted(manifest_names) != sorted(actual_names):
        issues.append("skills.json skill names do not match repository skills")
    return issues


def main():
    skill_dirs = list(iter_skill_dirs(ROOT))
    skills = all_skills(ROOT)
    failures = []
    categories = category_counts(skills)

    for skill_dir in skill_dirs:
        issues = validate_skill(skill_dir)
        if issues:
            failures.append((skill_dir.relative_to(ROOT), issues))

    manifest_issues = validate_manifest(skills)
    if manifest_issues:
        failures.append((Path("skills.json"), manifest_issues))

    print(f"Validated {len(skill_dirs)} skills across {len(categories)} categories.")
    for category, total in sorted(categories.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {total:>3}  {category}")

    if failures:
        print("\nIssues:")
        for skill_dir, issues in failures:
            for issue in issues:
                print(f"  - {skill_dir}: {issue}")
        return 1

    print("\nAll skill metadata checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
