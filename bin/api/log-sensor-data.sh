#!/bin/bash
pwd=$(dirname $(readlink -f $0))
wkdir=$(realpath $pwd/..)

py="$wkdir/venv/bin/python"

# Define the log file locations for each sensor
LOG_FILE_HUMIDITY="/var/log/humidity.log"
LOG_FILE_TEMPERATURE="/var/log/temperature.log"
LOG_FILE_DISTANCE="/var/log/distance.log"
LOG_FILE_BRIGHTNESS="/var/log/brightness.log"
LOG_FILE_SPEED="/var/log/speed.log"

# Ensure log files exist and are writable
sudo touch $LOG_FILE_HUMIDITY $LOG_FILE_TEMPERATURE $LOG_FILE_DISTANCE $LOG_FILE_BRIGHTNESS $LOG_FILE_SPEED
sudo chmod 666 $LOG_FILE_HUMIDITY $LOG_FILE_TEMPERATURE $LOG_FILE_DISTANCE $LOG_FILE_BRIGHTNESS $LOG_FILE_SPEED

# Get the current timestamp
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# Execute Python scripts and capture their output
humidity=$($py $wkdir/api/sensors/humidity/humidity.py)
temperature=$($py $wkdir/api/sensors/temperature/temperature.py)
distance=$($py $wkdir/api/sensors/distance/distance.py)
brightness=$($py $wkdir/api/sensors/light/light.py)
speed=$($py $wkdir/api/sensors/pump/pump.py)

# Append the results to their respective log files
echo "$timestamp, Humidity: $humidity" >> $LOG_FILE_HUMIDITY
echo "$timestamp, Temperature: $temperature" >> $LOG_FILE_TEMPERATURE
echo "$timestamp, Distance: $distance" >> $LOG_FILE_DISTANCE
echo "$timestamp, Brightness: $brightness" >> $LOG_FILE_BRIGHTNESS
echo "$timestamp, Speed: $speed" >> $LOG_FILE_SPEED
