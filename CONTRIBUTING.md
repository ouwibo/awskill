# Contributing to awskill

Thank you for considering contributing to **awskill**. All contributions are welcome.

## How to Contribute

### Adding a New Skill

1. Fork the repository
2. Create a new directory under the appropriate category:
   ```
   Category Name/
   └── your-skill-name/
       ├── SKILL.md       # required
       ├── scripts/       # optional — executable scripts
       └── references/    # optional — docs, API notes
   ```
3. Write `SKILL.md` with valid frontmatter:
   ```yaml
   ---
   name: your-skill-name
   description: One sentence describing when to use this skill.
   compatibility: Compatible with any AI agent environment
   metadata:
     author: your-github-handle
   ---
   ```
4. Submit a pull request with a clear description

### Adding a Tool Script

Place scripts under `scripts/tools/`. Python 3.8+ or Bash preferred.

- Include `--help` documentation
- Do not hardcode API keys — use environment variables
- Test before submitting

### Improving Documentation

- Fix typos, clarify instructions, add examples
- All improvements are welcome

## Code of Conduct

- Be respectful
- Only contribute tools for **authorized, ethical** security research
- No malware, no C2 payloads, no exploit code targeting production systems

## Questions

Open an issue or reach out via GitHub Discussions.
