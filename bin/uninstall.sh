#!/bin/bash
# Reverse bin/setup.sh: stop and remove the Garden of Eden services, restore the
# system files that setup.sh backed up, and remove our cron entries.
#
# Left in place on purpose (harmless, and annoying/risky to revert): installed
# apt packages, group membership, SSH being enabled, and the hostname. Pass
# --purge-hostname to also restore the previous hostname.
set -u

BIN_DIR=$(dirname "$(readlink -f "$0")")
INSTALL_DIR=$(realpath "$BIN_DIR/..")

PURGE_HOSTNAME=false
[ "${1:-}" = "--purge-hostname" ] && PURGE_HOSTNAME=true

echo "Stopping and removing services..."
for svc in garden-api.service mqtt.service; do
    sudo systemctl disable --now "$svc" 2>/dev/null
    sudo rm -f "/etc/systemd/system/$svc"
done
sudo systemctl daemon-reload 2>/dev/null

echo "Removing CLI symlinks and udev rules..."
sudo rm -f /usr/local/bin/light /usr/local/bin/water /usr/local/bin/garden-update
sudo rm -f /etc/udev/rules.d/99-gardyn-cameras.rules
sudo udevadm control --reload-rules 2>/dev/null

echo "Removing our cron entries..."
( crontab -l 2>/dev/null | grep -v 'garden-of-eden' | grep -v 'garden-timelapse' ) | crontab - 2>/dev/null

echo "Restoring backed-up system files..."
for f in /boot/firmware/config.txt /boot/config.txt /etc/modules /etc/hosts; do
    if [ -f "${f}.garden.bak" ]; then
        sudo cp -a "${f}.garden.bak" "$f" && echo "  restored $f"
    fi
done

if [ "$PURGE_HOSTNAME" = "true" ] && [ -f /etc/hostname.garden.bak ]; then
    sudo cp -a /etc/hostname.garden.bak /etc/hostname
    sudo hostnamectl set-hostname "$(cat /etc/hostname)" 2>/dev/null
    echo "  restored hostname"
fi

echo "Done. Installed apt packages, group membership, and SSH were left enabled."
echo "A reboot is recommended to apply restored boot/I2C settings."
