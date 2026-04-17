#!/usr/bin/env bash
# Setup script pro první instalaci na Hetzner VPS (Ubuntu 24.04).
# Spustit jako root: curl | bash NEBO:
#   ssh root@46.225.58.232
#   bash <(cat setup-vps.sh)
#
# Předpoklad: Ubuntu 24.04, Claude Code CLI už nainstalovaný v /usr/bin/claude

set -euo pipefail

LOG() { echo -e "\033[0;32m[$(date +%H:%M:%S)] $*\033[0m"; }
ERR() { echo -e "\033[0;31m[$(date +%H:%M:%S)] $*\033[0m" >&2; }

if [[ $EUID -ne 0 ]]; then
    ERR "Spusť jako root (sudo su)"
    exit 1
fi

LOG "=== Realitní Asistent — setup VPS ==="
LOG "OS: $(lsb_release -d | cut -f2)"

# --- 1. Systémové update ---
LOG "Aktualizace balíčků…"
apt-get update -qq
apt-get upgrade -y -qq

# --- 2. Základní nástroje ---
LOG "Základní nástroje (git, curl, ca-certificates)…"
apt-get install -y -qq \
    git curl ca-certificates gnupg lsb-release \
    apt-transport-https software-properties-common \
    htop ncdu net-tools ufw

# --- 3. Docker + Compose ---
if ! command -v docker &>/dev/null; then
    LOG "Instalace Dockeru…"
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        > /etc/apt/sources.list.d/docker.list
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable --now docker
    LOG "Docker $(docker --version) ✓"
else
    LOG "Docker už nainstalovaný: $(docker --version)"
fi

# --- 4. Firewall ---
LOG "Firewall (ufw)…"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp  comment 'HTTP (Caddy)'
ufw allow 443/tcp comment 'HTTPS (Caddy)'
ufw allow 443/udp comment 'HTTP/3 QUIC'
ufw --force enable
ufw status numbered

# --- 5. Claude Code CLI check ---
if command -v claude &>/dev/null; then
    LOG "Claude Code CLI: $(claude --version) ✓"
else
    ERR "Claude Code CLI nenalezen! Musí být v /usr/bin/claude."
    exit 1
fi

# --- 6. Plugin ceske-realitni-pravo ---
LOG "Kontrola pluginu ceske-realitni-pravo…"
if ! ls ~/.claude/plugins/marketplaces 2>/dev/null | grep -qi "ceske-realitni"; then
    LOG "⚠ Plugin ceske-realitni-pravo zatím není nainstalovaný."
    LOG "  Instalace proběhne interaktivně:"
    LOG "    claude plugins install ceske-realitni-pravo"
    LOG "  (Až na to bude čas — je to nutné pro právní skilly.)"
else
    LOG "Plugin ceske-realitni-pravo ✓"
fi

# --- 7. Struktura ---
REPO_DIR="/opt/realitni-asistent"
if [[ -d "$REPO_DIR" ]]; then
    LOG "Repo už existuje: $REPO_DIR"
    cd "$REPO_DIR"
    git pull || true
else
    LOG "Klonování repa…"
    git clone https://github.com/adamhoffik-cmyk/realitni-asistent.git "$REPO_DIR"
    cd "$REPO_DIR"
fi

# --- 8. .env ---
if [[ ! -f .env ]]; then
    LOG ".env neexistuje — vytvářím z .env.example"
    cp .env.example .env
    echo ""
    ERR "ÚPRAV .env před prvním spuštěním!"
    ERR "  - CADDY_BASIC_AUTH_HASH (viz scripts/gen-basic-auth.sh)"
    ERR "  - PII_ENCRYPTION_KEY (viz níže)"
    ERR "  - BACKEND_SECRET_KEY"
    ERR "  - SEARXNG_SECRET"
    ERR "  - APP_ENV=production"
    ERR "  - CADDY_DOMAIN=asistent.reality-pittner.cz"
fi

# --- 9. Generování PII key (jen info) ---
LOG ""
LOG "Pro PII_ENCRYPTION_KEY použij:"
LOG "  python3 -c \"import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())\""
LOG ""

# --- 10. Data dir ---
mkdir -p backend/data/{chroma,reference_articles,articles/drafts,articles/published,transcripts,video_scripts,uploads}

# --- 11. Caddy log dir ---
mkdir -p /var/log/caddy

LOG ""
LOG "=== Setup hotov. Další kroky: ==="
LOG "1. cd $REPO_DIR"
LOG "2. Upravit .env (viz výše)"
LOG "3. Vygenerovat Caddy BasicAuth hash:"
LOG "     docker run --rm caddy:2.8-alpine caddy hash-password --plaintext 'TvojeHeslo'"
LOG "4. Nastavit DNS A záznam asistent.reality-pittner.cz → 46.225.58.232"
LOG "5. docker compose --profile production up -d --build"
LOG "6. Sledovat logy: docker compose logs -f"
