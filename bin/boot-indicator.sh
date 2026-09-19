#!/usr/bin/env bash

# Boot heartbeat: pulse the grow lights on startup so powering the unit on gives
# a visible confirmation that the Pi booted and the control stack works -- it
# exercises pigpio + the light driver + the wiring end-to-end. Kept short by
# design so it never fights the watering/light schedule.

# -u undefined variables trigger error; -o pipefail. (No -e: a failed pulse
# should never block boot.)
set -uo pipefail

# Resolve the repo root from this script's location.
GOE_PATH=$(realpath "$(dirname "$(readlink -e "${0}")")/..")
LIGHT="${GOE_PATH}/bin/light.sh"

# pigpiod is pulled in by mqtt.service; wait until it's actually up (max ~30s)
# before driving GPIO.
for _ in $(seq 1 30); do
    pgrep -x pigpiod >/dev/null 2>&1 && break
    sleep 1
done

pulse() { "${LIGHT}" "${1:-60}" >/dev/null 2>&1 || true; }
dark()  { "${LIGHT}" off >/dev/null 2>&1 || true; }

# Two clear pulses, then leave the lights off. The schedule (cron) and MQTT
# state restore take over from here.
pulse 60; sleep 3
dark;     sleep 1
pulse 60; sleep 3
dark
