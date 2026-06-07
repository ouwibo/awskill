---
name: crypto-project-research
description: Automatically research any crypto/NFT project URL — chain, logo, funding, investors, twitter/socials, Galxe credentials, and overall summary. Activate when user pastes any project link or asks to research a project.
compatibility: Universal — works with any AI agent
metadata:
  author: hrxcrypt.zo.computer
category: Finance & Crypto
---

# Crypto Project Research Skill

## When to Activate
- User pastes any project URL (e.g., https://app.somesite.xyz, https://testnet.project.io)
- User asks "research this", "check this project", "what is this", "cek airdrop ini"
- User pastes a link and says "research" or "check" or "rekam"

## How It Works

When triggered, do ALL of the following in parallel where possible:

### Step 1 — Fetch the URL
```bash
read_webpage(url, use_browser=true)
```
Save the .md output for reference.

### Step 2 — Identify Chain & Project Type
Detect from the URL/content:
- Which blockchain (Ethereum, Solana, Base, Arbitrum, Blast, Scroll, zkSync, etc.)
- If it's a testnet, app, dashboard, or gamified task platform
- Token or NFT collection?

### Step 3 — Web Research (parallel)
```bash
web_search(query="project name crypto airdrop tokenomics")
web_research(category="company", query="project name official site investors funding")
web_research(category="github", query="project name repository")
```

### Step 4 — Social Research (parallel)
```bash
x_search(query="project name twitter handle airdrop")
web_search(query="project name discord telegram telegram community")
```

### Step 5 — Logo Search
```bash
image_search(query="project name crypto logo")
```

### Step 6 — Credentialing (if applicable)
```bash
web_search(query="project name galxe layer3 credential campaign")
```

## Output Format

Compile everything into this structured markdown report:

```markdown
## [Project Name] ($TICKER)

**🌐 Chain:** Ethereum | Solana | Base | Arbitrum | Blast | Scroll | zkSync | etc.

**📊 Status:** Active | Testnet | Upcoming | Ended | Preseason

**🔗 Links:**
- Website: https://...
- App: https://app....
- Twitter/X: @handle (N followers)
- Discord: N members
- Telegram: link
- GitHub: repository

**💰 Funding:** $X raised | Y Round | Investors: VC1, VC2, VC3
*(if no funding found, note "no public funding data")*

**🛠️ Project Type:** Gaming NFT | DeFi | L2 | Infrastructure | Social | etc.

**📦 Token/NFT:** Description of native asset

**🎯 How to Participate:**
1. Task 1 (time/cost)
2. Task 2 (time/cost)
...

**🔗 Credentialing:**
- Galxe: link (campaign name)
- Layer3: link
- or "None found"

**🐦 X/Twitter Alpha:**
- Recent notable tweets or sentiment
- Team activity
- Community size/trend

**📝 Notes & Alpha:**
- Key opportunity observations
- Potential red flags
- Timeline expectations
```

## Tools Priority
1. `read_webpage(use_browser=true)` — primary source
2. `web_search` — fast general info
3. `web_research` — deeper (company, github, pdf)
4. `x_search` — Twitter discourse & sentiment
5. `image_search` — logo

## Tips
- Always try to find the official Twitter/X handle first — it's the most reliable signal
- If project is on Treasure/Magic Eden/Berachain ecosystem, check those specifically
- Check coingecko.com for any listed token
- Check dextools for any live trading pair
- For testnets: note if there's a recorded TGE (token generation event) timeline
- For gaming: check player count, retention signals
- If Galxe credential found, also note what tasks are required
- Always include the actual URLs you found in the report