#!/usr/bin/env python3
"""
install.sh — awskill toolkit installer
Installs all bug bounty + crypto scanners and registers skills/commands.
Usage: python3 scripts/tools/install.py [--tools] [--skills] [--all]
"""
import os, sys, subprocess, shutil, platform

GOBIN = os.path.expanduser("~/go/bin")
os.makedirs(GOBIN, exist_ok=True)

ARCH = "amd64" if platform.machine() == "x86_64" else "arm64"
OS = "linux" if sys.platform.startswith("linux") else "darwin"

TOOLS = {
    "subfinder": f"https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_{OS}_{ARCH}.zip",
    "httpx":     f"https://github.com/projectdiscovery/httpx/releases/download/v1.6.10/httpx_1.6.10_{OS}_{ARCH}.zip",
    "nuclei":    f"https://github.com/projectdiscovery/nuclei/releases/download/v3.3.9/nuclei_3.3.9_{OS}_{ARCH}.zip",
    "katana":    f"https://github.com/projectdiscovery/katana/releases/download/v1.1.2/katana_1.1.2_{OS}_{ARCH}.zip",
    "dnsx":      f"https://github.com/projectdiscovery/dnsx/releases/download/v1.2.1/dnsx_1.2.1_{OS}_{ARCH}.zip",
    "gau":       f"https://github.com/lc/gau/releases/download/v2.2.3/gau_{OS}_{ARCH}.tar.gz",
    "ffuf":      f"https://github.com/ffuf/ffuf/releases/download/v2.1.0/ffuf_2.1.0_{OS}_{ARCH}.tar.gz",
    "nmap":      None,  # via apt/brew
    "amass":     f"https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_{OS}_{ARCH}.zip",
    "waybackurls": None,  # go install
    "anew":      None,  # go install
    "qsreplace": None,  # go install
    "dalfox":    f"https://github.com/hahwul/dalfox/releases/download/v2.9.2/dalfox_{OS}_{ARCH}.tar.gz",
    "sqlmap":    None,  # pip
    "trufflehog": f"https://github.com/trufflesecurity/trufflehog/releases/download/v3.88.2/trufflehog_{OS}_{ARCH}.tar.gz",
    "gitleaks":  f"https://github.com/gitleaks/gitleaks/releases/download/v8.24.3/gitleaks_8.24.3_{OS}_{ARCH}.tar.gz",
    "crapi":     None,  # docker
    "interactsh-client": f"https://github.com/projectdiscovery/interactsh/releases/download/v1.2.1/interactsh-client_1.2.1_{OS}_{ARCH}.zip",
    "wapiti":    None,  # pip
    "arjun":     None,  # pip
}

GO_TOOLS = {
    "waybackurls": "github.com/tomnomnom/waybackurls@latest",
    "anew":        "github.com/tomnomnom/anew@latest",
    "qsreplace":   "github.com/tomnomnom/qsreplace@latest",
}

PIP_TOOLS = {
    "sqlmap": "sqlmap",
    "wapiti": "wapiti3",
    "arjun":  "arjun",
}

APT_TOOLS = ["nmap", "ffuf", "git", "curl", "unzip"]

def run(cmd, capture=True):
    r = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    return r.returncode == 0, r.stdout + r.stderr

def ok(msg): print(f"  \033[92m[+]\033[0m {msg}")
def fail(msg): print(f"  \033[91m[-]\033[0m {msg}")
def info(msg): print(f"  \033[94m[*]\033[0m {msg}")

def install_apt():
    info("Installing system packages...")
    s, o = run(f"apt-get install -y {' '.join(APT_TOOLS)} 2>/dev/null || brew install {' '.join(APT_TOOLS)} 2>/dev/null")
    ok("System packages done") if s else fail("Some apt packages failed (non-critical)")

def install_binary(name, url):
    if not url: return False
    info(f"Downloading {name}...")
    tmp = f"/tmp/{name}_dl"
    s, _ = run(f"curl -fsSL '{url}' -o {tmp}")
    if not s: return False
    if url.endswith('.zip'):
        run(f"unzip -o {tmp} -d {GOBIN} {name} 2>/dev/null")
    elif url.endswith('.tar.gz'):
        run(f"tar -xzf {tmp} -C {GOBIN} {name} 2>/dev/null || tar -xzf {tmp} -C {GOBIN}")
    run(f"chmod +x {GOBIN}/{name}")
    exists = os.path.exists(f"{GOBIN}/{name}")
    ok(f"{name} installed") if exists else fail(f"{name} binary extract failed")
    return exists

def install_go_tools():
    go_path = shutil.which("go") or "/usr/local/go/bin/go"
    if not os.path.exists(go_path):
        fail("Go not found — fix: curl -fsSL https://go.dev/dl/go1.23.8.linux-amd64.tar.gz | tar -C /usr/local -xz")
        return
    env = f"GOPATH={os.path.expanduser('~')}/go PATH={GOBIN}:{os.environ.get('PATH','')}"
    for name, pkg in GO_TOOLS.items():
        info(f"go install {name}...")
        s, _ = run(f"{env} {go_path} install {pkg}")
        ok(name) if s else fail(f"{name} — fix: {go_path} install {pkg}")

def install_pip_tools():
    for name, pkg in PIP_TOOLS.items():
        info(f"pip install {name}...")
        s, _ = run(f"pip3 install {pkg} -q")
        ok(name) if s else fail(f"{name} — fix: pip3 install {pkg}")

def install_skills():
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    skills_dst = os.path.expanduser("~/.claude/skills")
    cmds_dst = os.path.expanduser("~/.claude/commands")
    os.makedirs(skills_dst, exist_ok=True)
    os.makedirs(cmds_dst, exist_ok=True)

    sec_path = os.path.join(base, "Security & Penetration Testing")
    crypto_path = os.path.join(base, "Finance & Crypto")
    
    count = 0
    for cat_path in [sec_path, crypto_path]:
        if not os.path.isdir(cat_path): continue
        for skill in os.listdir(cat_path):
            sp = os.path.join(cat_path, skill)
            dp = os.path.join(skills_dst, skill)
            if os.path.isdir(sp) and os.path.exists(f"{sp}/SKILL.md"):
                if not os.path.exists(dp):
                    shutil.copytree(sp, dp)
                    count += 1
    ok(f"{count} skills registered to ~/.claude/skills")

def verify():
    print("\n  Verification:")
    path = f"{GOBIN}:{os.environ.get('PATH','')}"
    all_tools = list(TOOLS.keys()) + list(GO_TOOLS.keys()) + list(PIP_TOOLS.keys())
    ok_count = 0
    for t in sorted(set(all_tools)):
        found = shutil.which(t, path=path)
        if found:
            ok(f"{t}: {found}")
            ok_count += 1
        else:
            fail(f"{t}: NOT FOUND")
    print(f"\n  {ok_count}/{len(set(all_tools))} tools ready")

if __name__ == "__main__":
    args = sys.argv[1:]
    do_tools = "--tools" in args or "--all" in args or not args
    do_skills = "--skills" in args or "--all" in args or not args

    print("\n  awskill — Bug Bounty + Crypto Tool Installer")
    print("  by ouwibo | github.com/ouwibo/awskill\n")

    if do_tools:
        install_apt()
        for name, url in TOOLS.items():
            if url: install_binary(name, url)
        install_go_tools()
        install_pip_tools()

    if do_skills:
        install_skills()

    verify()
    print(f"\n  Add to PATH: export PATH={GOBIN}:$PATH\n")
