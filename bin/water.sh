#!/usr/bin/env bash

# Script to control Gardyn water pump
# Usage: water <seconds|on|off>
# "on" defaults to 300 seconds (5 minutes). The valid range is 1 to
# MAX_PUMP_RUN_SECONDS from the repo .env (default 900, 15 minutes), the same
# cap the REST API, MQTT service and schedule compiler enforce.

# -e exit immediately
# -u undefined variables trigger error
# -o exit with first piped failure
set -euo pipefail

# Constants
readonly TIME_DEFAULT=300    # 5 minutes in seconds
readonly TIME_MIN=1          # 1 second
readonly SPEED=50
readonly WATER_BY_DEFAULT=true  # Whether to default to TIME_DEFAULT on invalid input

NC=$(echo -e '\033[0m')
IT=$(echo -e '\033[3m')

# Get Garden of Eden path from script location
GOE_PATH=$(realpath "$(dirname "$(readlink -e "${0}")")/..")
# Put the repo root on PYTHONPATH so the driver scripts can `import config`
# regardless of the caller's working directory (cron, systemd, etc.).
export PYTHONPATH="${GOE_PATH}${PYTHONPATH:+:${PYTHONPATH}}"

# Longest allowed run, shared with the API/MQTT/schedule via MAX_PUMP_RUN_SECONDS.
# Env var wins, then the repo .env, then the 15-minute default.
TIME_MAX="${MAX_PUMP_RUN_SECONDS:-}"
if [[ -z "${TIME_MAX}" && -f "${GOE_PATH}/.env" ]]; then
    TIME_MAX=$(grep -E '^MAX_PUMP_RUN_SECONDS=' "${GOE_PATH}/.env" | tail -n1 | cut -d= -f2 | tr -d '[:space:]"')
fi
readonly TIME_MAX="${TIME_MAX:-900}"

# Turn off water pump
turn_off_water() {
    "${GOE_PATH}/venv/bin/python" "${GOE_PATH}/app/sensors/pump/pump.py" --off
}

# Turn on water pump
turn_on_water() {
    "${GOE_PATH}/venv/bin/python" "${GOE_PATH}/app/sensors/pump/pump.py" --on --speed "${SPEED}"
}

# Function to water for a specified time, then turn off
water_for_time() {
    local time="$1"
	echo "Watering for ${time} seconds."
    turn_on_water
    sleep "${time}"
    # turn_off_water # turn off will be caught by the exit trap.
}

# Function to handle exit signals, ensuring the water pump is turned off
clean_up() {
    turn_off_water
}

# Function to print usage instructions
usage() {
    cat << EOF
Usage: water <off|on|${IT}seconds${NC}>
Valid time range is ${TIME_MIN} to ${TIME_MAX} seconds; "on" defaults to ${TIME_DEFAULT} seconds.
Example: water 75
EOF
}

# Trap signals to ensure water is turned off
trap clean_up EXIT

# Main logic
main() {
    if [[ $# -eq 0 ]]; then
        echo "ERROR: No arguments provided"
        usage
        exit 1
    fi

    local time

    case "$1" in
        off)
            turn_off_water
            exit 0
            ;;
        on)
            time="${TIME_DEFAULT}"
            ;;
        ''|*[!0-9]*)
            echo "ERROR: Unrecognized input format"
            usage
            exit 1
            ;;
        *)
            time="$1"
            ;;
    esac

    # Validate that the input time is within range
    if [[ "${time}" -ge "${TIME_MIN}" && "${time}" -le "${TIME_MAX}" ]]; then
        water_for_time "${time}"
    elif [[ "${WATER_BY_DEFAULT}" == true ]]; then
        water_for_time "${TIME_DEFAULT}"
    else
        echo "ERROR: Input must be between ${TIME_MIN} and ${TIME_MAX} seconds"
        usage
        exit 1
    fi
}

# Run main function
main "$@"
