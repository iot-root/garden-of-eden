#!/bin/bash

# Configuration
BIN_DIR=$(dirname $(readlink -f $0))
INSTALL_DIR=$(realpath $BIN_DIR/..)
LOG_FILE="/tmp/install_packages.log"
PYTHON_ENV_LOG_FILE="/tmp/setup_python_env.log"
VERBOSE=false

# Colors
GRN="\e[32m"
RED="\e[31m"
GRY="\e[90m"
LGY="\e[37m"
RST="\e[0m"

# Logging functions
function log_error {
    echo -e "[${RED}ERROR${RST}]: $*" >&2
}

function log_pass {
    echo -e "[${GRN}PASS${RST}]: $*"
}

function log_info {
    echo -e "[${GRY}INFO${RST}]: ${LGY}$*${RST}" >&2
}

function log {
    if [ "$VERBOSE" == "true" ]; then
        echo "$@"
    fi
}

# Spinner function
function show_spinner {
    local pid=$!
    local delay=0.1
    local spinstr='|/-\'
    echo -n "Updating..."
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    echo -e "\b\b\b\b\b\b"
}

# System update and package installation
function install_packages {
    log_info "Updating apt package list"
    sudo apt update > "$LOG_FILE" 2>&1 &
    show_spinner
    wait $!
    log_info "Installing packages"
    sudo apt install -y i2c-tools fswebcam pigpio python3 python3-pip python3-venv mosquitto mosquitto-clients >> "$LOG_FILE" 2>&1 &
    show_spinner
    wait $!
    if [ $? -ne 0 ]; then
        log_error "Package installation failed. Check the log file for details."
        cat "$LOG_FILE"
    else
        log_pass "Packages installed successfully. see $LOG_FILE"
    fi
}

# Python environment setup
function setup_python_env {
    log_info "Creating a python virtual environment and installing dependencies"
    python3 -m venv $INSTALL_DIR/venv > "$PYTHON_ENV_LOG_FILE" 2>&1 &
    show_spinner
    wait $!
    
    source $INSTALL_DIR/venv/bin/activate
    pip3 install -r $INSTALL_DIR/requirements.txt >> "$PYTHON_ENV_LOG_FILE" 2>&1 &
    show_spinner
    wait $!
    
    if [ $? -ne 0 ]; then
        log_error "Python environment setup failed. Check the log file for details."
        cat "$PYTHON_ENV_LOG_FILE"
    else
        log_pass "Python environment set up successfully. See $PYTHON_ENV_LOG_FILE"
    fi
    
    deactivate
}

# Enable I2C if not enabled
function enable_i2c {
    local i2c_status=$(sudo raspi-config nonint get_i2c)
    if [ "$i2c_status" -eq 1 ]; then
        log_info "I2C is not enabled. Enabling now..."
        sudo raspi-config nonint do_i2c 1
        log_pass "I2C enabled."
    else
        log_info "I2C is already enabled."
    fi
}

# Check I2C detection
function check_i2c_detection {
    sudo i2cdetect -y 1 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_pass "i2cdetect executed successfully."
    else
        log_error "i2cdetect encountered an error."
    fi
}

# Ensure .env file exists
function ensure_env_file {
    if [ ! -f .env ]; then
        cp .env-dist .env
        log_info ".env file created from .env-dist. Please update the mqtt env variables, etc."
    else
        log_info ".env file already exists."
    fi
}

# Add user to required groups
function add_user_to_groups {
    local current_user=$(whoami)
    local groups=("i2c" "gpio" "dialout")
    log_info "The script is being run by: $current_user"
    
    for group in "${groups[@]}"; do
        if getent group $group > /dev/null; then
            sudo usermod -a -G $group $current_user
            log_pass "User $current_user added to group $group."
        else
            log_error "Group $group does not exist. Skipping..."
        fi
    done
}

# Add SENSOR_TYPE to .env file
# If a gardyn model 1.0 or 2.0, AM2320 will not appear on i2cdetect without wakeup sequeence.
# so we assume it is an AM2320 unless we find a DHT20
function add_sensor_type_to_env {
    if ! grep -q "SENSOR_TYPE=" $INSTALL_DIR/.env; then
        local sensor_type="AM2320"
        if i2cdetect -y 1 | grep -q "38"; then
            sensor_type="DHT20"
        fi
        echo "SENSOR_TYPE=$sensor_type" >> $INSTALL_DIR/.env
    fi
}

# Check for the presence of an I2C device
function check_device {
    local device_name=$1
    local addr_hex=$2
    local addr_dec=$((16#$addr_hex))
    local row=$((addr_dec / 16))
    local col=$((addr_dec % 16))
    
    if sudo i2cdetect -y 1 | awk -v row="$row" -v col="$col" 'NR == row + 2 && $((col + 2)) != "--" {print $((col + 2))}' | grep -q "$addr_hex"; then
        log_pass "$device_name detected at address 0x$addr_hex."
    else
        log_error "$device_name not detected at address 0x$addr_hex."
    fi
}

# Check for I2C sensors
function check_i2c_sensors {
    log_info "Checking for I2C sensors"
    check_device "PCT2075" "48"
    check_device "INA219" "40"
    log_info "Note: the DHT20 temperature & humidity sensor should only appear for Gardyn 3.0 and newer"
    check_device "DHT20" "38"
    log_info "Note: the AM2320 temperature & humidity sensor should only appear for Gardyn 1.0 and 2.0"
    check_device "AM2320" "5c"
}

# Ensure pigpio daemon runs after system reboots
function enable_pigpiod_service {
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod
    log_info "pigpiod has been started and enabled on boot."
}

# Setup and start MQTT service
function setup_mqtt_service {
    local service_file="$INSTALL_DIR/services/etc/systemd/system/mqtt.service"
    
    cat > $service_file <<EOF
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

    sudo cp $service_file /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable mqtt.service
    sudo systemctl start mqtt.service
    log_info "MQTT service has been started and enabled on boot."
}

# Main script execution
cd $INSTALL_DIR

install_packages
setup_python_env
enable_i2c
check_i2c_detection
ensure_env_file
add_user_to_groups
add_sensor_type_to_env
check_i2c_sensors

#Note: pigpiod will be started by mqtt.service
#enable_pigpiod_service

setup_mqtt_service
