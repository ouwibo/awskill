#!/usr/bin/env python3
"""
crypto_audit.py — DeFi / Web3 smart contract & project auditor

Hardened: targets are strictly validated before any subprocess call, Etherscan
key is read from $ETHERSCAN_API_KEY (skip API calls if unset), and all
interpolations into shell pipelines go through shlex.quote().

Usage: python3 scripts/tools/crypto_audit.py <0xADDR | github-url | https-url>
"""
import os
import re
import sys
import json
import shlex
import shutil
import argparse
import subprocess

GOBIN = os.path.expanduser("~/go/bin")
PATH = f"{GOBIN}:{os.environ.get('PATH','')}"

ETH_ADDR_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
GITHUB_RE = re.compile(r"^https://github\.com/([A-Za-z0-9._\-]+)/([A-Za-z0-9._\-]+)/?$")
URL_RE = re.compile(r"^https?://[A-Za-z0-9.\-]+(?::[0-9]+)?(?:/[A-Za-z0-9._~\-/]*)?$")
DOMAIN_RE = re.compile(r"^[a-zA-Z0-9.\-]+$")


def run(cmd: str) -> str:
    """Run a shell pipeline; caller MUST shlex.quote() any user input."""
    r = subprocess.run(
        cmd, shell=True, capture_output=True, text=True,
        env={**os.environ, "PATH": PATH},
    )
    return r.stdout.strip()


def banner(msg):
    print(f"\n\033[1;35m[*] {msg}\033[0m")


def ok(msg):
    print(f"\033[92m[+] {msg}\033[0m")


def warn(msg):
    print(f"\033[93m[!] {msg}\033[0m")


def _have(tool: str) -> bool:
    return shutil.which(tool, path=PATH) is not None


def etherscan_key() -> str:
    return os.environ.get("ETHERSCAN_API_KEY", "").strip()


def check_etherscan(addr: str):
    banner(f"Etherscan: {addr}")
    key = etherscan_key()
    if not key:
        warn("ETHERSCAN_API_KEY not set — skipping balance lookup")
        return
    url = (
        "https://api.etherscan.io/api"
        f"?module=account&action=balance&address={addr}&tag=latest&apikey={key}"
    )
    out = run(f"curl -sS {shlex.quote(url)}")
    try:
        d = json.loads(out)
        if d.get("status") == "1":
            bal = int(d["result"]) / 1e18
            ok(f"ETH Balance: {bal:.4f} ETH")
        else:
            warn(f"Etherscan returned status={d.get('status')}: {d.get('message')}")
    except Exception:
        warn("Etherscan: response not JSON or rate limited")


def check_contract(addr: str):
    banner("Contract Security Check")
    key = etherscan_key()
    if not key:
        warn("ETHERSCAN_API_KEY not set — cannot fetch verified source")
        return
    url = (
        "https://api.etherscan.io/api"
        f"?module=contract&action=getsourcecode&address={addr}&apikey={key}"
    )
    code = run(f"curl -sS {shlex.quote(url)}")
    try:
        src = json.loads(code).get("result", [{}])[0].get("SourceCode", "")
    except Exception:
        warn("Could not parse Etherscan response")
        return
    if not src:
        warn("Source not verified on Etherscan")
        return
    checks = [
        ("Reentrancy", "reentrancy"),
        ("Unchecked calls", "unchecked"),
        ("Integer overflow", "overflow"),
        ("Self destruct", "selfdestruct"),
        ("Delegatecall", "delegatecall"),
        ("tx.origin auth", "tx.origin"),
    ]
    src_l = src.lower()
    for name, pattern in checks:
        found = pattern in src_l
        (warn if found else ok)(f"{name}: {'FOUND' if found else 'clean'}")


def check_github(repo_url: str):
    banner(f"GitHub Repo Audit: {repo_url}")
    m = GITHUB_RE.match(repo_url)
    if not m:
        warn("Not a valid GitHub repo URL (expected https://github.com/owner/repo)")
        return
    owner, repo = m.group(1), m.group(2)
    repo_slug = f"{owner}/{repo}"

    api = f"https://api.github.com/repos/{repo_slug}"
    info = run(f"curl -sS {shlex.quote(api)}")
    try:
        d = json.loads(info)
    except Exception:
        warn("GitHub API: invalid response")
        return

    if "message" in d and d.get("message") in ("Not Found", "Bad credentials"):
        warn(f"GitHub: {d['message']}")
        return

    ok(f"Stars: {d.get('stargazers_count', 0)} | Forks: {d.get('forks_count', 0)}")
    ok(f"Open issues: {d.get('open_issues_count', 0)}")
    ok(f"Last push: {d.get('pushed_at', 'unknown')}")
    if d.get("license"):
        ok(f"License: {d['license'].get('name', 'unknown')}")
    else:
        warn("No license declared")
    if d.get("archived"):
        warn("Repo is ARCHIVED")

    if _have("trufflehog"):
        banner("Secrets scan — trufflehog")
        out = run(
            f"trufflehog github --repo={shlex.quote(repo_url)} --json 2>/dev/null | head -5"
        )
        if out and "DetectorName" in out:
            warn(f"SECRETS FOUND (first matches):\n{out}")
        else:
            ok("No secrets detected")
    else:
        warn("trufflehog not installed — skipping secret scan")


def check_url(url: str):
    banner(f"Web3 Site Audit: {url}")
    domain = re.sub(r"^https?://", "", url).split("/", 1)[0].split(":", 1)[0]
    if not DOMAIN_RE.match(domain):
        warn(f"Invalid hostname extracted from URL: {domain!r}")
        return

    if _have("nmap"):
        banner("SSL/TLS — nmap ssl-cert")
        ssl_out = run(
            f"nmap --script ssl-cert -p 443 {shlex.quote(domain)} 2>/dev/null"
            f" | grep -E 'Subject:|Not valid'"
        )
        if ssl_out:
            for line in ssl_out.splitlines():
                if line.strip():
                    ok(line.strip())
        else:
            warn("SSL check produced no output")

    banner("HTTP security headers")
    headers = run(
        f"curl -sSI {shlex.quote(url)}"
        f" | grep -iE 'x-frame|content-security|strict-transport|x-content-type'"
    )
    if headers:
        for h in headers.splitlines():
            if h.strip():
                ok(h.strip())
    else:
        warn("Missing standard security headers")

    if _have("nuclei"):
        banner("Nuclei web3 templates")
        subprocess.run(
            ["nuclei", "-u", url, "-tags", "web3,crypto", "-silent",
             "-severity", "medium,high,critical"],
            env={**os.environ, "PATH": PATH},
        )
    else:
        warn("nuclei not installed — skipping template scan")


def main():
    p = argparse.ArgumentParser(description="awskill crypto auditor by ouwibo")
    p.add_argument("target", help="0x ETH address, GitHub repo URL, or https URL")
    args = p.parse_args()
    t = args.target.strip()

    if ETH_ADDR_RE.match(t):
        check_etherscan(t)
        check_contract(t)
    elif GITHUB_RE.match(t):
        check_github(t)
    elif URL_RE.match(t):
        check_url(t)
    else:
        sys.stderr.write(
            f"[-] Invalid target: {t!r}\n"
            "    Expected one of:\n"
            "      • 0x<40 hex chars> (Ethereum address)\n"
            "      • https://github.com/<owner>/<repo>\n"
            "      • https://<domain>[/path]\n"
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
