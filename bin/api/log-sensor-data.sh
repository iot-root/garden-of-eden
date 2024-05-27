#!/bin/bash
pwd=$(dirname $(readlink -f $0))
wkdir=$(realpath $pwd/../..)

py="$wkdir/venv/bin/python"

# Define the log file locations for each sensor
LOG_FILE_HUMIDITY="/var/log/humidity.log"
LOG_FILE_TEMPERATURE="/var/log/temperature.log"
LOG_FILE_DISTANCE="/var/log/distance.log"
LOG_FILE_BRIGHTNESS="/var/log/brightness.log"
LOG_FILE_PUMP_SPEED="/var/log/pump_speed.log"
LOG_FILE_PUMP_STATS="/var/log/pump_stats.log"
LOG_FILE_PCB_TEMP="/var/log/pcb_temp.log"


# Ensure log files exist and are writable
sudo touch $LOG_FILE_HUMIDITY $LOG_FILE_TEMPERATURE $LOG_FILE_DISTANCE $LOG_FILE_BRIGHTNESS $LOG_FILE_PUMP_SPEED $LOG_FILE_PCB_TEMP $LOG_FILE_PUMP_STATS
sudo chmod 666 $LOG_FILE_HUMIDITY $LOG_FILE_TEMPERATURE $LOG_FILE_DISTANCE $LOG_FILE_BRIGHTNESS $LOG_FILE_PUMP_SPEED $LOG_FILE_PCB_TEMP $LOG_FILE_PUMP_STATS

# Execute Python scripts and capture their output
humidity=$($py $wkdir/api/app/sensors/humidity/humidity.py --log)
temperature=$($py $wkdir/api/app/sensors/temperature/temperature.py --log)
distance=$($py $wkdir/api/app/sensors/distance/distance.py --log)
brightness=$($py $wkdir/api/app/sensors/light/light.py --log)
pump_speed=$($py $wkdir/api/app/sensors/pump/pump.py --log)
pump_stats=$($py $wkdir/api/app/sensors/pump/pump_power.py --log)
pcb=$($py $wkdir/api/app/sensors/pcb_temp/pcb_temp.py --log)


# Append the results to their respective log files
echo "$humidity" >> $LOG_FILE_HUMIDITY
echo "$temperature" >> $LOG_FILE_TEMPERATURE
echo "$distance" >> $LOG_FILE_DISTANCE
echo "$brightness" >> $LOG_FILE_BRIGHTNESS
echo "$pump_speed" >> $LOG_FILE_PUMP_SPEED
echo "$pump_stats" >> $LOG_FILE_PUMP_STATS
echo "$pcb" >> $LOG_FILE_PCB_TEMP
