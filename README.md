# awskill

> Universal AI agent skill arsenal for bug bounty hunters and crypto researchers.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-254-blue.svg)](#categories)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Quick Start

```bash
git clone https://github.com/ouwibo/awskill
cd awskill
bash install.sh
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
| **Total** | **254** |

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

### Browse & Run Skills
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
