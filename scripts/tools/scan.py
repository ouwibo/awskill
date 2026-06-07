#!/usr/bin/env python3
"""
scan.py — unified bug bounty scanner

Hardened: target is validated against a strict regex before any shell call,
all interpolations use shlex.quote(), and output goes to a freshly created
mkdtemp() directory instead of a predictable /tmp path.

Usage: python3 scripts/tools/scan.py <target> [--mode recon|full|xss|sqli|secrets|crypto|params]
"""
import os
import re
import sys
import shlex
import shutil
import argparse
import tempfile
import subprocess

GOBIN = os.path.expanduser("~/go/bin")
PATH = f"{GOBIN}:{os.environ.get('PATH','')}"

# Allowed target charset: domain labels, ASCII letters, digits, dots, hyphens.
# No protocol, no port, no slash. Strip those *before* validation.
TARGET_RE = re.compile(r"^(?=.{1,253}$)[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$")


def normalize_target(raw: str) -> str:
    """Strip protocol/path, lowercase, validate. Exit on bad input."""
    t = raw.strip().lower()
    t = re.sub(r"^https?://", "", t)
    t = t.split("/", 1)[0].split("?", 1)[0].split(":", 1)[0]
    if not TARGET_RE.match(t):
        sys.stderr.write(f"[-] Invalid target: {raw!r}. Expected a domain (e.g. example.com).\n")
        sys.exit(2)
    return t


def run(cmd: str, live: bool = True):
    """Run a shell pipeline. Caller MUST shlex.quote() any user input."""
    env = {**os.environ, "PATH": PATH}
    if live:
        return subprocess.run(cmd, shell=True, env=env).returncode
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    return r.stdout + r.stderr


def banner(msg):
    print(f"\n\033[1;36m[*] {msg}\033[0m")


def ok(msg):
    print(f"\033[92m[+] {msg}\033[0m")


def warn(msg):
    print(f"\033[93m[!] {msg}\033[0m")


def _have(tool: str) -> bool:
    return shutil.which(tool, path=PATH) is not None


def recon(target: str, out: str):
    os.makedirs(out, exist_ok=True)
    t = shlex.quote(target)
    o = shlex.quote(out)
    banner(f"RECON: {target}")

    if _have("subfinder"):
        banner("Subdomain enumeration — subfinder")
        run(f"subfinder -d {t} -o {o}/subdomains.txt -silent")
    else:
        warn("subfinder not installed — skipping subdomain enum")

    if _have("httpx") and os.path.exists(f"{out}/subdomains.txt"):
        banner("HTTP probe — httpx")
        run(f"httpx -l {o}/subdomains.txt -o {o}/alive.txt -silent -title -status-code -tech-detect")

    if _have("gau"):
        banner("URL discovery — gau")
        run(f"gau {t} | tee -a {o}/urls.txt >/dev/null")

    if _have("waybackurls"):
        run(f"echo {t} | waybackurls | tee -a {o}/urls.txt >/dev/null")

    if _have("katana") and os.path.exists(f"{out}/alive.txt"):
        banner("JS recon — katana")
        run(f"katana -list {o}/alive.txt -o {o}/katana_urls.txt -silent")

    if _have("dnsx") and os.path.exists(f"{out}/subdomains.txt"):
        banner("DNS resolve — dnsx")
        run(f"dnsx -l {o}/subdomains.txt -o {o}/dns_resolved.txt -silent")

    ok(f"Recon done → {out}/")


def vuln_scan(target: str, out: str):
    os.makedirs(out, exist_ok=True)
    t = shlex.quote(target)
    o = shlex.quote(out)
    banner(f"VULN SCAN: {target}")

    if _have("nuclei"):
        banner("Nuclei scan")
        run(f"nuclei -u {t} -o {o}/nuclei.txt -silent -severity medium,high,critical")
    else:
        warn("nuclei not installed — skipping")

    urls_file = f"{out}/urls.txt"
    if _have("dalfox") and os.path.exists(urls_file):
        banner("XSS — dalfox")
        run(f"dalfox file {shlex.quote(urls_file)} -o {o}/xss.txt")

    if _have("sqlmap"):
        banner("SQLi — sqlmap (note: only tests https://{target}/?id=1)")
        sqlmap_url = f"https://{target}/?id=1"
        run(f"sqlmap -u {shlex.quote(sqlmap_url)} --batch --level=2 --output-dir={o}/sqlmap")

    ok(f"Vuln scan done → {out}/")


def secrets_scan(target: str, out: str):
    os.makedirs(out, exist_ok=True)
    o = shlex.quote(out)
    banner(f"SECRETS SCAN: {target}")

    if _have("trufflehog"):
        # NOTE: target is expected to be a GitHub org for this path.
        run(f"trufflehog github --org={shlex.quote(target)} --json > {o}/secrets.json 2>&1 || true")
    else:
        warn("trufflehog not installed — skipping GitHub secret scan")

    if _have("gitleaks"):
        run(f"gitleaks detect --source=. --report-path={o}/gitleaks.json --no-banner || true")

    ok(f"Secrets scan done → {out}/")


def param_fuzz(target: str, out: str):
    os.makedirs(out, exist_ok=True)
    t = shlex.quote(target)
    o = shlex.quote(out)
    banner(f"PARAM FUZZ: {target}")
    if _have("arjun"):
        url = f"https://{target}"
        run(f"arjun -u {shlex.quote(url)} --output {o}/params.json")
    else:
        warn("arjun not installed — install with: pip3 install arjun")
    ok(f"Param fuzz done → {out}/")


def crypto_audit(target: str, out: str):
    os.makedirs(out, exist_ok=True)
    t = shlex.quote(target)
    o = shlex.quote(out)
    banner(f"WEB CRYPTO/SSL AUDIT: {target}")

    if _have("slither"):
        banner("Solidity static analysis — slither")
        run(f"slither {t} || true")
    else:
        warn("slither not installed (pip3 install slither-analyzer) — skipping Solidity scan")

    if _have("httpx"):
        banner("HTTP security headers")
        run(f"httpx -u {t} -silent -include-response-header -json > {o}/headers.json 2>&1 || true")

    if _have("nmap"):
        banner("SSL/TLS check")
        run(f"nmap --script ssl-cert,ssl-enum-ciphers -p 443 {t} -oN {o}/ssl.txt")

    ok(f"Crypto audit done → {out}/")


def main():
    p = argparse.ArgumentParser(description="awskill scanner by ouwibo")
    p.add_argument("target", help="Target domain (e.g. example.com)")
    p.add_argument("--mode", choices=["recon", "full", "xss", "sqli", "secrets", "crypto", "params"], default="recon")
    p.add_argument("--out", default=None, help="Output directory (default: mkdtemp)")
    args = p.parse_args()

    target = normalize_target(args.target)
    out = args.out or tempfile.mkdtemp(prefix=f"awskill_{target}_")

    if args.mode == "recon":
        recon(target, out)
    elif args.mode == "full":
        recon(target, out)
        vuln_scan(target, out)
        secrets_scan(target, out)
        param_fuzz(target, out)
    elif args.mode in ("xss", "sqli"):
        vuln_scan(target, out)
    elif args.mode == "secrets":
        secrets_scan(target, out)
    elif args.mode == "crypto":
        crypto_audit(target, out)
    elif args.mode == "params":
        param_fuzz(target, out)

    print(f"\n\033[1;32mResults saved to: {out}/\033[0m\n")


if __name__ == "__main__":
    main()
