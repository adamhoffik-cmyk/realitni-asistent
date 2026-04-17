#!/usr/bin/env bash
# Interaktivní generátor .env pro produkci na VPS.
# Vygeneruje všechny secrets (PII, backend, searxng, BasicAuth bcrypt)
# a zapíše je do .env (musí už existovat z setup-vps.sh).
#
# Použití (z /opt/realitni-asistent):
#   bash scripts/gen-env.sh

set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
    echo "❌ .env neexistuje. Spusť nejdřív setup-vps.sh"
    exit 1
fi

LOG() { echo -e "\033[0;32m$*\033[0m"; }
WARN() { echo -e "\033[0;33m$*\033[0m"; }

LOG "=== Generátor .env secrets ==="
echo ""

read -r -p "Doména [default: asistent.46-225-58-232.nip.io]: " DOMAIN
DOMAIN="${DOMAIN:-asistent.46-225-58-232.nip.io}"

read -r -p "E-mail pro Let's Encrypt [default: adam.hoffik@gmail.com]: " EMAIL
EMAIL="${EMAIL:-adam.hoffik@gmail.com}"

read -r -p "BasicAuth uživatel [default: adam]: " BA_USER
BA_USER="${BA_USER:-adam}"

# Heslo s validací
while true; do
    read -rsp "BasicAuth heslo (min 10 znaků): " PW1; echo
    if [[ ${#PW1} -lt 10 ]]; then
        WARN "⚠ Min. 10 znaků, máš ${#PW1}. Zkus znovu."
        continue
    fi
    read -rsp "Zopakuj heslo: " PW2; echo
    if [[ "$PW1" != "$PW2" ]]; then
        WARN "⚠ Hesla se neshodují. Zkus znovu."
        continue
    fi
    break
done

LOG ""
LOG "Generuji bcrypt hash (potřeba Dockeru)…"
if ! command -v docker &>/dev/null; then
    echo "❌ docker nenalezen. Spusť nejdřív setup-vps.sh"
    exit 1
fi
BA_HASH=$(docker run --rm caddy:2.8-alpine caddy hash-password --plaintext "$PW1")

LOG "Generuji secrets (PII, backend, searxng)…"
gen_key() { python3 -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"; }
PII_KEY=$(gen_key)
BACKEND_KEY=$(gen_key)
SEARXNG_KEY=$(gen_key)

LOG "Zapisuji do .env…"

# Escape $ v bcrypt hashi — docker-compose interpretuje $FOO jako env var.
# Double $$ = literal $ pro docker-compose.
BA_HASH_ESC="${BA_HASH//\$/\$\$}"

# Sed edit-in-place
sed -i "s|^APP_ENV=.*|APP_ENV=production|" .env
sed -i "s|^APP_BASE_URL=.*|APP_BASE_URL=https://$DOMAIN|" .env
sed -i "s|^BACKEND_CORS_ORIGINS=.*|BACKEND_CORS_ORIGINS=https://$DOMAIN|" .env
sed -i "s|^BACKEND_SECRET_KEY=.*|BACKEND_SECRET_KEY=$BACKEND_KEY|" .env
sed -i "s|^PII_ENCRYPTION_KEY=.*|PII_ENCRYPTION_KEY=$PII_KEY|" .env
sed -i "s|^SEARXNG_SECRET=.*|SEARXNG_SECRET=$SEARXNG_KEY|" .env
sed -i "s|^CADDY_BASIC_AUTH_USER=.*|CADDY_BASIC_AUTH_USER=$BA_USER|" .env
sed -i "s|^CADDY_BASIC_AUTH_HASH=.*|CADDY_BASIC_AUTH_HASH=$BA_HASH_ESC|" .env
sed -i "s|^CADDY_DOMAIN=.*|CADDY_DOMAIN=$DOMAIN|" .env
sed -i "s|^CADDY_EMAIL=.*|CADDY_EMAIL=$EMAIL|" .env
sed -i "s|^NEXT_PUBLIC_API_BASE_URL=.*|NEXT_PUBLIC_API_BASE_URL=https://$DOMAIN|" .env
sed -i "s|^NEXT_PUBLIC_WS_BASE_URL=.*|NEXT_PUBLIC_WS_BASE_URL=wss://$DOMAIN|" .env
sed -i "s|^GOOGLE_REDIRECT_URI=.*|GOOGLE_REDIRECT_URI=https://$DOMAIN/api/auth/google/callback|" .env

# Claude home mount pro backend
CLAUDE_HOME="${HOME}/.claude"
CLAUDE_JSON="${HOME}/.claude.json"
if grep -q "^CLAUDE_HOME=" .env; then
    sed -i "s|^CLAUDE_HOME=.*|CLAUDE_HOME=$CLAUDE_HOME|" .env
else
    echo "CLAUDE_HOME=$CLAUDE_HOME" >> .env
fi
if grep -q "^CLAUDE_JSON=" .env; then
    sed -i "s|^CLAUDE_JSON=.*|CLAUDE_JSON=$CLAUDE_JSON|" .env
else
    echo "CLAUDE_JSON=$CLAUDE_JSON" >> .env
fi

echo ""
LOG "=== .env připravený ✓ ==="
echo "  Doména:        https://$DOMAIN"
echo "  BasicAuth:     $BA_USER (heslo uloženo jako bcrypt hash)"
echo "  Claude home:   $CLAUDE_HOME"
echo ""
LOG "Další kroky:"
echo "  1. claude plugins install ceske-realitni-pravo  # (pokud ještě není)"
echo "  2. docker compose --profile production up -d --build"
echo ""
WARN "⚠ Nikdy necommituj .env do gitu (.gitignore to hlídá)."
