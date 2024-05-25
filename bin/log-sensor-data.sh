#!/bin/bash
pwd=$(dirname $(readlink -f $0))
wkdir=$(realpath $pwd/..)
py="$wkdir/venv/bin/python"

# Define the log file location
log_files=(
    "/var/log/humidity-data.log"
    "/var/log/temp-data.log"
    "/var/log/distance-data.log"
    "/var/log/brightness-data.log"
    "/var/log/speed-data.log" 
)

# Capture logs
readings=(
    $($py $wkdir/api/sensors/humidity/humidity.py --log)
    $($py $wkdir/api/sensors/temperature/temperature.py --log)
    $($py $wkdir/api/sensors/distance/distance.py --log)
    $($py $wkdir/api/sensors/light/light.py --log)
    $($py $wkdir/api/sensors/pump/pump.py --log)
)

# Ensure log files exist and set appropriate permissions
ensure_log_file() {
    local file=$1
    if [ ! -f "$file" ]; then
        sudo touch "$file"
        sudo chown $(whoami):$(id -gn) "$file"
        sudo chmod 664 "$file"
    fi
}

for log_file in "${log_files[@]}"; do
    ensure_log_file $log_file
done

# Get the current timestamp
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# Append the results to the log files, 
# MAKE SURE THE ORDER OF LOGS AND SCRIPTS MATCH
for i in "${!log_files[@]}"; do
    sudo echo "$timestamp, ${readings[$i]}" >> "${log_files[$i]}"
done