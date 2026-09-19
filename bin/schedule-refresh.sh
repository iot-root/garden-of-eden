#!/usr/bin/env bash

# Re-apply the saved schedule. Run nightly by cron (added automatically while
# Vacation mode is active) so vacation reverts to the normal schedule once its
# end date passes.

set -euo pipefail

GOE_PATH=$(realpath "$(dirname "$(readlink -e "${0}")")/..")
export PYTHONPATH="${GOE_PATH}${PYTHONPATH:+:${PYTHONPATH}}"

"${GOE_PATH}/venv/bin/python" -c "from app.sensors.schedule import schedule as s; s.refresh()"
