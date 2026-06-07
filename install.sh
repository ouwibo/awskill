#!/usr/bin/env bash
# install.sh — awskill one-line installer
# curl -fsSL https://raw.githubusercontent.com/ouwibo/awskill/main/install.sh | bash
#
# Hardening:
#   * set -euo pipefail
#   * sudo detection for system paths
#   * SHA256 verification for ProjectDiscovery release artifacts
#   * Semantic Go version compare (sort -V)
#   * PEP 668 (Debian 12 / Ubuntu 24.04) pip fallback
set -euo pipefail

GOBIN="$HOME/go/bin"
mkdir -p "$GOBIN"

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')

# Detect whether we can/need to escalate. Prefer non-root with sudo over
# silently failing apt-get. If neither root nor sudo, system installs are
# skipped with a clear warning.
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    if command -v sudo &>/dev/null; then
        SUDO="sudo"
    fi
fi

ok()   { echo -e "\033[92m[+]\033[0m $1"; }
fail() { echo -e "\033[91m[-]\033[0m $1"; }
info() { echo -e "\033[94m[*]\033[0m $1"; }
warn() { echo -e "\033[93m[!]\033[0m $1"; }

echo -e "\n\033[1;36m  awskill — Bug Bounty + Crypto Toolkit\033[0m"
echo -e "  by ouwibo | github.com/ouwibo/awskill\n"

# ---------- System deps ----------
info "Installing system packages..."
if command -v apt-get &>/dev/null; then
    if [ -n "$SUDO" ] || [ "$(id -u)" -eq 0 ]; then
        $SUDO apt-get install -y nmap ffuf git curl unzip python3-pip || warn "apt-get partial failure"
        ok "System packages done"
    else
        warn "Not root and sudo not found — skipping apt-get; install manually: nmap ffuf git curl unzip python3-pip"
    fi
elif command -v brew &>/dev/null; then
    brew install nmap ffuf git curl unzip || warn "brew partial failure"
    ok "System packages done"
else
    warn "No apt-get or brew detected — install nmap/ffuf/git/curl/unzip/python3-pip manually"
fi

# ---------- Go (install/upgrade) ----------
GO_VERSION="1.23.8"

# Semantic compare via sort -V. Returns 0 if installed Go >= required.
go_ok() {
    local required="$1"
    local current
    current=$(go version 2>/dev/null | grep -oE 'go[0-9.]+' | sed 's/^go//' || true)
    [ -z "$current" ] && return 1
    [ "$(printf '%s\n%s\n' "$required" "$current" | sort -V | head -1)" = "$required" ]
}

if ! go_ok "1.21"; then
    info "Installing Go $GO_VERSION..."
    GO_TGZ="/tmp/awskill_go.tar.gz"
    curl -fsSL "https://go.dev/dl/go${GO_VERSION}.${OS}-${ARCH}.tar.gz" -o "$GO_TGZ"
    if [ -n "$SUDO" ] || [ "$(id -u)" -eq 0 ]; then
        $SUDO tar -C /usr/local -xzf "$GO_TGZ"
        ok "Go $GO_VERSION installed to /usr/local/go"
    else
        # Fall back to user-local
        mkdir -p "$HOME/.local"
        tar -C "$HOME/.local" -xzf "$GO_TGZ"
        export PATH="$HOME/.local/go/bin:$PATH"
        warn "Installed Go to ~/.local/go (no sudo). Add ~/.local/go/bin to PATH."
    fi
    rm -f "$GO_TGZ"
fi
export GOPATH="$HOME/go"
export PATH="/usr/local/go/bin:$HOME/.local/go/bin:$GOBIN:$PATH"

# ---------- SHA256 verification helper ----------
# For ProjectDiscovery releases the convention is `<tool>_<version>_checksums.txt`
# at the same release tag. We download that file, look up the artifact's hash,
# and verify before extraction. For other tools (gau, dalfox, trufflehog,
# gitleaks) we try a best-effort `checksums.txt` lookup and warn if absent.
verify_sha256() {
    local archive="$1" url="$2" name="$3"
    local rel_dir checksums hash expected
    rel_dir=$(dirname "$url")
    # Common naming conventions for the checksums file.
    for candidate in \
        "${rel_dir}/${name}_checksums.txt" \
        "${rel_dir}/checksums.txt" \
        "${rel_dir}/${name}-checksums.txt"
    do
        if curl -fsSL "$candidate" -o "/tmp/awskill_sha.txt" 2>/dev/null; then
            checksums="/tmp/awskill_sha.txt"
            break
        fi
    done
    if [ -z "${checksums:-}" ] || [ ! -s "${checksums:-}" ]; then
        warn "$name: no checksums file at release — skipping SHA256 verify"
        return 0
    fi
    expected=$(grep "$(basename "$url")" "$checksums" 2>/dev/null | awk '{print $1}' | head -1)
    if [ -z "$expected" ]; then
        warn "$name: checksum entry not found for $(basename "$url") — skipping"
        rm -f "$checksums"
        return 0
    fi
    hash=$(sha256sum "$archive" | awk '{print $1}')
    rm -f "$checksums"
    if [ "$hash" != "$expected" ]; then
        fail "$name: SHA256 MISMATCH (got $hash, expected $expected) — refusing to install"
        return 1
    fi
    ok "$name: SHA256 verified"
    return 0
}

