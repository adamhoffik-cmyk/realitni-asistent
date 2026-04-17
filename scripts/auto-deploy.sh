#!/usr/bin/env bash
# Auto-deploy skript — detekuje nové commity na origin/main a rebuildne
# Spouští ho systemd timer (viz auto-deploy.service + .timer) každou minutu.
#
# Log: /var/log/asistent-auto-deploy.log (posledních 500 řádků)
set -euo pipefail

REPO_DIR="/opt/realitni-asistent"
LOG="/var/log/asistent-auto-deploy.log"
LOCK="/tmp/asistent-deploy.lock"

cd "$REPO_DIR"

# Ochrana proti paralelnímu běhu (timer spustí už během předchozího buildu)
exec 200>"$LOCK"
flock -n 200 || { echo "$(date -Is) — už běží jiný deploy, přeskakuji"; exit 0; }

log() { echo "$(date -Is) — $*" | tee -a "$LOG"; }

# Rotace logu — nech si posledních 500 řádků
if [[ -f "$LOG" ]] && [[ $(wc -l < "$LOG") -gt 500 ]]; then
    tail -500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi

# Zjisti, zda máme novou verzi na origin
git fetch --quiet origin main

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [[ "$LOCAL" == "$REMOTE" ]]; then
    # Žádná změna — potichu konec (nezahlušuj log)
    exit 0
fi

log "=== Nový commit detekován ==="
log "   local=$LOCAL"
log "   remote=$REMOTE"

# Zobraz změněné soubory (pro rozhodnutí co rebuildovat)
CHANGED=$(git diff --name-only "$LOCAL" "$REMOTE")
log "Změněno:"
echo "$CHANGED" | sed 's/^/   /' | tee -a "$LOG"

# Pull
git pull --ff-only origin main 2>&1 | tee -a "$LOG"

# Rozhodni co rebuildovat — inteligentní logika
REBUILD_BACKEND=false
REBUILD_FRONTEND=false
RESTART_ONLY_BACKEND=false
RESTART_ONLY_FRONTEND=false

if echo "$CHANGED" | grep -qE '^backend/(Dockerfile|pyproject\.toml)'; then
    REBUILD_BACKEND=true
elif echo "$CHANGED" | grep -qE '^backend/app/'; then
    REBUILD_BACKEND=true  # Python kód — rebuild přes COPY layer
fi

if echo "$CHANGED" | grep -qE '^frontend/(Dockerfile|package\.json|package-lock\.json)'; then
    REBUILD_FRONTEND=true
elif echo "$CHANGED" | grep -qE '^frontend/(app|components|lib|public)/'; then
    REBUILD_FRONTEND=true
fi

if echo "$CHANGED" | grep -qE '^(docker-compose\.yml|Caddyfile)'; then
    REBUILD_BACKEND=true
    REBUILD_FRONTEND=true
fi

if echo "$CHANGED" | grep -qE '^scripts/|^docs/|^README|^\.gitignore|^plugins/'; then
    # Jen config/doc změny — nic nemusíme rebuildovat
    if [[ "$REBUILD_BACKEND" == false && "$REBUILD_FRONTEND" == false ]]; then
        log "Jen doc/script změny — nic se nerebuildu"
        exit 0
    fi
fi

# Rebuild + restart
SERVICES=()
[[ "$REBUILD_BACKEND" == true ]] && SERVICES+=("backend")
[[ "$REBUILD_FRONTEND" == true ]] && SERVICES+=("frontend")

if [[ ${#SERVICES[@]} -gt 0 ]]; then
    log "Buildim + restartuji: ${SERVICES[*]}"
    docker compose --profile production up -d --build "${SERVICES[@]}" 2>&1 | tee -a "$LOG"

    # Úklid staré image layers (uvolni disk)
    docker image prune -f 2>&1 | tail -2 | tee -a "$LOG"
fi

log "=== Deploy hotov ✓ ==="
