#!/bin/bash
# Nightly auto-update (invoked by garden-autoupdate.timer).
#
# Fast-forwards the current branch from origin and, ONLY if something actually
# changed, refreshes deps and restarts the services. Designed to be safe to run
# unattended on live hardware:
#   * --ff-only: never rewrites history or discards local work; if the branch
#     can't fast-forward (e.g. it was force-pushed) it logs and bails.
#   * no-op when already up to date, so it doesn't cycle the light/pump for
#     nothing.
#   * a service restart ends with the pump OFF (graceful_shutdown), so an
#     interrupted watering run fails safe.
set -uo pipefail

BIN_DIR=$(dirname "$(readlink -f "$0")")
INSTALL_DIR=$(realpath "$BIN_DIR/..")
cd "$INSTALL_DIR" || exit 1

log() { echo "[garden-autoupdate] $*"; }

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || { log "not a git repo; abort"; exit 1; }

if ! git fetch --quiet origin "$branch"; then
    log "git fetch failed (offline?); will retry next run"
    exit 0
fi

local_rev=$(git rev-parse HEAD)
remote_rev=$(git rev-parse "origin/$branch" 2>/dev/null) || { log "no origin/$branch; abort"; exit 0; }

if [ "$local_rev" = "$remote_rev" ]; then
    log "already up to date ($branch @ ${local_rev:0:7})"
    exit 0
fi

log "update available on $branch: ${local_rev:0:7} -> ${remote_rev:0:7}"

if ! git merge-base --is-ancestor "$local_rev" "$remote_rev"; then
    log "cannot fast-forward (branch diverged/force-pushed); skipping to stay safe"
    exit 0
fi

if ! git pull --ff-only --quiet; then
    log "git pull --ff-only failed; skipping"
    exit 0
fi
log "pulled to $(git rev-parse --short HEAD)"

# Refresh Python deps (best effort; a failure here shouldn't block the restart).
if [ -d "$INSTALL_DIR/venv" ]; then
    # shellcheck disable=SC1091
    source "$INSTALL_DIR/venv/bin/activate"
    pip install --quiet -r "$INSTALL_DIR/requirements.txt" || log "pip install reported errors"
    deactivate
fi

# Restart only the installed services. This is reached only when code changed.
for svc in mqtt.service garden-api.service; do
    if systemctl list-unit-files | grep -q "^${svc}"; then
        sudo systemctl restart "$svc" && log "restarted $svc"
    fi
done

log "update complete -> $(git rev-parse --short HEAD)"
