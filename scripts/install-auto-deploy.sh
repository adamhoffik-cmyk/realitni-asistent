#!/usr/bin/env bash
# Jednorázová instalace auto-deploy systemd timeru.
# Spouští se na VPS jako root.
set -euo pipefail

REPO_DIR="/opt/realitni-asistent"
SYSTEMD_DIR="/etc/systemd/system"

echo "Instalace auto-deploy systemd timer…"

# Kopíruj unit soubory do systemd
cp "$REPO_DIR/scripts/asistent-auto-deploy.service" "$SYSTEMD_DIR/"
cp "$REPO_DIR/scripts/asistent-auto-deploy.timer" "$SYSTEMD_DIR/"
chmod 644 "$SYSTEMD_DIR/asistent-auto-deploy.service"
chmod 644 "$SYSTEMD_DIR/asistent-auto-deploy.timer"
chmod +x "$REPO_DIR/scripts/auto-deploy.sh"

# Zajisti existenci log souboru
touch /var/log/asistent-auto-deploy.log
chmod 644 /var/log/asistent-auto-deploy.log

# Reload systemd + enable + start
systemctl daemon-reload
systemctl enable --now asistent-auto-deploy.timer

echo ""
echo "✓ Instalace hotová"
echo ""
echo "Stav: systemctl status asistent-auto-deploy.timer"
echo "Log:  tail -f /var/log/asistent-auto-deploy.log"
echo "Manuální spuštění: systemctl start asistent-auto-deploy.service"
echo ""
systemctl status asistent-auto-deploy.timer --no-pager | head -10
