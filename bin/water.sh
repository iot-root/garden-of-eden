#!/usr/bin/env bash

# water <minutes|on|off>
# on = 5 minutes

set -euo pipefail

# If invalid time is specified, should we set
# gardyn to pump water for time_default (5 min)?
water_by_default=true

# 5 minutes is Gardyn's default watering time
time_default=5m

# minimum 1 second, maximum 15 minutes
time_min=1s
time_max=15m

# 100 speed is used in README; change if necessary
speed=100

# We have not yet started water this session
water_state=0

# bytes for plain / italic
NC=$(echo -e '\033[0m') ;
IT=$(echo -e '\033[3m') ;

# get Garden of Eden path from env
if [[ ! -d ${GOE_PATH:-} ]] ; then
	wild_guess=$(realpath "$(find /home/ -type d -name garden-of-eden)") ;
	if [[ -z "${wild_guess}" ]] ; then
		wild_guess='/path/to/garden-of-eden' ;
	fi
	cat << EOF
ERROR: The garden-of-eden environment path is incorrect or not set
       Try addding something to your .profile like:

GOE_PATH="${wild_guess}" ;
export GOE_PATH ;
EOF
	exit 1 ;
fi

# e.g. 3m => 180; 1m45s => 105
time_to_seconds() {
	echo $(($(sed 's/m/*60\+/g; s/s//g; s/+[ ]*$//g' <<< "${1}"))) ;
}

usage() {
	cat << EOF
  water <off|on|${IT}xmys${NC}>
  Valid values ${time_min}–${time_max}; "on" defaults to ${time_default}.
  Example: water 1m15s
EOF
}

water_off() {
	"${GOE_PATH}/venv/bin/python" "${GOE_PATH}/app/sensors/pump/pump.py" --off ;
	water_state=0 ;
}

water_on() {
	water_state=1 ;
	"${GOE_PATH}/venv/bin/python" "${GOE_PATH}/app/sensors/pump/pump.py" --on --speed ${speed} ;
}

water_for_time() {
	water_on ;
	sleep "${1}" ;
	water_off ;
}

# Function to double-check water is off on most exit conditions
water_exit() {
  if [[ ${water_state} -gt 0 ]] ; then
		water_off ;
	fi
}

# Function to turn off water on most error / termination conditions
water_kill() {
	error_code=$? ;
	echo "Warning: Received termination signal! Stopping water..." ;
	water_off ;
	echo "Water stopped, exiting" ;
	exit "${error_code}" ;
}

# Catch common error / interrupt signals and turn off the water
## Note: SIGKILL / SIGSTOP cannot be trapped
trap water_kill SIGABRT SIGALRM SIGHUP SIGINT SIGQUIT SIGTERM
# Double-check water is off on any normal exit
trap water_exit EXIT

# Max-accepted valid input is "13m120s"
if [[ ${#1} -gt 7 ]] ; then
	echo 'ERROR: Input too long!' ;
  usage ;
	exit 1 ;
# No suffix specified; assume minutes <= 15, seconds otherwise
elif [[ ${1} == ?(-)+([[:digit:]]) ]] ; then
	if [[ (( ${1} -le 15 )) ]] ; then
		time="${1}m" ;
	else
		time="${1}s" ;
	fi
# time is in xmys format
elif [[ "${1}" =~ ^([0-9]{1,3}[ms]{1})([0-9]{1,3}s)?$ ]] ; then
	time="${1}" ;
elif [[ "${1}" == "on" ]] ; then
	time=${time_default} ;
elif [[ "${1}" == "off" ]] ; then
	water_off ;
	exit 0 ;
else
	echo 'ERROR: Unrecognized input format!' ;
	usage ;
	exit 1 ;
fi

seconds=$(time_to_seconds "${time}") ;
seconds_min=$(time_to_seconds "${time_min}") ;
seconds_max=$(time_to_seconds "${time_max}") ;

if [[ (( ${seconds} -ge ${seconds_min} )) && (( ${seconds} -le ${seconds_max} )) ]] ; then
	water_for_time "${seconds}" ;
elif [[ ${water_by_default} ]] ; then
	water_for_time "${time_default}" ;
else
	echo 'ERROR: Unrecognized input format!' ;
	usage ;
	exit 1 ;
fi

exit 0 ;
