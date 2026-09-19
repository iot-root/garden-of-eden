#!/bin/bash
# Run every on-Pi verification script in this directory (check_*.sh, check_*.py).
#
#   tests/on_pi/run_all.sh              # everything
#   tests/on_pi/run_all.sh --no-hw      # skip checks that drive the hardware
#
# Needs the repo venv (python3 -m venv venv && venv/bin/pip install -r
# requirements.txt). Checks that drive pins also need pigpiod running; they are
# the ones whose header says so, and --no-hw skips them.
set -u

HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
PY=${PYTHON:-$REPO/venv/bin/python}
NO_HW=${1:-}
failed=()
ran=0

# A check is hardware-driving if its header says "# hardware: yes".
drives_hardware() { grep -qE '^# hardware: yes' "$1"; }

for check in "$HERE"/check_*.sh "$HERE"/check_*.py; do
    [ -e "$check" ] || continue
    name=$(basename "$check")
    if [ "$NO_HW" = "--no-hw" ] && drives_hardware "$check"; then
        echo "##### $name (skipped: --no-hw)"
        continue
    fi
    if drives_hardware "$check" && ! pgrep -x pigpiod >/dev/null; then
        echo "##### $name"
        echo "pigpiod is not running; start it with: sudo systemctl start pigpiod"
        failed+=("$name (pigpiod not running)")
        continue
    fi
    echo
    echo "##### $name"
    ran=$((ran + 1))
    case "$name" in
        *.py) "$PY" "$check" || failed+=("$name") ;;
        *) "$check" || failed+=("$name") ;;
    esac
done

echo
if [ "$ran" -eq 0 ]; then
    echo "No checks found in $HERE"
    exit 1
elif [ ${#failed[@]} -eq 0 ]; then
    echo "ALL ON-PI CHECKS PASSED ($ran run)"
else
    echo "FAILED: ${failed[*]}"
    exit 1
fi
