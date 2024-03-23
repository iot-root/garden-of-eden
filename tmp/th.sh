#!/bin/bash

# DEVICE_ADDR=0x5c
# DEVICE_ADDR=0x48
DEVICE_ADDR=0x38
I2C_BUS=1

# Wake up the sensor
pigs i2co $I2C_BUS $DEVICE_ADDR 0
sleep 0.001

# Open the I2C device
handle=$(pigs i2co $I2C_BUS $DEVICE_ADDR 0)

# If unable to obtain a handle, exit
if [ -z "$handle" ]; then
    echo "Error: Couldn't obtain I2C handle."
    exit 1
fi

# Request the data
pigs i2cwd $handle 0x03 0x00 0x04

# Give the sensor some time to process the request
sleep 0.001

# Read the data
data=($(pigs i2crd $handle 8))

echo 
humidity_raw=${data[3]}${data[4]}
temperature_raw=${data[5]}${data[6]}

# Note: You may need to adjust the conversion of raw values to actual values
# based on the AM2320's data format.
if (( (temperature_raw & 0x8000) )); then
    temperature_raw=$(( -(temperature_raw & 0x7FFF) ))
fi
temperature_raw=$((  ($temperature_raw/10) ))
humidity_raw=$(( ($humidity_raw / 10) ))
# temperature=$(( ($temperature_raw / 10) ))

# Display the results
echo "Humidity: $humidity_raw%"
echo "Temperature: $temperature_raw"

# Close the I2C connection
pigs i2cc $handle




# I2C_SLAVE = 0x0703
# Wake up AM2320
# sudo i2cset -y $I2C_BUS $DEVICE_ADDR 0x00
# sleep 0.003  # Wait at least 0.8ms, at most 3ms


# sudo i2cset -y $I2C_BUS $DEVICE_ADDR 0x03 0x00 0x04 i
# sleep 0.0016  # Wait at least 1.5ms for result
# sudo i2cdump -y $I2C_BUS $DEVICE_ADDR b
# RB=$(sudo i2cdump -y $I2C_BUS $DEVICE_ADDR b)
# echo $RB

# Request data from AM2320
# sudo i2cset -y $I2C_BUS $DEVICE_ADDR 0x03 0x00 0x01 i
# sleep 0.0016  # Wait at least 1.5ms for result
# HUMI_MSB=$(sudo i2cget -y $I2C_BUS $DEVICE_ADDR)

# sudo i2cset -y $I2C_BUS $DEVICE_ADDR 0x03 0x01 0x01 i
# sleep 0.0016  # Wait at least 1.5ms for result
# HUMI_LSB=$(sudo i2cget -y $I2C_BUS $DEVICE_ADDR)

# sudo i2cset -y $I2C_BUS $DEVICE_ADDR 0x03 0x02 0x01 i
# sleep 0.0016  # Wait at least 1.5ms for result
# TEMP_MSB=$(sudo i2cget -y $I2C_BUS $DEVICE_ADDR)

# sudo i2cset -y $I2C_BUS $DEVICE_ADDR 0x03 0x03 0x01 i
# sleep 0.0016  # Wait at least 1.5ms for result
# TEMP_MSB=$(sudo i2cget -y $I2C_BUS $DEVICE_ADDR)

# Read the data
# Note: The following commands may not fetch the exact bytes you expect, this is just a demonstration
# RB=$(sudo i2cdump -y $I2C_BUS $DEVICE_ADDR b)
# echo $RB

# HUMI_MSB=$(sudo i2cget -y $I2C_BUS $DEVICE_ADDR)
# HUMI_LSB=$(sudo i2cget -y $I2C_BUS $DEVICE_ADDR)
# TEMP_MSB=$(sudo i2cget -y $I2C_BUS $DEVICE_ADDR)
# TEMP_MSB=$(sudo i2cget -y $I2C_BUS $DEVICE_ADDR)

# echo $HUMI_MSB
# echo $HUMI_LSB
# echo $TEMP_MSB
# echo $TEMP_LSB
# Combining bytes and conversion
# Note: This will likely need adjustments
# TEMP=$(( ($TEMP_MSB << 8) + $TEMP_LSB ))
# HUMI=$(( ($HUMI_MSB << 8) + $HUMI_LSB ))

# Display results
# echo "Temperature: $TEMP, Humidity: $HUMI"
