#!/usr/bin/env python3
"""
scan.py — unified bug bounty scanner
Usage: python3 scripts/tools/scan.py <target> [--mode recon|full|xss|sqli|secrets|crypto]
"""
import os, sys, subprocess, shutil, argparse

GOBIN = os.path.expanduser("~/go/bin")
PATH = f"{GOBIN}:{os.environ.get('PATH','')}"

def run(cmd, live=True):
    env = {**os.environ, "PATH": PATH}
    if live:
        subprocess.run(cmd, shell=True, env=env)
    else:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
        return r.stdout + r.stderr

def banner(msg): print(f"\n\033[1;36m[*] {msg}\033[0m")
def ok(msg): print(f"\033[92m[+] {msg}\033[0m")

def recon(target, out):
    os.makedirs(out, exist_ok=True)
    banner(f"RECON: {target}")
    
    banner("Subdomain enumeration — subfinder")
    run(f"subfinder -d {target} -o {out}/subdomains.txt -silent")
    
    banner("HTTP probe — httpx")
    run(f"httpx -l {out}/subdomains.txt -o {out}/alive.txt -silent -title -status-code -tech-detect")
    
    banner("URL discovery — gau + waybackurls")
    run(f"gau {target} 2>/dev/null | anew {out}/urls.txt")
    run(f"echo {target} | waybackurls 2>/dev/null | anew {out}/urls.txt")
    
    banner("JS recon — katana")
    run(f"katana -u {out}/alive.txt -o {out}/katana_urls.txt -silent 2>/dev/null || echo 'katana: skipped'")
    
    banner("DNS brute — dnsx")
    run(f"cat {out}/subdomains.txt | dnsx -o {out}/dns_resolved.txt -silent 2>/dev/null")
    
    ok(f"Recon done → {out}/")

def vuln_scan(target, out):
    os.makedirs(out, exist_ok=True)
    banner(f"VULN SCAN: {target}")
    
    banner("Nuclei scan")
    run(f"nuclei -u {target} -o {out}/nuclei.txt -silent -severity medium,high,critical 2>/dev/null")
    
    banner("XSS — dalfox")
    urls = f"{out}/urls.txt"
    if os.path.exists(urls):
        run(f"cat {urls} | dalfox pipe -o {out}/xss.txt 2>/dev/null || echo 'dalfox: skipped'")
    
    banner("SQLi — sqlmap")
    run(f"sqlmap -u 'https://{target}/?id=1' --batch --level=2 --output-dir={out}/sqlmap 2>/dev/null || echo 'sqlmap: skipped'")
    
    ok(f"Vuln scan done → {out}/")

def secrets_scan(target, out):
    os.makedirs(out, exist_ok=True)
    banner(f"SECRETS SCAN: {target}")
    run(f"trufflehog github --org={target} --json 2>/dev/null | tee {out}/secrets.json || echo 'trufflehog: skipped'")
    run(f"gitleaks detect --source=. --report-path={out}/gitleaks.json 2>/dev/null || echo 'gitleaks: skipped'")
    ok(f"Secrets scan done → {out}/")

def param_fuzz(target, out):
    os.makedirs(out, exist_ok=True)
    banner(f"PARAM FUZZ: {target}")
    run(f"arjun -u https://{target} --output {out}/params.json 2>/dev/null || echo 'arjun: skipped'")
    ok(f"Param fuzz done → {out}/")

def crypto_audit(target, out):
    os.makedirs(out, exist_ok=True)
    banner(f"CRYPTO AUDIT: {target}")
    
    banner("Contract analysis — slither (if available)")
    run(f"slither {target} 2>/dev/null || echo 'slither: install with pip3 install slither-analyzer'")
    
    banner("HTTP security headers")
    run(f"httpx -u {target} -silent -include-response-header -json 2>/dev/null | tee {out}/headers.json")
    
    banner("SSL/TLS check")
    run(f"nmap --script ssl-cert,ssl-enum-ciphers -p 443 {target} 2>/dev/null | tee {out}/ssl.txt")
    
    ok(f"Crypto audit done → {out}/")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="awskill scanner by ouwibo")
    p.add_argument("target", help="Target domain or URL")
    p.add_argument("--mode", choices=["recon","full","xss","sqli","secrets","crypto","params"], default="recon")
    p.add_argument("--out", default=None, help="Output directory")
    args = p.parse_args()

    target = args.target.replace("https://","").replace("http://","").rstrip("/")
    out = args.out or f"/tmp/awskill_{target}"

    if args.mode == "recon":
        recon(target, out)
    elif args.mode == "full":
        recon(target, out)
        vuln_scan(target, out)
        secrets_scan(target, out)
        param_fuzz(target, out)
    elif args.mode in ["xss","sqli"]:
        vuln_scan(target, out)
    elif args.mode == "secrets":
        secrets_scan(target, out)
    elif args.mode == "crypto":
        crypto_audit(target, out)
    elif args.mode == "params":
        param_fuzz(target, out)

    print(f"\n\033[1;32m Results saved to: {out}/\033[0m\n")
