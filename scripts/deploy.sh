#!/usr/bin/env bash
# Deploy script — pull + rebuild + restart produkčního stacku.
# Spouštěno na VPS v /opt/realitni-asistent

set -euo pipefail

LOG() { echo -e "\033[0;32m[$(date +%H:%M:%S)] $*\033[0m"; }

cd "$(dirname "$0")/.."

LOG "Pulling latest main…"
git fetch origin
git reset --hard origin/main

LOG "Rebuilding services…"
docker compose --profile production pull --ignore-buildable
docker compose --profile production build --pull

LOG "Restarting stack…"
docker compose --profile production up -d --remove-orphans

LOG "Čekám na health check…"
for i in {1..20}; do
    if docker compose ps --format json | grep -q '"Health":"healthy"'; then
        LOG "✓ Backend healthy"
        break
    fi
    sleep 3
done

LOG "Status:"
docker compose --profile production ps

LOG ""
LOG "Logy: docker compose --profile production logs -f"
LOG "Deploy hotov ✓"
