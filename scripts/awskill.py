#!/usr/bin/env python3
"""
awskill - Skill Index & Launcher

Usage:
    python3 scripts/awskill.py --stats
    python3 scripts/awskill.py --list [--cat <category>]
    python3 scripts/awskill.py --search <query>
    python3 scripts/awskill.py --run <skill>
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
IGNORED_ROOT_DIRS = {".git", "scripts", "__pycache__"}


def extract_description(content):
    """Return the first description from a SKILL.md frontmatter block."""
    lines = content.splitlines()
    in_description = False

    for line in lines:
        if line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value not in {">-", ">", "|", ""}:
                return value
            in_description = True
            continue

        if in_description:
            if line.startswith("  ") and line.strip():
                return line.strip()
            if line and not line.startswith(" "):
                break

    return ""


def get_all_skills():
    skills = []
    for category_path in sorted(p for p in BASE.iterdir() if p.is_dir()):
        if category_path.name in IGNORED_ROOT_DIRS:
            continue

        for skill_path in sorted(p for p in category_path.iterdir() if p.is_dir()):
            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                continue

            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            scripts_path = skill_path / "scripts"
            scripts = sorted(os.listdir(scripts_path)) if scripts_path.is_dir() else []
            skills.append(
                {
                    "name": skill_path.name,
                    "category": category_path.name,
                    "desc": extract_description(content),
                    "scripts": scripts,
                    "path": str(skill_path),
                }
            )
    return skills


def cmd_list(cat_filter=None):
    skills = get_all_skills()
    current_cat = None
    for skill in skills:
        if cat_filter and cat_filter.lower() not in skill["category"].lower():
            continue
        if skill["category"] != current_cat:
            print(f"\n{'=' * 60}")
            print(f"  {skill['category']}")
            print(f"{'=' * 60}")
            current_cat = skill["category"]
        has_scripts = f"[{len(skill['scripts'])} script(s)]" if skill["scripts"] else ""
        print(f"  {skill['name']:<45} {has_scripts}")
        if skill["desc"]:
            print(f"    {skill['desc'][:80]}")


def cmd_search(query):
    skills = get_all_skills()
    q = query.lower()
    print(f"\nSearch results for '{query}':\n")
    found = 0
    for skill in skills:
        if q in skill["name"].lower() or q in skill["desc"].lower() or q in skill["category"].lower():
            print(f"  [{skill['category']}] {skill['name']}")
            print(f"    {skill['desc'][:80]}")
            found += 1
    print(f"\n{found} skills found.")


def cmd_stats():
    skills = get_all_skills()
    categories = {}
    for skill in skills:
        categories[skill["category"]] = categories.get(skill["category"], 0) + 1
    print(f"\nTotal: {len(skills)} skills\n")
    for category, total in sorted(categories.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {total:>3}  {category}")


def cmd_run(skill_name):
    skills = get_all_skills()
    match = [skill for skill in skills if skill["name"] == skill_name]
    if not match:
        print(f"Skill '{skill_name}' not found. Use --search to find it.")
        return 1

    skill = match[0]
    print(f"\nRunning skill: {skill['name']}")
    print(f"Category: {skill['category']}")
    print(f"Path: {skill['path']}\n")
    scripts_path = Path(skill["path"]) / "scripts"
    if scripts_path.is_dir():
        for script_name in sorted(os.listdir(scripts_path)):
            script_path = scripts_path / script_name
            if script_name.endswith(".ts"):
                print(f"Script: {script_name}")
                return subprocess.run(["bun", str(script_path), "--help"], cwd=scripts_path).returncode
            if script_name.endswith(".py"):
                print(f"Script: {script_name}")
                return subprocess.run([sys.executable, str(script_path), "--help"], cwd=scripts_path).returncode
        print("No runnable Python or TypeScript scripts found.")
    else:
        print("No scripts — skill uses built-in tools. Read SKILL.md:")
        print((Path(skill["path"]) / "SKILL.md").read_text(encoding="utf-8", errors="ignore")[:500])
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Browse, search, and run awskill skills.")
    parser.add_argument("query", nargs="*", help="Search terms used when no explicit command is provided.")
    parser.add_argument("--stats", action="store_true", help="Show repository skill counts.")
    parser.add_argument("--list", action="store_true", help="List skills, optionally filtered by --cat.")
    parser.add_argument("--cat", help="Filter the skill list by category.")
    parser.add_argument("--search", help="Search skills by name, category, or description.")
    parser.add_argument("--run", help="Run the first helper script for an exact skill name.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    if args.stats or not any([args.list, args.cat, args.search, args.run, args.query]):
        cmd_stats()
        return 0
    if args.list or args.cat:
        cmd_list(args.cat)
        return 0
    if args.search is not None:
        cmd_search(args.search)
        return 0
    if args.run is not None:
        return cmd_run(args.run)

    cmd_search(" ".join(args.query))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
