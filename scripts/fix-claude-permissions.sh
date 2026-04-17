#!/usr/bin/env bash
# Jednorázové nastavení permissions pro non-root backend kontejner.
#
# Důvod: Claude Code CLI odmítá --dangerously-skip-permissions pod rootem.
# Kontejner tedy běží jako UID 1000. Mountované soubory (~/.claude,
# ~/.claude.json, data/) musí být vlastněné UID 1000.
#
# Jsou ztrátové pro host (root) jen v tom smyslu, že root musí být při
# manipulaci explicitní (sudo). Root má stejně přístup ke všemu.
set -euo pipefail

LOG() { echo -e "\033[0;32m$*\033[0m"; }
WARN() { echo -e "\033[0;33m$*\033[0m"; }

REPO_DIR="/opt/realitni-asistent"
CLAUDE_HOME="${HOME}/.claude"
CLAUDE_JSON="${HOME}/.claude.json"
DATA_DIR="$REPO_DIR/backend/data"

LOG "=== Nastavuji permissions pro non-root container (UID 1000) ==="

if [[ -d "$CLAUDE_HOME" ]]; then
    chown -R 1000:1000 "$CLAUDE_HOME"
    LOG "✓ $CLAUDE_HOME → 1000:1000"
else
    WARN "⚠ $CLAUDE_HOME neexistuje — možná jsi nespustil claude login"
fi

if [[ -f "$CLAUDE_JSON" ]]; then
    chown 1000:1000 "$CLAUDE_JSON"
    LOG "✓ $CLAUDE_JSON → 1000:1000"
else
    WARN "⚠ $CLAUDE_JSON neexistuje — obnov z backupu (viz docs/WELCOME_BACK.md)"
fi

if [[ -d "$DATA_DIR" ]]; then
    chown -R 1000:1000 "$DATA_DIR"
    LOG "✓ $DATA_DIR → 1000:1000"
fi

LOG ""
LOG "Hotovo. Teď rebuild kontejneru:"
LOG "  cd $REPO_DIR && docker compose --profile production up -d --build backend"
