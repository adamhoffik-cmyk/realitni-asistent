#!/usr/bin/env bash
# Obnoví Tailscale HTTPS cert pro VPS + reloadne Caddy.
# Spouští systemd timer každých 7 dní.
set -euo pipefail

REPO_DIR="/opt/realitni-asistent"
CERT_DIR="$REPO_DIR/tailscale-certs"
LOG="/var/log/asistent-tailscale-cert.log"

log() { echo "$(date -Is) — $*" | tee -a "$LOG"; }

# Hostname z .env
if [[ -f "$REPO_DIR/.env" ]]; then
    HOSTNAME=$(grep -E '^TAILSCALE_HOSTNAME=' "$REPO_DIR/.env" | cut -d= -f2-)
fi
if [[ -z "${HOSTNAME:-}" ]]; then
    log "⚠ TAILSCALE_HOSTNAME nenastaveno v .env"
    exit 1
fi

# Kontrola — je cert starší než 30 dní?
if [[ -f "$CERT_DIR/cert.pem" ]]; then
    expiry_epoch=$(openssl x509 -enddate -noout -in "$CERT_DIR/cert.pem" | cut -d= -f2 | xargs -I {} date -d {} +%s)
    now_epoch=$(date +%s)
    days_left=$(( (expiry_epoch - now_epoch) / 86400 ))
    if [[ $days_left -gt 30 ]]; then
        log "Cert má ještě $days_left dní — renewal přeskočen"
        exit 0
    fi
    log "Cert vyprší za $days_left dní — obnovuji"
fi

mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

if ! tailscale cert --cert-file=cert.pem.new --key-file=key.pem.new "$HOSTNAME" 2>&1 | tee -a "$LOG"; then
    log "⚠ tailscale cert selhal"
    rm -f cert.pem.new key.pem.new
    exit 1
fi

mv cert.pem.new cert.pem
mv key.pem.new key.pem
log "✓ Cert obnoven pro $HOSTNAME"

# Reload Caddy aby načetl nový cert
docker compose --profile production exec -T caddy caddy reload --config /etc/caddy/Caddyfile 2>&1 | tee -a "$LOG" || {
    log "⚠ Caddy reload selhal, restartuji kontejner"
    docker compose --profile production restart caddy
}

log "✓ Renewal hotov"
