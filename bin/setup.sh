#!/bin/bash
#VERBOSE=false

pwd=$(dirname $(readlink -f $0))
wkdir=$(realpath $pwd/..)

GRN="\e[32m"
RED="\e[31m"
RST="\e[0m"

function error { echo -ne "[${RED}ERROR${RST}]: $*\n" >&2; }
function info  { echo -ne "[${GRN}INFO${RST}]: $*\n" >&2; }
function red   { echo -ne "[${RED}INFO${RST}]: $*\n" >&2; }

if [ "$VERBOSE" == "true" ]; then
  log() { echo "$@"; }
  #log() {echo -ne "[${RED}INFO${RST}]: $*\n" >&2;}
else
  log() { :; }
fi

sudo apt update

# Using gpiozero to leverage pigpio daemon which is hardware driven and more efficient.
# This ensures better accuracy of the distance sensor and is less cpu intesive when using PWMs.
sudo apt install -y python3-gpiozero python3-pigpio python3-flask

# for i2c troubleshooting...
sudo apt-get install i2c-tools

# for ina219 pump current monitor
pip3 install pi-ina219

# pcb_temp monitor with overtemp trigger
sudo pip3 install adafruit-circuitpython-pct2075

# Note: Gardyn 3.0 temp-humidity sensor is clearly marked
# as AM2320 and per the datasheet specifies i2c_addr of "0x5c".
# However, something is afoot as the sensor actually behaves per
# the AHT20 spec: using i2cdetect the sensor shows up as 0x38, 
# implying it is a AHT20 sensor. Meaning, the temp and humidity does 
# not work on gardyn devices at all .... but it will now :-)
# My thinking is that the temp and humidity values are just hardcoded 
# in the system as I could not find any updating of the sensor readings.
sudo pip3 install adafruit-circuitpython-ahtx0

# Check if I2C is enabled
i2c_status=$(sudo raspi-config nonint get_i2c)

# If I2C is not enabled (value is 1), then enable it
if [ "$i2c_status" -eq 1 ]; then
    info "I2C is not enabled. Enabling now..."
    sudo raspi-config nonint do_i2c 1
    info "I2C enabled."
else
    info "I2C is already enabled."
fi

# Confirm i2c results
sudo i2cdetect -y 1 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    info "PASS: i2cdetect executed successfully."
else
    error "FAIL: i2cdetect encountered an error."
fi
