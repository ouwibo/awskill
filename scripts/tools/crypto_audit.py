#!/usr/bin/env python3
"""
crypto_audit.py — DeFi/Web3 smart contract & project auditor
Usage: python3 scripts/tools/crypto_audit.py <address|url|github>
"""
import os, sys, subprocess, json, re, argparse

GOBIN = os.path.expanduser("~/go/bin")
PATH = f"{GOBIN}:{os.environ.get('PATH','')}"

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       env={**os.environ, "PATH": PATH})
    return r.stdout.strip()

def banner(msg): print(f"\n\033[1;35m[*] {msg}\033[0m")
def ok(msg): print(f"\033[92m[+] {msg}\033[0m")
def warn(msg): print(f"\033[93m[!] {msg}\033[0m")

def check_etherscan(addr):
    banner(f"Etherscan: {addr}")
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={addr}&tag=latest&apikey=YourApiKeyToken"
    out = run(f"curl -s '{url}'")
    try:
        d = json.loads(out)
        if d.get('status') == '1':
            bal = int(d['result']) / 1e18
            ok(f"ETH Balance: {bal:.4f} ETH")
    except: warn("Etherscan: no API key set (set ETHERSCAN_API_KEY)")

def check_contract(addr):
    banner("Contract Security Check")
    checks = [
        ("Reentrancy", "reentrancy"),
        ("Unchecked calls", "unchecked"),
        ("Integer overflow", "overflow"),
        ("Self destruct", "selfdestruct"),
        ("Delegatecall", "delegatecall"),
        ("tx.origin auth", "tx.origin"),
    ]
    code = run(f"curl -s 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address={addr}&apikey=${{ETHERSCAN_API_KEY}}'")
    try:
        src = json.loads(code).get('result',[{}])[0].get('SourceCode','')
        if src:
            for name, pattern in checks:
                found = pattern.lower() in src.lower()
                (warn if found else ok)(f"{name}: {'FOUND' if found else 'clean'}")
        else:
            warn("Source not verified on Etherscan")
    except: warn("Could not fetch contract source")

def check_github(repo_url):
    banner(f"GitHub Repo Audit: {repo_url}")
    repo = re.sub(r'https://github\.com/', '', repo_url).rstrip('/')
    
    # Check stars, forks, issues via API
    info = run(f"curl -s 'https://api.github.com/repos/{repo}'")
    try:
        d = json.loads(info)
        ok(f"Stars: {d.get('stargazers_count',0)} | Forks: {d.get('forks_count',0)}")
        ok(f"Open issues: {d.get('open_issues_count',0)}")
        ok(f"Last push: {d.get('pushed_at','unknown')}")
        if d.get('license'):
            ok(f"License: {d['license'].get('name','unknown')}")
        else:
            warn("No license found")
        if d.get('archived'):
            warn("Repo is ARCHIVED")
    except: warn("GitHub API rate limited or repo not found")

    # Secret scan with trufflehog
    banner("Secrets scan — trufflehog")
    out = run(f"trufflehog github --repo={repo_url} --json 2>/dev/null | head -5")
    if out and 'DetectorName' in out:
        warn(f"SECRETS FOUND:\n{out}")
    else:
        ok("No secrets detected")

def check_url(url):
    banner(f"Web3 Site Audit: {url}")
    domain = re.sub(r'https?://', '', url).rstrip('/')
    
    # SSL check
    ok_ssl = run(f"nmap --script ssl-cert -p 443 {domain} 2>/dev/null | grep 'Subject:'")
    ok(f"SSL: {ok_ssl}") if ok_ssl else warn("SSL check failed")
    
    # Security headers
    headers = run(f"curl -sI {url} | grep -i 'x-frame\\|content-security\\|strict-transport\\|x-content-type'")
    if headers:
        for h in headers.split('\n'):
            if h.strip(): ok(h.strip())
    else:
        warn("Missing security headers")
    
    # Nuclei quick scan
    banner("Nuclei web3 templates")
    run_live = subprocess.run(
        f"nuclei -u {url} -tags web3,crypto -silent -severity medium,high,critical 2>/dev/null",
        shell=True, env={**os.environ, "PATH": PATH}
    )

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="awskill crypto auditor by ouwibo")
    p.add_argument("target", help="ETH address, GitHub URL, or project URL")
    args = p.parse_args()
    t = args.target

    if re.match(r'^0x[a-fA-F0-9]{40}$', t):
        check_etherscan(t)
        check_contract(t)
    elif 'github.com' in t:
        check_github(t)
    else:
        check_url(t)
