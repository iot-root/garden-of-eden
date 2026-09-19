#!/bin/bash
# Update an existing Garden of Eden install in place (issue #14):
# pull latest code, refresh Python deps, and restart services.
set -euo pipefail

BIN_DIR=$(dirname "$(readlink -f "$0")")
INSTALL_DIR=$(realpath "$BIN_DIR/..")

echo "Updating Garden of Eden in $INSTALL_DIR"
cd "$INSTALL_DIR"

# Pull latest on the current branch.
git pull --ff-only

# Refresh dependencies inside the venv.
if [ -d "$INSTALL_DIR/venv" ]; then
    # shellcheck disable=SC1091
    source "$INSTALL_DIR/venv/bin/activate"
    pip install -r "$INSTALL_DIR/requirements.txt"
    deactivate
else
    echo "WARNING: venv not found; run bin/setup.sh first." >&2
fi

# Restart services if installed.
for svc in mqtt.service garden-api.service; do
    if systemctl list-unit-files | grep -q "^${svc}"; then
        sudo systemctl restart "$svc"
        echo "Restarted $svc"
    fi
done

echo "Update complete."
