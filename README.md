# awskill

> Universal AI agent skill arsenal for bug bounty hunters and crypto researchers.

```bash
git clone https://github.com/ouwibo/awskill
cd awskill && bash install.sh
```

---

## Overview

**254 skills** organized across 8 categories. Compatible with any AI agent — Claude, GPT, Gemini, or custom.

Combines the best of:
- [projectdiscovery](https://github.com/projectdiscovery) tools
- [shuvonsec/claude-bug-bounty](https://github.com/shuvonsec/claude-bug-bounty)
- [yaklang/hack-skills](https://github.com/yaklang/hack-skills)
- [zocomputer/skills](https://github.com/zocomputer/skills)

---

## Categories

| Category | Count |
|---|---|
| Security & Penetration Testing | 128 |
| Developer Tools | 29 |
| Web & Frontend Development | 19 |
| Content & Documents | 18 |
| AI & Agent Automation | 17 |
| SEO & Marketing | 13 |
| Finance & Crypto | 12 |
| Productivity & Utilities | 12 |
| **Total** | **254** |

---

## Installation

```bash
git clone https://github.com/ouwibo/awskill
cd awskill
bash install.sh
```

Installs the following tools automatically:

| Category | Tools |
|---|---|
| Recon | subfinder, httpx, katana, dnsx, gau, waybackurls, amass |
| Vulnerability | nuclei, dalfox, sqlmap, arjun, ffuf, nmap |
| Secrets | trufflehog, gitleaks |
| Web3 | slither, interactsh-client |
| Utilities | anew, qsreplace |

---

## Usage

### Recon
```bash
python3 scripts/tools/scan.py target.com
python3 scripts/tools/scan.py target.com --mode recon
```

### Full Scan
```bash
python3 scripts/tools/scan.py target.com --mode full
```

### XSS / SQLi
```bash
python3 scripts/tools/scan.py target.com --mode xss
python3 scripts/tools/scan.py target.com --mode sqli
```

### Secrets Hunt
```bash
python3 scripts/tools/scan.py target.com --mode secrets
```

### Crypto / Web3 Audit
```bash
python3 scripts/tools/crypto_audit.py 0xCONTRACT_ADDRESS
python3 scripts/tools/crypto_audit.py https://github.com/org/repo
python3 scripts/tools/crypto_audit.py https://project.io
```

### Browse Skills
```bash
python3 scripts/awskill.py --list
python3 scripts/awskill.py --search xss
python3 scripts/awskill.py --cat "Security & Penetration Testing"
python3 scripts/awskill.py --run bug-bounty
```

---

## Slash Commands (23)

| Command | Description |
|---|---|
| `/recon` | Full recon on a target |
| `/hunt` | Start a bug bounty hunt |
| `/validate` | Validate a finding |
| `/report` | Generate a bug report |
| `/autopilot` | Fully automated hunting |
| `/bypass-403` | 403/401 bypass techniques |
| `/chain` | Chain vulnerabilities |
| `/cloud-recon` | Cloud asset discovery |
| `/intel` | OSINT and intel gathering |
| `/scope` | Define scope |
| `/secrets-hunt` | Hunt for exposed secrets |
| `/takeover` | Subdomain takeover check |
| `/token-scan` | Scan for exposed tokens |
| `/triage` | Triage and prioritize findings |
| `/scan-cves` | Scan for known CVEs |
| `/param-discover` | Parameter discovery |
| `/surface` | Attack surface mapping |
| `/arsenal` | List available tools |
| `/web3-audit` | Web3 / smart contract audit |
| `/scope-aggregate` | Aggregate scope across programs |
| `/pickup` | Resume a previous session |
| `/remember` | Save context to memory |
| `/memory-gc` | Clear agent memory |

---

## Requirements

- Python 3.8+
- Go 1.21+ (auto-installed if missing)
- Linux / macOS

---

## License

MIT — free to use, fork, and contribute.

---

by [ouwibo](https://github.com/ouwibo)
