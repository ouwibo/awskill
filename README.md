# awskill

> Universal AI agent skill arsenal for bug bounty hunters and crypto researchers.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-248-blue.svg)](#categories)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Quick Start

Install every skill as a flat list in your agent skills directory:

```bash
git clone https://github.com/ouwibo/awskill
cd awskill
bash install.sh
```

By default, `install.sh` copies all 248 skills into `~/.claude/skills` without category folders. To install into Codex instead:

```bash
AWSKILL_TARGET=codex bash install.sh
```

If you only want to install skills without installing external security tools:

```bash
python3 scripts/tools/install_skills.py --target claude --force
python3 scripts/tools/install_skills.py --target codex --force
```

---

## Categories

| Category | Skills |
|---|---|
| [Security & Penetration Testing](Security%20%26%20Penetration%20Testing/) | 128 |
| [Developer Tools](Developer%20Tools/) | 29 |
| [Web & Frontend Development](Web%20%26%20Frontend%20Development/) | 19 |
| [Content & Documents](Content%20%26%20Documents/) | 18 |
| [AI & Agent Automation](AI%20%26%20Agent%20Automation/) | 17 |
| [SEO & Marketing](SEO%20%26%20Marketing/) | 13 |
| [Finance & Crypto](Finance%20%26%20Crypto/) | 12 |
| [Productivity & Utilities](Productivity%20%26%20Utilities/) | 12 |
| **Total** | **248** |

---

## Tools Installed

| Tool | Purpose |
|---|---|
| `subfinder` | Subdomain discovery |
| `httpx` | HTTP probing |
| `nuclei` | Template-based vulnerability scanning |
| `katana` | Web crawler |
| `gau` | Fetch all known URLs |
| `dnsx` | DNS toolkit |
| `ffuf` | Fast web fuzzer |
| `nmap` | Network scanner |
| `dalfox` | XSS scanner |
| `sqlmap` | SQL injection |
| `trufflehog` | Secrets scanning |
| `gitleaks` | Git secrets detection |
| `slither` | Solidity static analyzer |
| `arjun` | HTTP parameter discovery |

---

## Usage

### Bug Bounty Recon
```bash
python3 scripts/tools/scan.py target.com
python3 scripts/tools/scan.py target.com --mode recon
python3 scripts/tools/scan.py target.com --mode full
python3 scripts/tools/scan.py target.com --mode xss
python3 scripts/tools/scan.py target.com --mode sqli
python3 scripts/tools/scan.py target.com --mode secrets
```

### Crypto / Web3 Audit
```bash
python3 scripts/tools/crypto_audit.py 0xCONTRACT_ADDRESS
python3 scripts/tools/crypto_audit.py https://github.com/org/repo
python3 scripts/tools/crypto_audit.py https://project.io
```

### Browse, Export, Install & Run Skills
```bash
python3 scripts/awskill.py --list
python3 scripts/awskill.py --search xss
python3 scripts/awskill.py --cat "Security & Penetration Testing"
python3 scripts/awskill.py --run bug-bounty
python3 scripts/awskill.py --install --target codex --force
python3 scripts/awskill.py --export-flat --clean
```

`--export-flat` copies every skill out of the category folders into `dist/skills/` and writes a matching `dist/skills/skills.json` manifest, which makes the full collection easy to inspect, zip, or mirror.

### Validate Repository Metadata
```bash
python3 scripts/tools/generate_manifest.py
python3 scripts/tools/validate_skills.py
python3 -m compileall -q scripts
```

The root [`skills.json`](skills.json) manifest is generated from all `SKILL.md` files and is the canonical installable list for the hundreds of skills in this repository.

---

## Slash Commands (23)

| Command | Description |
|---|---|
| `/recon` | Full reconnaissance on a target |
| `/hunt` | Start a bug bounty hunt |
| `/validate` | Validate a finding |
| `/report` | Generate a bug report |
| `/autopilot` | Fully automated hunting |
| `/bypass-403` | Bypass 403/401 responses |
| `/chain` | Chain vulnerabilities |
| `/cloud-recon` | Cloud asset discovery |
| `/intel` | OSINT and intelligence gathering |
| `/scope` | Define target scope |
| `/secrets-hunt` | Hunt for exposed secrets |
| `/takeover` | Subdomain takeover check |
| `/token-scan` | Scan for exposed tokens |
| `/triage` | Triage and prioritize findings |
| `/scan-cves` | Scan for known CVEs |
| `/param-discover` | Parameter discovery |
| `/surface` | Attack surface mapping |
| `/arsenal` | List available tools |
| `/web3-audit` | Smart contract audit |
| `/scope-aggregate` | Aggregate scope across programs |
| `/pickup` | Resume a previous session |
| `/remember` | Save context to memory |
| `/memory-gc` | Clear agent memory |

---

## Requirements

- Python 3.8+
- Go 1.21+ (auto-installed by `install.sh` if missing)
- Linux / macOS

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding skills, tools, and documentation.

## Security

This toolkit is for **authorized security research only**. See [SECURITY.md](SECURITY.md) for responsible use policy and vulnerability reporting.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

[MIT](LICENSE) — free to use, fork, and contribute.

---

by [ouwibo](https://github.com/ouwibo)
