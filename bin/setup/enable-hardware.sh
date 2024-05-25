# Check if I2C is enabled and enable it if necessary
i2c_status=$(sudo raspi-config nonint get_i2c)

# If I2C is not enabled (value is 1), then enable it
if [ "$i2c_status" -eq 1 ]; then
    info "I2C is not enabled. Enabling now..."
    sudo raspi-config nonint do_i2c 1
    info "I2C enabled."
else
    info "I2C is already enabled."
fi

# Verify i2c hardware detection
sudo i2cdetect -y 1 > /dev/null 2>&1 # Supress output
if [ $? -eq 0 ]; then
    info "PASS: i2cdetect executed successfully."
else
    error "FAIL: i2cdetect encountered an error."
fi

# Create or update .env file from .env-dist if it doesn't exist
if [ ! -f ./api/.env ]; then
    # Copy .env-dist to .env if .env does not exist
    cp ./api/.env-dist ./api/.env
    info "./api/.env file created from ./api/.env-dist, please update the mqtt env variables, etc"
else
    info ".env file already exists."
fi

# Add current user to necessary groups for hardware access
CURRENT_USER=$(whoami)
GROUPS="i2c gpio dialout"
info "The script is being run by: $CURRENT_USER"
for group in $GROUPS; do
    if [ $(getent group $group) ]; then
        sudo usermod -a -G $group $CURRENT_USER
        info "User $CURRENT_USER added to group $group."
    else
        error "Group $group does not exist. Skipping..."
    fi
done

