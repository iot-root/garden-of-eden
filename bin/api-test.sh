#!/bin/bash
# Note requires rest API service to be running `python run.py`
# examples:
# curl http://localhost:5000/distance/measure
# curl http://localhost:5000/temperature
# curl -X POST -H "Content-Type: application/json" -d '{"value":30}' http://localhost:5000/pump/speed
# curl http://localhost:5000/pump/stats

BASE_URL="http://localhost:5000"
CONTENT_TYPE_HEADER="Content-Type: application/json"
SLEEP_DURATION=1

post_data() {
    local endpoint="$1"
    local data="$2"
    
    curl -X POST -H "$CONTENT_TYPE_HEADER" -d "$data" "$BASE_URL$endpoint"
}

get_data() {
    local endpoint="$1"
    
    curl "$BASE_URL$endpoint"
}

control_light() {
    local value="$1"
    
    post_data "/light/brightness" "{\"value\": $value}"
    get_data "/light/brightness"
    sleep "$SLEEP_DURATION"
}

control_pump() {
    local value="$1"
    
    post_data "/pump/speed" "{\"value\": $value}"
    get_data "/pump/speed"
    sleep "$SLEEP_DURATION"
}

# Light Control
control_light 30
control_light 0

post_data "/light/on" ""
sleep "$SLEEP_DURATION"
post_data "/light/off" ""

# Pump Control
control_pump 30
control_pump 0

post_data "/pump/on" ""
sleep "$SLEEP_DURATION"
post_data "/pump/off" ""

# pump current usage
control_pump 30
get_data "/pump/stats"
control_pump 10
get_data "/pump/stats"
post_data "/pump/off" ""
sleep "$SLEEP_DURATION"
get_data "/pump/stats"

# Distance Measure
get_data "/distance"

# Ambient temp
get_data "/temperature"

# humidity
get_data "/humidity"

# temperature on the PCB in case of the event that
# the motor or lights are causing board to get too hot
# from current draw
get_data "/pcb-temp"
