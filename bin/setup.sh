#!/bin/bash
#VERBOSE=false

#todo
# - update mqtt.service with run user as and working directory

BIN_DIR=$(dirname $(readlink -f $0))
INSTALL_DIR=$(realpath $BIN_DIR/..)

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


# copy files relative to project root
cd $INSTALL_DIR

sudo apt update
sudo apt install -y i2c-tools fswebcam pigpio python3 python3-pip python3-venv

# do you need a mqtt broker?
#sudo apt-get install mosquitto mosquitto-clients

info "Creating a python virtual environment and install dependencies"
python3 -m venv $INSTALL_DIR/venv
source $INSTALL_DIR/venv/bin/activate
pip3 install -r $INSTALL_DIR/requirements.txt
deactivate

# Check if I2C is enabled, need to confirm on pi-zero and pi-zero-2 modeles
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

# Check if the .env file exists
if [ ! -f .env ]; then
    # Copy .env-dist to .env if .env does not exist
    cp .env-dist .env
    info ".env file created from .env-dist, please update the mqtt env variables, etc"
else
    info ".env file already exists."
fi

# Ensure user is part of the required groups
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

# ensure pigpio daemon runs after system reboots.
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# Create the systemd service file with dynamic paths
SERVICE_FILE="$INSTALL_DIR/services/etc/systemd/system/mqtt.service"
cat > $SERVICE_FILE <<EOF
[Unit]
Description=MQTT Service
Requires=pigpiod.service
After=network.target pigpiod.service

[Service]
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/mqtt.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
# Move to the systemd directory, reload daemon, enable start at boot and start the service
sudo cp $SERVICE_FILE /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mqtt.service
sudo systemctl start mqtt.service
info "MQTT service has been started and enabled on boot."