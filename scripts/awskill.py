#!/usr/bin/env python3
"""
awskill - Skill Index & Launcher
Usage: python3 scripts/awskill.py [--list] [--cat <category>] [--search <query>] [--run <skill>]
"""
import os, sys, re, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_all_skills():
    skills = []
    for cat in sorted(os.listdir(BASE)):
        cat_path = os.path.join(BASE, cat)
        if not os.path.isdir(cat_path) or cat == "scripts": continue
        for skill in sorted(os.listdir(cat_path)):
            skill_path = os.path.join(cat_path, skill)
            if not os.path.isdir(skill_path): continue
            skill_md = os.path.join(skill_path, "SKILL.md")
            if not os.path.exists(skill_md): continue
            content = open(skill_md, errors='ignore').read()
            desc = ""
            in_block = False
            for line in content.split('\n'):
                if line.startswith('description:'):
                    val = line[12:].strip()
                    if val not in ['>-', '>', '|', '']:
                        desc = val; break
                    else: in_block = True
                elif in_block and line.startswith('  '):
                    desc = line.strip(); break
            scripts = []
            sc = os.path.join(skill_path, "scripts")
            if os.path.isdir(sc): scripts = os.listdir(sc)
            skills.append({"name": skill, "category": cat, "desc": desc, "scripts": scripts, "path": skill_path})
    return skills

def cmd_list(cat_filter=None):
    skills = get_all_skills()
    current_cat = None
    for s in skills:
        if cat_filter and cat_filter.lower() not in s["category"].lower(): continue
        if s["category"] != current_cat:
            print(f"\n{'='*60}")
            print(f"  {s['category']}")
            print(f"{'='*60}")
            current_cat = s["category"]
        has_scripts = f"[{len(s['scripts'])} script(s)]" if s['scripts'] else ""
        print(f"  {s['name']:<45} {has_scripts}")
        if s['desc']:
            print(f"    {s['desc'][:80]}")

def cmd_search(query):
    skills = get_all_skills()
    q = query.lower()
    print(f"\nSearch results for '{query}':\n")
    found = 0
    for s in skills:
        if q in s['name'].lower() or q in s['desc'].lower() or q in s['category'].lower():
            print(f"  [{s['category']}] {s['name']}")
            print(f"    {s['desc'][:80]}")
            found += 1
    print(f"\n{found} skills found.")

def cmd_stats():
    skills = get_all_skills()
    cats = {}
    for s in skills:
        cats[s['category']] = cats.get(s['category'], 0) + 1
    print(f"\nTotal: {len(skills)} skills\n")
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {n:>3}  {c}")

def cmd_run(skill_name):
    skills = get_all_skills()
    match = [s for s in skills if s['name'] == skill_name]
    if not match:
        print(f"Skill '{skill_name}' not found. Use --search to find it.")
        return
    s = match[0]
    print(f"\nRunning skill: {s['name']}")
    print(f"Category: {s['category']}")
    print(f"Path: {s['path']}\n")
    sc = os.path.join(s['path'], 'scripts')
    if os.path.isdir(sc):
        for f in sorted(os.listdir(sc)):
            fp = os.path.join(sc, f)
            if f.endswith('.ts'):
                print(f"Script: {f}")
                subprocess.run(['bun', fp, '--help'], cwd=sc)
                break
            elif f.endswith('.py'):
                print(f"Script: {f}")
                subprocess.run([sys.executable, fp, '--help'], cwd=sc)
                break
    else:
        print("No scripts — skill uses built-in tools. Read SKILL.md:")
        print(open(os.path.join(s['path'], 'SKILL.md'), errors='ignore').read()[:500])

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or '--stats' in args:
        cmd_stats()
    elif '--list' in args:
        cat = args[args.index('--list')+1] if '--cat' in args else None
        cmd_list(cat)
    elif '--search' in args:
        idx = args.index('--search')
        cmd_search(args[idx+1] if idx+1 < len(args) else '')
    elif '--run' in args:
        idx = args.index('--run')
        cmd_run(args[idx+1] if idx+1 < len(args) else '')
    elif '--cat' in args:
        idx = args.index('--cat')
        cmd_list(args[idx+1] if idx+1 < len(args) else None)
    else:
        cmd_search(' '.join(args))
