#!/usr/bin/env python3
"""Shared awskill discovery, metadata, and manifest helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator, List

ROOT = Path(__file__).resolve().parents[1]
IGNORED_ROOT_DIRS = {".git", ".github", "scripts", "dist", "__pycache__"}
REQUIRED_FRONTMATTER_FIELDS = ("name", "description")


def parse_frontmatter(skill_md: Path):
    """Parse simple YAML-like frontmatter from a SKILL.md file."""
    text = skill_md.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---\n"):
        return None, None, "missing opening frontmatter delimiter"

    try:
        raw_frontmatter, body = text[4:].split("\n---", 1)
    except ValueError:
        return None, None, "missing closing frontmatter delimiter"

    data: Dict[str, str] = {}
    current_key = None
    current_lines: List[str] = []

    def flush_multiline():
        nonlocal current_key, current_lines
        if current_key:
            data[current_key] = " ".join(line.strip() for line in current_lines if line.strip()).strip()
            current_key = None
            current_lines = []

    for line in raw_frontmatter.splitlines():
        if current_key and (line.startswith(" ") or not line.strip()):
            current_lines.append(line)
            continue

        flush_multiline()
        if not line.strip() or line.startswith(" ") or ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {">-", ">", "|"}:
            current_key = key
            current_lines = []
        else:
            data[key] = value

    flush_multiline()
    return data, body, None


def iter_skill_dirs(root: Path = ROOT) -> Iterator[Path]:
    """Yield skill directories from the category/skill repository layout."""
    for skill_md in sorted(root.glob("*/*/SKILL.md")):
        rel_parts = skill_md.relative_to(root).parts
        if rel_parts[0] in IGNORED_ROOT_DIRS:
            continue
        yield skill_md.parent


def skill_metadata(skill_dir: Path, root: Path = ROOT) -> Dict[str, object]:
    """Return normalized metadata for one skill directory."""
    skill_md = skill_dir / "SKILL.md"
    frontmatter, _body, _error = parse_frontmatter(skill_md)
    frontmatter = frontmatter or {}
    scripts_path = skill_dir / "scripts"
    scripts = sorted(p.name for p in scripts_path.iterdir()) if scripts_path.is_dir() else []
    rel_path = skill_dir.relative_to(root)
    files = sorted(str(p.relative_to(skill_dir)) for p in skill_dir.rglob("*") if p.is_file())

    return {
        "name": skill_dir.name,
        "title": frontmatter.get("name", skill_dir.name),
        "description": frontmatter.get("description", ""),
        "category": rel_path.parts[0] if len(rel_path.parts) > 1 else "Uncategorized",
        "path": str(rel_path),
        "scripts": scripts,
        "files": files,
    }


def all_skills(root: Path = ROOT) -> List[Dict[str, object]]:
    """Return all skills with normalized metadata."""
    return [skill_metadata(skill_dir, root) for skill_dir in iter_skill_dirs(root)]


def category_counts(skills: List[Dict[str, object]]) -> Dict[str, int]:
    """Return skill counts grouped by category."""
    counts: Dict[str, int] = {}
    for skill in skills:
        category = str(skill["category"])
        counts[category] = counts.get(category, 0) + 1
    return counts


def write_manifest(path: Path, root: Path = ROOT) -> Dict[str, object]:
    """Write a deterministic install manifest and return it."""
    skills = all_skills(root)
    manifest = {
        "schema": "https://github.com/ouwibo/awskill/schema/skills-manifest-v1.json",
        "total": len(skills),
        "categories": category_counts(skills),
        "skills": skills,
    }
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest
