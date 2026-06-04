#!/usr/bin/env python3
"""Validate awskill repository metadata and skill files."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IGNORED_DIRS = {".git", "__pycache__"}
REQUIRED_FRONTMATTER_FIELDS = ("name", "description")


def iter_skill_dirs():
    for skill_md in sorted(ROOT.glob("*/*/SKILL.md")):
        if any(part in IGNORED_DIRS for part in skill_md.parts):
            continue
        yield skill_md.parent


def parse_frontmatter(skill_md):
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---\n"):
        return None, None, "missing opening frontmatter delimiter"

    try:
        raw_frontmatter, body = text[4:].split("\n---", 1)
    except ValueError:
        return None, None, "missing closing frontmatter delimiter"

    data = {}
    for line in raw_frontmatter.splitlines():
        if not line.strip() or line.startswith(" "):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data, body, None


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


def main():
    skill_dirs = list(iter_skill_dirs())
    failures = []
    categories = {}

    for skill_dir in skill_dirs:
        category = skill_dir.parent.name
        categories[category] = categories.get(category, 0) + 1
        issues = validate_skill(skill_dir)
        if issues:
            failures.append((skill_dir.relative_to(ROOT), issues))

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
