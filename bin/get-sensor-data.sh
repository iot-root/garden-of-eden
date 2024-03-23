#!/bin/bash

# Define the log file location
LOG_FILE="/var/log/gardyn/data.log"
#echo "test" >> $LOG_FILE

# Get the current timestamp
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# Execute Python scripts and capture their output
humidity=$(/usr/bin/python3 /home/gardyn/projects/gardyn-of-eden/app/sensors/humidity/humidity.py)
temperature=$(/usr/bin/python3 /home/gardyn/projects/gardyn-of-eden/app/sensors/temperature/temperature.py)
distance=$(/usr/bin/python3 /home/gardyn/projects/gardyn-of-eden/app/sensors/distance/distance.py)

# Append the results to the log file
echo "$timestamp, $humidity" >> $LOG_FILE
echo "$timestamp, $temperature" >> $LOG_FILE
echo "$timestamp, $distance" >> $LOG_FILE
