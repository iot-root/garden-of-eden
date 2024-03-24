#!/bin/bash
pwd=$(dirname $(readlink -f $0))
wkdir=$(realpath $pwd/..)

py="$wkdir/venv/bin/python"
# Define the log file location
LOG_FILE="/var/log/gardyn-data.log"

sudo touch $LOG_FILE
#echo "test" >> $LOG_FILE

# Get the current timestamp
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# Execute Python scripts and capture their output
humidity=$($py $wkdir/app/sensors/humidity/humidity.py)
temperature=$($py $wkdir/app/sensors/temperature/temperature.py)
distance=$($py $wkdir/app/sensors/distance/distance.py)

# Append the results to the log file
echo "$timestamp, $humidity" >> $LOG_FILE
echo "$timestamp, $temperature" >> $LOG_FILE
echo "$timestamp, $distance" >> $LOG_FILE
