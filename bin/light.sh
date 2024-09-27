#!/usr/bin/env bash

# Script to control Gardyn lights
# Usage: light <brightness|on|off>
# "on" sets brightness to 70%, valid brightness range is 4%-100%

# -e exit immediately 
# -u undefined variables trigger error
# -o exit with first piped failure
set -euo pipefail

# Constants
readonly BRIGHTNESS_DEFAULT=70
readonly BRIGHTNESS_MIN=0
readonly BRIGHTNESS_MAX=100
readonly LIGHT_BY_DEFAULT=true   # Whether to default to 70% brightness on invalid input

RST=$(echo -e '\e[0m')
ITL=$(echo -e '\e[3m')

# Get Garden of Eden path from script location
GOE_PATH=$(realpath "$(dirname "$(readlink -e "${0}")")/..")

# Turn off the light
turn_off_light() {
    "${GOE_PATH}/venv/bin/python" "${GOE_PATH}/app/sensors/light/light.py" --off
}

# Turn on the light with specified brightness
turn_on_light() {
    local brightness="$1"
    "${GOE_PATH}/venv/bin/python" "${GOE_PATH}/app/sensors/light/light.py" --on --brightness "${brightness}"
}

# Print usage information
usage() {
    cat << EOF
Usage: light <off|on|${ITL}brightness${RST}>
Brightness value must be ${BRIGHTNESS_MIN}-${BRIGHTNESS_MAX}; "on" defaults to ${BRIGHTNESS_DEFAULT}.
Example: light 65
EOF
}

# Validate brightness
validate_brightness() {
    local brightness="$1"
    if [[ "${brightness}" -ge "${BRIGHTNESS_MIN}" && "${brightness}" -le "${BRIGHTNESS_MAX}" ]]; then
        return 0
    else
        return 1
    fi
}

# Main logic
main() {
    if [[ $# -eq 0 ]]; then
        echo "ERROR: No arguments provided"
        usage
        exit 1
    fi

    local brightness

    case "$1" in
        off)
            turn_off_light
            exit 0
            ;;
        on)
            brightness="${BRIGHTNESS_DEFAULT}"
            ;;
        ''|*[!0-9]*)
            echo "ERROR: Unrecognized input format"
            usage
            exit 1
            ;;
        *)
            brightness="$1"
            ;;
    esac

    if validate_brightness "${brightness}"; then
        turn_on_light "${brightness}"
    elif [[ "${LIGHT_BY_DEFAULT}" == true ]]; then
        turn_on_light "${BRIGHTNESS_DEFAULT}"
    else
        echo "ERROR: Brightness must be between ${BRIGHTNESS_MIN}-${BRIGHTNESS_MAX}"
        usage
        exit 1
    fi
}

# Run main function
main "$@"
