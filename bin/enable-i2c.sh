echo "I2C devices located at..."
ls /dev/i2c*    

# Check if I2C is enabled and enable it if necessary
i2c_status=$(sudo raspi-config nonint get_i2c)

# If I2C is not enabled (value is 1), then enable it
if [ "$i2c_status" -eq 1 ]; then
    echo "I2C is not enabled. Enabling now..."
    sudo raspi-config nonint do_i2c 1
    echo "I2C enabled."
else
    echo "I2C is already enabled."
fi

# Verify i2c hardware detection
# sudo i2cdetect -y 1 > /dev/null 2>&1 # Supress output
sudo i2cdetect -y 2 # for pi-zero 2 w?
if [ $? -eq 0 ]; then
    echo "PASS: i2cdetect executed successfully."
else
    echo "FAIL: i2cdetect encountered an error."
fi