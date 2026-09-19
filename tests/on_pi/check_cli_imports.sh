#!/bin/bash
# Verifies #129: the driver scripts run directly (README examples,
# bin/get-sensor-data.sh) can import the root config.py.
#
# Runs every driver from / with PYTHONPATH cleared, so only the script's own
# sys.path handling can find config.py. Light and pump are run with --help,
# which imports everything but never touches the pins. Sensor scripts only
# read, so they are run for real; a sensor that isn't connected is fine as
# long as the failure isn't an import error.
#
#   tests/on_pi/check_cli_imports.sh            # uses ./venv/bin/python
#   PYTHON=python3 tests/on_pi/check_cli_imports.sh
set -u

REPO=$(cd "$(dirname "$0")/../.." && pwd)
PY=${PYTHON:-$REPO/venv/bin/python}
PASS=0
FAIL=0

ok() { echo "  PASS  $*"; PASS=$((PASS + 1)); }
bad() { echo "  FAIL  $*"; FAIL=$((FAIL + 1)); }

run_driver() { # run_driver <relative script> [args...]  -> sets OUT and RC
    local script="$1"; shift
    OUT=$(cd / && env -u PYTHONPATH timeout 60 "$PY" "$REPO/$script" "$@" 2>&1)
    RC=$?
}

import_error() { grep -qE "ModuleNotFoundError|ImportError|No module named" <<<"$OUT"; }

echo "== actuator drivers (--help only; pins untouched)"
for script in app/sensors/light/light.py app/sensors/pump/pump.py; do
    run_driver "$script" --help
    if [ "$RC" -eq 0 ] && grep -q "^usage:" <<<"$OUT"; then
        ok "$script --help"
    else
        bad "$script --help (exit $RC): $(head -n 3 <<<"$OUT")"
    fi
done

echo "== sensor drivers (read-only)"
for script in app/sensors/distance/distance.py \
    app/sensors/humidity/humidity.py \
    app/sensors/temperature/temperature.py \
    app/sensors/pcb_temp/pcb_temp.py \
    app/sensors/pump/pump_power.py; do
    run_driver "$script"
    if import_error; then
        bad "$script: $(grep -m1 -E 'ModuleNotFoundError|ImportError|No module named' <<<"$OUT")"
    elif [ "$RC" -eq 124 ]; then
        bad "$script timed out"
    else
        ok "$script imports and runs (exit $RC): $(tail -n 1 <<<"$OUT")"
    fi
done

echo
echo "check_cli_imports: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
