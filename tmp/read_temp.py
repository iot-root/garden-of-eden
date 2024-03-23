#!/bin/bash

# Function to read temperature in Celsius from PCT2075 temperature sensor at the specified address
function read_temperature_celsius() {
  local address=$1
  local raw_data=$(sudo i2cset -y 1 "$address" 0x00)
  sleep 0.001

  local raw_data=$(sudo i2cget -y 1 "$address" 0x00)
  echo "$raw_data"
  echo
  local msb=$((raw_data))
  local lsb=$(sudo i2cget -y 1 $address 0x01)
  local temperature=$((msb << 5 | (lsb & 0xF8) >> 3))
  if [ $((temperature & 0x800)) -ne 0 ]; then
    # Negative temperature (convert from 2's complement)
    temperature=$(((temperature ^ 0xFFF) + 1))
    temperature=$((-temperature))
  fi
  temperature=$(awk "BEGIN { printf \"%.2f\", $temperature * 0.125 }")
  echo "$temperature"
}

# Replace 0x48 with the actual I2C address of your PCT2075 temperature sensor
# temp_sensor_address=0x5c
temp_sensor_address=0x48

temperature_c=$(read_temperature_celsius $temp_sensor_address)

echo "Temperature in Celsius: $temperature_c"