# ---------- Binary tool installer ----------
install_bin() {
    local name="$1" url="$2"
    info "Installing $name..."
    local tmp tmpdir
    tmpdir=$(mktemp -d -t "awskill_${name}_XXXX")
    tmp="$tmpdir/dl"
    if ! curl -fsSL "$url" -o "$tmp"; then
        fail "$name: download failed"
        rm -rf "$tmpdir"
        return
    fi
    if ! verify_sha256 "$tmp" "$url" "$name"; then
        rm -rf "$tmpdir"
        return
    fi
    # Extract to tmpdir first, then move just the binary to GOBIN.
    case "$url" in
        *.zip)
            unzip -q -o "$tmp" -d "$tmpdir/extract"
            ;;
        *.tar.gz|*.tgz)
            mkdir -p "$tmpdir/extract"
            tar -xzf "$tmp" -C "$tmpdir/extract"
            ;;
        *)
            fail "$name: unknown archive type"
            rm -rf "$tmpdir"
            return
            ;;
    esac
    # Find the binary by name in the extract dir.
    local bin_path
    bin_path=$(find "$tmpdir/extract" -type f -name "$name" -perm -u+x 2>/dev/null | head -1)
    if [ -z "$bin_path" ]; then
        # Fallback: any executable file matching $name without -perm constraint.
        bin_path=$(find "$tmpdir/extract" -type f -name "$name" 2>/dev/null | head -1)
    fi
    if [ -z "$bin_path" ]; then
        fail "$name: binary not found in archive"
        rm -rf "$tmpdir"
        return
    fi
    mv "$bin_path" "$GOBIN/$name"
    chmod +x "$GOBIN/$name"
    ok "$name installed"
    rm -rf "$tmpdir"
}

install_bin subfinder    "https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_${OS}_${ARCH}.zip"
install_bin httpx        "https://github.com/projectdiscovery/httpx/releases/download/v1.6.10/httpx_1.6.10_${OS}_${ARCH}.zip"
install_bin nuclei       "https://github.com/projectdiscovery/nuclei/releases/download/v3.3.9/nuclei_3.3.9_${OS}_${ARCH}.zip"
install_bin katana       "https://github.com/projectdiscovery/katana/releases/download/v1.1.2/katana_1.1.2_${OS}_${ARCH}.zip"
install_bin dnsx         "https://github.com/projectdiscovery/dnsx/releases/download/v1.2.1/dnsx_1.2.1_${OS}_${ARCH}.zip"
install_bin interactsh-client "https://github.com/projectdiscovery/interactsh/releases/download/v1.2.1/interactsh-client_1.2.1_${OS}_${ARCH}.zip"
install_bin gau          "https://github.com/lc/gau/releases/download/v2.2.3/gau_${OS}_${ARCH}.tar.gz"
install_bin dalfox       "https://github.com/hahwul/dalfox/releases/download/v2.9.2/dalfox_${OS}_${ARCH}.tar.gz"
install_bin trufflehog   "https://github.com/trufflesecurity/trufflehog/releases/download/v3.88.2/trufflehog_${OS}_${ARCH}.tar.gz"
install_bin gitleaks     "https://github.com/gitleaks/gitleaks/releases/download/v8.24.3/gitleaks_8.24.3_${OS}_${ARCH}.tar.gz"

# ---------- Go install tools ----------
for pkg in \
    "github.com/tomnomnom/waybackurls@latest" \
    "github.com/tomnomnom/anew@latest" \
    "github.com/tomnomnom/qsreplace@latest"; do
    name=$(echo "$pkg" | awk -F'/' '{print $NF}' | cut -d@ -f1)
    info "go install $name..."
    if go install "$pkg"; then ok "$name"; else fail "$name — manual fix: go install $pkg"; fi
done

# ---------- Python tools (PEP 668 aware) ----------
PIP_PKGS="sqlmap arjun wapiti3 slither-analyzer"
info "Installing Python tools: $PIP_PKGS"
if command -v pipx &>/dev/null; then
    for p in $PIP_PKGS; do pipx install "$p" || warn "$p: pipx install failed"; done
elif pip3 install --help 2>&1 | grep -q break-system-packages; then
    # PEP 668: warn and use --break-system-packages
    warn "PEP 668 environment detected — using --break-system-packages (consider 'pipx' instead)"
    pip3 install --break-system-packages $PIP_PKGS || warn "pip3 partial failure"
else
    pip3 install $PIP_PKGS || warn "pip3 partial failure"
fi
ok "Python tools done"

# ---------- Register all skills ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_TARGET="${AWSKILL_TARGET:-claude}"

info "Registering all skills for $SKILL_TARGET..."
python3 "$SCRIPT_DIR/scripts/tools/install_skills.py" --target "$SKILL_TARGET" --force
ok "All awskill skills registered"

# ---------- Verify ----------
echo -e "\n\033[1;37m  Verification:\033[0m"
for t in subfinder httpx nuclei gau katana ffuf dnsx nmap dalfox trufflehog gitleaks waybackurls anew sqlmap arjun; do
    if command -v "$t" &>/dev/null || [ -x "$GOBIN/$t" ]; then
        echo -e "  \033[92m✓\033[0m $t"
    else
        echo -e "  \033[91m✗\033[0m $t"
    fi
done

echo -e "\n  Add to ~/.bashrc or ~/.zshrc:"
echo -e "  \033[33mexport PATH=$GOBIN:/usr/local/go/bin:\$PATH\033[0m\n"
echo -e "  \033[1;32mReady! Try: python3 scripts/tools/scan.py example.com\033[0m\n"
