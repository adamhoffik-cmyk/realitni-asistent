#!/usr/bin/env bash
# Generuje bcrypt hash pro Caddy BasicAuth.
# Použití: ./scripts/gen-basic-auth.sh

set -euo pipefail

read -s -p "Zadej heslo: " PASSWORD
echo
read -s -p "Zopakuj heslo: " PASSWORD_CONFIRM
echo

if [[ "$PASSWORD" != "$PASSWORD_CONFIRM" ]]; then
    echo "❌ Hesla se neshodují"
    exit 1
fi

if [[ ${#PASSWORD} -lt 10 ]]; then
    echo "⚠ Doporučené minimum je 10 znaků, tvé má ${#PASSWORD}. Pokračovat? (y/N)"
    read -r answer
    [[ "$answer" != "y" ]] && exit 1
fi

echo ""
echo "Generuji bcrypt hash…"
HASH=$(docker run --rm caddy:2.8-alpine caddy hash-password --plaintext "$PASSWORD")

echo ""
echo "✓ Hash vygenerován. Přidej do .env:"
echo ""
echo "CADDY_BASIC_AUTH_USER=adam"
echo "CADDY_BASIC_AUTH_HASH=$HASH"
echo ""
