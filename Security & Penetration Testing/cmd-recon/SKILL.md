---
name: cmd-recon
description: Run the full recon pipeline by invoking tools/recon_engine.sh — subdomain enum (subfinder + amass + crt.sh + wayback), httpx live host probing with tech detection, nmap port scan, gau URL collection, JS analysis, ffuf directory fuzzing, parameter discovery, config exposure check, CI/CD workflow scan. Outputs to recon/<target>/. Handles FQDN, IP, CIDR, and file-of-hosts targets automatically. Usage: /recon target.com
compatibility: Universal — works with any AI agent
metadata:
  author: ouwibo
---

# /recon

Run the full recon pipeline on a target. **Always invoke the production script directly** — do not re-implement the steps inline. The methodology below is reference material; the script is the entry point.

## Run This (the only required step)

```bash
# Domain (full subdomain enum + crawl + fuzz):
bash tools/recon_engine.sh target.com

# CIDR — skips subdomain enum, runs nmap host sweep:
bash tools/recon_engine.sh 10.0.0.0/24

# Single IP — scope-locked, no subdomain enum:
bash tools/recon_engine.sh 192.0.2.10

# Domain list (programs without wildcard scope) — pre-resolved hosts in a file:
bash tools/recon_engine.sh path/to/scope.txt

# Quick mode (skip amass + reduce ffuf coverage):
bash tools/recon_engine.sh target.com --quick
```

The script auto-detects target type:
- Path to a readable file → loads it as a host list (one per line, `#` comments OK) and **skips subdomain enumeration entirely**.
- `x.x.x.x/y` → CIDR sweep (max /24, scope-locked).
- `x.x.x.x` → single IP, scope-locked.
- Anything else → treated as a domain; full enum runs.

Output lands in `recon/<target>/` (or `recon/<file-basename>/` for list mode):

```
recon/<target>/
├── subdomains/all.txt
├── live/urls.txt
├── urls/all.txt
├── candidates/{xss,ssrf,idor,sqli,redirect,lfi}.txt
├── api-endpoints.txt
├── nuclei/findings.txt
└── cicd/summary.txt        (if CI/CD workflows detected)
```

## Troubleshooting

### "/recon path/to/file.txt still runs subdomain enumeration"

You're on an older revision of this command file where the model re-implemented the pipeline inline and never invoked the production script. Pull latest, or run the script directly:

```bash
bash tools/recon_engine.sh path/to/file.txt
```

You should see `[*] Domain-list target — loading <file> (skipping subdomain enum)` near the start.

### "/recon loops / doesn't actually run anything"

Same root cause as the hunt-loop bug. Run the bash directly:

```bash
bash tools/recon_engine.sh target.com
```

Or in your prompt: "Run `bash tools/recon_engine.sh target.com` and report the output. Do not re-implement the steps."

### "Missing tools"

```bash
bash tools/install_tools.sh
```

Recon needs: `subfinder`, `dnsx`, `httpx` (ProjectDiscovery — not the Python CLI), `katana`, `gau`, `nuclei`, `ffuf`, `nmap`, `gf`, `anew`. The installer handles all of them.

## After Recon

1. Review `recon/<target>/live/urls.txt` — open interesting ones in a browser.
2. Check `recon/<target>/nuclei/findings.txt` — any high/critical?
3. Review `recon/<target>/api-endpoints.txt` — start IDOR testing.
4. `grep -E "admin|jenkins|grafana|gitlab" recon/<target>/live/urls.txt` — admin panels.
5. Run `/hunt target.com` to start active vulnerability testing on the recon output.

## 5-Minute Kill Signal

If after running this pipeline:
- All hosts return 403 or static pages
- No API endpoints visible
- No interesting parameters in URLs
- nuclei returns 0 medium/high findings

**→ Move on to a different target.** Don't sink hours into a dead surface.

---

# Reference: What the script does (informational)

The pipeline in `tools/recon_engine.sh` runs these phases (numbers may shift; check the script source):

1. **Subdomain enumeration** — subfinder + Chaos API (if `$CHAOS_API_KEY` set) + amass + crt.sh + wayback.
2. **Live host discovery** — dnsx resolve, then httpx with status/title/tech-detect.
3. **Port scan** — nmap top-1000 on live hosts (CIDR mode runs a wider sweep).
4. **URL crawl** — katana deep crawl + waybackurls + gau historical.
5. **gf classification** — xss, ssrf, idor, sqli, redirect, lfi candidate files.
6. **JS analysis** — LinkFinder / SecretFinder on every JS bundle.
7. **ffuf directory fuzzing** — uses `wordlists/common.txt` (run `python3 tools/hunt.py --setup-wordlists` once if missing).
8. **Parameter discovery** — Arjun / x8 against high-value endpoints.
9. **Config exposure** — `.git/`, `.env`, `wp-config.php`, `.DS_Store`, swagger.json, etc.
10. **CI/CD scan** — sisakulint against any GitHub Actions workflows discovered.

For the IDOR / SSRF / GraphQL / SSTI / etc. active-testing playbooks, see `/hunt` and its methodology section.