#!/usr/bin/env bash
# install.sh — awskill one-line installer
# curl -fsSL https://raw.githubusercontent.com/ouwibo/awskill/main/install.sh | bash

set -e

GOBIN="$HOME/go/bin"
mkdir -p "$GOBIN"

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')

ok()   { echo -e "\033[92m[+]\033[0m $1"; }
fail() { echo -e "\033[91m[-]\033[0m $1"; }
info() { echo -e "\033[94m[*]\033[0m $1"; }

echo -e "\n\033[1;36m  awskill — Bug Bounty + Crypto Toolkit\033[0m"
echo -e "  by ouwibo | github.com/ouwibo/awskill\n"

# --- System deps ---
info "Installing system packages..."
if command -v apt-get &>/dev/null; then
    apt-get install -y nmap ffuf git curl unzip python3-pip 2>/dev/null | tail -1
elif command -v brew &>/dev/null; then
    brew install nmap ffuf git curl unzip 2>/dev/null | tail -1
fi
ok "System packages done"

# --- Go (upgrade if needed) ---
GO_VERSION="1.23.8"
if ! command -v go &>/dev/null || [[ "$(go version 2>/dev/null | grep -oP 'go\K[0-9.]+')" < "1.21" ]]; then
    info "Installing Go $GO_VERSION..."
    curl -fsSL "https://go.dev/dl/go${GO_VERSION}.${OS}-${ARCH}.tar.gz" | tar -C /usr/local -xz
    export PATH=/usr/local/go/bin:$PATH
    ok "Go $GO_VERSION installed"
fi
export GOPATH="$HOME/go"
export PATH="/usr/local/go/bin:$GOBIN:$PATH"

# --- Binary tools ---
install_bin() {
    local name=$1 url=$2
    info "Installing $name..."
    local tmp="/tmp/${name}_dl"
    curl -fsSL "$url" -o "$tmp" 2>/dev/null || { fail "$name: download failed"; return; }
    if [[ "$url" == *.zip ]]; then
        unzip -o "$tmp" -d "$GOBIN" "$name" 2>/dev/null && chmod +x "$GOBIN/$name" && ok "$name" || fail "$name: extract failed"
    elif [[ "$url" == *.tar.gz ]]; then
        tar -xzf "$tmp" -C "$GOBIN" "$name" 2>/dev/null || tar -xzf "$tmp" -C "$GOBIN" 2>/dev/null
        chmod +x "$GOBIN/$name" 2>/dev/null && ok "$name" || fail "$name: extract failed"
    fi
}

install_bin subfinder    "https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_${OS}_${ARCH}.zip"
install_bin httpx        "https://github.com/projectdiscovery/httpx/releases/download/v1.6.10/httpx_1.6.10_${OS}_${ARCH}.zip"
install_bin nuclei       "https://github.com/projectdiscovery/nuclei/releases/download/v3.3.9/nuclei_3.3.9_${OS}_${ARCH}.zip"
install_bin katana       "https://github.com/projectdiscovery/katana/releases/download/v1.1.2/katana_1.1.2_${OS}_${ARCH}.zip"
install_bin dnsx         "https://github.com/projectdiscovery/dnsx/releases/download/v1.2.1/dnsx_1.2.1_${OS}_${ARCH}.zip"
install_bin gau          "https://github.com/lc/gau/releases/download/v2.2.3/gau_${OS}_${ARCH}.tar.gz"
install_bin dalfox       "https://github.com/hahwul/dalfox/releases/download/v2.9.2/dalfox_${OS}_${ARCH}.tar.gz"
install_bin trufflehog   "https://github.com/trufflesecurity/trufflehog/releases/download/v3.88.2/trufflehog_${OS}_${ARCH}.tar.gz"
install_bin gitleaks     "https://github.com/gitleaks/gitleaks/releases/download/v8.24.3/gitleaks_8.24.3_${OS}_${ARCH}.tar.gz"
install_bin interactsh-client "https://github.com/projectdiscovery/interactsh/releases/download/v1.2.1/interactsh-client_1.2.1_${OS}_${ARCH}.zip"

# --- Go install tools ---
for pkg in \
    "github.com/tomnomnom/waybackurls@latest" \
    "github.com/tomnomnom/anew@latest" \
    "github.com/tomnomnom/qsreplace@latest"; do
    name=$(echo $pkg | awk -F'/' '{print $NF}' | cut -d@ -f1)
    info "go install $name..."
    go install "$pkg" 2>/dev/null && ok "$name" || fail "$name — fix: go install $pkg"
done

# --- Python tools ---
info "Installing Python tools..."
pip3 install sqlmap arjun wapiti3 slither-analyzer 2>/dev/null | tail -1
ok "Python tools done"

# --- Register skills to ~/.claude ---
SKILLS_DST="$HOME/.claude/skills"
CMDS_DST="$HOME/.claude/commands"
mkdir -p "$SKILLS_DST" "$CMDS_DST"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

count=0
for cat in "Security & Penetration Testing" "Finance & Crypto"; do
    cat_path="$BASE_DIR/$cat"
    [ -d "$cat_path" ] || continue
    for skill in "$cat_path"/*/; do
        name=$(basename "$skill")
        if [ -f "$skill/SKILL.md" ] && [ ! -d "$SKILLS_DST/$name" ]; then
            cp -r "$skill" "$SKILLS_DST/$name"
            ((count++))
        fi
    done
done
ok "$count skills registered to ~/.claude/skills"

# --- Verify ---
echo -e "\n\033[1;37m  Verification:\033[0m"
for t in subfinder httpx nuclei gau katana ffuf dnsx nmap dalfox trufflehog gitleaks waybackurls anew sqlmap arjun; do
    bin=$(command -v "$t" 2>/dev/null || echo "$GOBIN/$t")
    [ -x "$bin" ] && echo -e "  \033[92m✓\033[0m $t" || echo -e "  \033[91m✗\033[0m $t"
done

echo -e "\n  Add to ~/.bashrc or ~/.zshrc:"
echo -e "  \033[33mexport PATH=$GOBIN:/usr/local/go/bin:\$PATH\033[0m\n"
echo -e "  \033[1;32mReady! Try: python3 scripts/tools/scan.py target.com\033[0m\n"
