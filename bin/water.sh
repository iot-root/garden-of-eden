#!/usr/bin/env bash

# water <minutes|on|off>
# on = 5 minutes

minutes_min=1
minutes_max=15

minutes=5

NC=$(echo -e '\033[0m') ;
IT=$(echo -e '\033[3m') ;

water_off() {
	 "${HOME}/garden-of-eden/venv/bin/python" "${HOME}/garden-of-eden/app/sensors/pump/pump.py" --off ;
}

water_on() {
	"${HOME}/garden-of-eden/venv/bin/python" "${HOME}/garden-of-eden/app/sensors/pump/pump.py" --on --speed 100 ;
	sleep $((${1} * 60)) ;
	water_off ;
}

usage() {
	cat << EOF
  water <off|on|${IT}minutes${NC}>
  minutes value must be 1–15; "on" defaults to 5.

  e.g.:
    water 2
EOF
}

if [[ ${1} == ?(-)+([[:digit:]]) ]] ; then
	minutes="${1}" ;
elif [[ "${1}" == "on" ]] ; then
	minutes=5 ;
elif [[ "${1}" == "off" ]] ; then
	water_off ;
	exit 0 ;
else
	usage ;
	exit 1 ;
fi

if [[ (( ${minutes} -ge ${minutes_min} )) && (( ${minutes} -le ${minutes_max} )) ]] ; then
	water_on "${minutes}" ;
else
	usage ;
	exit 2 ;
fi

exit 0 ;
