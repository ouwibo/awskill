```
 █████╗ ██╗    ██╗███████╗██╗  ██╗██╗██╗     ██╗
██╔══██╗██║    ██║██╔════╝██║ ██╔╝██║██║     ██║
███████║██║ █╗ ██║███████╗█████╔╝ ██║██║     ██║
██╔══██║██║███╗██║╚════██║██╔═██╗ ██║██║     ██║
██║  ██║╚███╔███╔╝███████║██║  ██╗██║███████╗███████╗
╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝
                            245 skills · 18 categories · 1 install
```

**Bug bounty arsenal + Web3 audit + dev tools for AI agents.**
Drop-in for Claude Code & Codex. Tools verified, scripts sandboxed, manifest CI-checked.

[![MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-245-blue.svg)](skills.json)
[![CI](https://img.shields.io/badge/CI-validate-brightgreen.svg)](.github/workflows/validate.yml)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Install

```bash
git clone https://github.com/ouwibo/awskill
cd awskill && bash install.sh
```

> Codex instead? `AWSKILL_TARGET=codex bash install.sh`

Installs 14 security binaries (with SHA256 verification), registers all 245 skills into `~/.claude/skills`, and adds `~/go/bin` to `$PATH`.

---

## Use

```bash
/hunt target.com              # autonomous bug bounty pipeline
/web3-audit 0xCONTRACT        # smart contract security audit
/scope target.com             # check program scope
/chain                        # build A→B→C exploit chains
/triage                       # 7-question gate validation
/report                       # H1 / Bugcrowd / Intigriti / Immunefi format
```

Browse what's installed:

```bash
python3 scripts/awskill.py --stats
python3 scripts/awskill.py --search xss
python3 scripts/awskill.py --cat "Web3 & Smart Contract Security"
```

---

## Web3 Spotlight 🔥

A dedicated `Web3 & Smart Contract Security` category — the playbook for Immunefi/Cantina hunts:

| Skill | What it covers |
|---|---|
| `smart-contract-vulnerabilities` | Reentrancy, integer overflow, delegatecall, signature replay, CREATE2 |
| `defi-attack-patterns` | Flash loan, oracle manipulation, MEV, vault inflation, bridge attacks |
| `web3-audit` | 10-bug-class methodology + Foundry PoC template + grep patterns |
| `cmd-web3-audit` | Run the methodology end-to-end on a target |
| `cmd-token-scan` | Meme coin rug detection — honeypot, hidden mint, fee manipulation |
| `meme-coin-audit` | Solana/EVM token deep audit |
| `crypto-project-research` | Chain, funding, investors, socials before you hunt |

---

## Categories

| Category | Skills | Category | Skills |
|---|---|---|---|
| **Web Application Security** | 56 | **Active Directory & Windows** | 7 |
| **Bug Bounty & Workflow** | 30 | **Cryptography & Cryptanalysis** | 6 |
| **Developer Tools** | 28 | **Network & Infrastructure** | 6 |
| **Web & Frontend Development** | 19 | **Productivity & Utilities** | 6 |
| **AI & Agent Automation** | 17 | **Linux & macOS Internals** | 5 |
| **Content & Documents** | 16 | **Mobile Security** | 3 |
| **SEO & Marketing** | 13 | **AI & LLM Security** | 2 |
| **Binary Exploitation & RE** | 12 | **Forensics** | 1 |
| **Finance & Crypto** | 11 | | |
| **Web3 & Smart Contract Security** | 7 | **Total** | **245** |

[Full machine-readable index → `skills.json`](skills.json)

---

## Slash Commands

```
RECON              HUNT               REPORT
/scope             /hunt              /triage
/scope-aggregate   /autopilot         /validate
/recon             /web3-audit        /chain
/intel             /scan-cves         /report
/surface           /param-discover    /remember
/cloud-recon       /secrets-hunt
/pickup            /takeover          META
                   /token-scan        /arsenal
                   /bypass-403        /memory-gc
```

---

## Built-in Tools (SHA256-verified install)

`subfinder` `httpx` `nuclei` `katana` `gau` `dnsx` `ffuf` `nmap`
`dalfox` `sqlmap` `trufflehog` `gitleaks` `slither` `arjun`

---

## Contribute

Add a skill in three steps:

```bash
mkdir -p "skills/<Category>/my-skill"
$EDITOR  "skills/<Category>/my-skill/SKILL.md"   # write the playbook
python3 scripts/tools/validate_skills.py         # checks frontmatter + structure
python3 scripts/tools/generate_manifest.py       # regenerates skills.json
```

CI runs the same checks on every PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

---

## Requirements

Python 3.8+ · Go 1.21+ (auto-installed) · Linux / macOS

---

**For authorized security research only** — see [SECURITY.md](SECURITY.md).

[CHANGELOG](CHANGELOG.md) · [CONTRIBUTING](CONTRIBUTING.md) · [MIT](LICENSE) · `@ouwibo`
