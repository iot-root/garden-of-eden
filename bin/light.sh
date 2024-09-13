#!/usr/bin/env bash

# light <brightness|on|off>
# on = brightness 70

brightness_min=1
brightness_max=15

brightness=70

NC=$(echo -e '\033[0m') ;
IT=$(echo -e '\033[3m') ;

light_off() {
	"${HOME}/garden-of-eden/venv/bin/python" "${HOME}/garden-of-eden/app/sensors/light/light.py" --off ;
}

light_on() {
	"${HOME}/garden-of-eden/venv/bin/python" "${HOME}/garden-of-eden/app/sensors/light/light.py" --on --brightness "${1}" ;
}

usage() {
	cat << EOF
  light <off|on|${IT}brightness${NC}>
  brightness value must be 1–100; "on" defaults to 70.

  e.g.:
    light 65
EOF
}

if [[ ${1} == ?(-)+([[:digit:]]) ]] ; then
	brightness=${1} ;
elif [[ "${1}" == "on" ]] ; then
	brightness=70 ;
elif [[ "${1}" == "off" ]] ; then
	light_off ;
	exit 0 ;
else
	usage ;
	exit 1 ;
fi

if [[ (( ${brightness} -ge ${brightness_min} )) && (( ${brightness} -le ${brightness_max} )) ]] ; then
	light_on "${brightness}" ;
else
	usage ;
	exit 2 ;
fi

exit 0 ;
