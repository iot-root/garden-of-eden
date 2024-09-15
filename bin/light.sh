#!/usr/bin/env bash

# light <brightness|on|off>
# on = brightness 70

set -euo pipefail

# If invalid brightness is specified, should we set
# gardyn lights to brightness_default (70%)?
light_by_default=true

# 70 is Gardyn's "100%"
brightness_default=70

# minimum 4%, maximum 100%; lower than 4% just flashes
brightness_min=4
brightness_max=100

RST=$(echo -e '\e[0m') ;
ITL=$(echo -e '\e[3m') ;

# get Garden of Eden path from script location
GOE_PATH=$(realpath "$(dirname "$(readlink -e "${0}")")/..") ;


light_off() {
	"${GOE_PATH}/venv/bin/python" "${GOE_PATH}/app/sensors/light/light.py" --off ;
}

light_on() {
	"${GOE_PATH}/venv/bin/python" "${GOE_PATH}/app/sensors/light/light.py" --on --brightness "${1}" ;
}

usage() {
	cat << EOF
  light <off|on|${ITL}brightness${RST}>
  brightness value must be ${brightness_min}–${brightness_max}; "on" defaults to ${brightness_default}.
  Example: light 65
EOF
}

# Max-accepted valid input is "100"
if [[ ${#1} -gt 3 ]] ; then
	echo 'ERROR: Input too many characters' ;
  usage ;
	exit 1 ;
elif [[ ${1} == ?(-)+([[:digit:]]) ]] ; then
	brightness=${1} ;
elif [[ "${1}" == "on" ]] ; then
	brightness=${brightness_default} ;
elif [[ "${1}" == "off" ]] ; then
	light_off ;
	exit 0 ;
else
	echo 'ERROR: Unrecognized input format' ;
	usage ;
	exit 1 ;
fi

if [[ (( ${brightness} -ge ${brightness_min} )) && (( ${brightness} -le ${brightness_max} )) ]] ; then
	light_on "${brightness}" ;
elif [[ ${light_by_default} ]] ; then
	light_on "${brightness_default}" ;
else
	echo "ERROR: Input must be between ${brightness_min}–${brightness_max}" ;
	usage ;
	exit 1 ;
fi

exit 0 ;
