#!/bin/bash

# Configuration
BIN_DIR=$(dirname $(readlink -f $0))
INSTALL_DIR=$(realpath $BIN_DIR/..)
LOG_FILE="/tmp/install_packages.log"
PYTHON_ENV_LOG_FILE="/tmp/setup_python_env.log"
VERBOSE=false

# Safety flags
DRY_RUN=false
ASSUME_YES=false
for _arg in "$@"; do
    case "$_arg" in
        --dry-run) DRY_RUN=true ;;
        -y|--yes) ASSUME_YES=true ;;
        -v|--verbose) VERBOSE=true ;;
        -h|--help)
            cat <<'USAGE'
Usage: bin/setup.sh [--dry-run] [--yes] [--verbose]

  --dry-run   Print every system change that would be made, then exit.
              Makes NO changes. Run this first if you're unsure.
  --yes       Skip the confirmation prompt.
  --verbose   Extra logging.

setup.sh backs up every system file it edits to <file>.garden.bak, and
bin/uninstall.sh reverses the install. See docs/access.md.
USAGE
            exit 0 ;;
    esac
done

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
        #echo "$@"
        echo -e "[${GRY}INFO${RST}]: ${LGY}$*${RST}" >&2
    fi
}

# Make a one-time backup of a system file before modifying it, so every change
# is reversible (bin/uninstall.sh restores these).
function _backup_file {
    local f="$1"
    if [ -f "$f" ] && [ ! -f "${f}.garden.bak" ]; then
        sudo cp -a "$f" "${f}.garden.bak" && log_info "Backed up $f -> ${f}.garden.bak"
    fi
}

# Locate the active boot config. Raspberry Pi OS Bookworm uses /boot/firmware.
function boot_config_path {
    if [ -f /boot/firmware/config.txt ]; then
        echo /boot/firmware/config.txt
    elif [ -f /boot/config.txt ]; then
        echo /boot/config.txt
    else
        echo ""
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
    sudo apt install -y i2c-tools fswebcam ffmpeg pigpio python3 python3-pip python3-venv mosquitto mosquitto-clients openssh-server avahi-daemon >> "$LOG_FILE" 2>&1 &
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

# Function to enable I2C in /boot/config.txt and configure I2C
# See https://github.com/fivdi/i2c-bus/blob/master/doc/raspberry-pi-i2c.md
function enable_i2c_config_txt() {
    local config_file param="dtparam=i2c_arm=on"
    config_file="$(boot_config_path)"

    if [ -n "$config_file" ]; then
        _backup_file "$config_file"
        log "Enabling I2C in $config_file..."
        if grep -q "^#*dtparam=i2c_arm" "$config_file"; then
            # Replace the existing (possibly commented) line.
            sudo sed -i "/^#*dtparam=i2c_arm/c\\$param" "$config_file"
        else
            # No line present: append it (the old replace-only logic silently
            # did nothing here, leaving I2C disabled in config.txt).
            echo "$param" | sudo tee -a "$config_file" > /dev/null
        fi
        log_pass "I2C enabled in $config_file."
    else
        log_error "No config.txt found in /boot or /boot/firmware; relying on raspi-config for I2C."
    fi

    # Enable I2C interface via raspi-config (edits the correct file itself).
    sudo raspi-config nonint do_i2c 0

    # Ensure the i2c-dev module loads on boot.
    log "Configuring I2C modules..."
    _backup_file /etc/modules
    sudo sed -i '/^#*i2c-dev/d' /etc/modules
    echo "i2c-dev" | sudo tee -a /etc/modules > /dev/null
}


# Function to load I2C module immediately
function  load_i2c_module() {
    if lsmod | grep -q i2c_dev; then
        log_pass "I2C module is already loaded."
    else
        log_info "Loading I2C module..."
        sudo modprobe i2c-dev
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

# Function to restart the system if necessary
function  restart_system() {
    echo "The system needs to be restarted to apply the changes. Do you want to restart now? (y/n)"
    read -r answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        sudo reboot
    else
        echo "Please remember to reboot your system later to apply the changes."
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
    log_info "Setting temp&humidity SENSOR_TYPE in .env"
    if ! grep -q "SENSOR_TYPE=" $INSTALL_DIR/.env; then
        local sensor_type="AM2320"
        if i2cdetect -y 1 | grep -q "38"; then
            sensor_type="DHT20"
        fi
        log_info "Setting SENSOR_TYPE=$sensor_type in .env"
        echo "SENSOR_TYPE=$sensor_type" >> $INSTALL_DIR/.env
    fi
}

function check_device {
    local device_name=$1
    local addr_hex=$2
    local max_retries=${3:-1}
    local retry_interval=${4:-0.1}
    local addr_dec=$((16#$addr_hex))
    local row=$((addr_dec / 16))
    local col=$((addr_dec % 16))

    log_info "Checking for $device_name at address 0x$addr_hex..."

    for ((i=1; i<=max_retries; i++))
    do
        if sudo i2cdetect -y 1 | awk -v row="$row" -v col="$col" 'NR == row + 2 && $((col + 2)) != "--" {print $((col + 2))}' | grep -q "$addr_hex"; then
            log_pass "$device_name detected at address 0x$addr_hex."
            return 0
        fi
        sleep $retry_interval
        log_info "Attempt $i: $device_name not detected, retrying..."
    done

    log_error "$device_name not detected after $max_retries attempts."
}

# Check for I2C sensors
function check_i2c_sensors {
    log_info "Checking for I2C sensors"
    check_device "PCT2075" "48"
    check_device "INA219" "40"
    log "Note: the DHT20 temperature & humidity sensor should only appear for Gardyn 3.0 and newer"
    check_device "DHT20" "38"
    # note different method to detect AM2320
    log "Note: the AM2320 temperature & humidity sensor should only appear for Gardyn 1.0 and 2.0"
    check_device "AM2320" "5c" "10" "0.002"
}

function create_bash_script_symlinks() {
    sudo ln -fs "${INSTALL_DIR}/bin/light.sh" "/usr/local/bin/light"
    sudo ln -fs "${INSTALL_DIR}/bin/water.sh" "/usr/local/bin/water"
    sudo ln -fs "${INSTALL_DIR}/bin/update.sh" "/usr/local/bin/garden-update"
}

# Warn early if we're not on a supported Raspberry Pi OS. pigpio and the GPIO
# wheels assume a Pi; on other platforms they may need to be built manually.
function check_os_compatibility {
    log_info "Checking OS compatibility"

    if [ -f /proc/device-tree/model ] && grep -qi "raspberry pi" /proc/device-tree/model; then
        log_pass "Detected $(tr -d '\0' < /proc/device-tree/model)"
    else
        log_error "Not running on a Raspberry Pi. pigpio/GPIO libraries may need to be built manually and hardware features will not work."
    fi

    if [ -f /etc/os-release ]; then
        # shellcheck disable=SC1091
        . /etc/os-release
        log_info "OS: ${PRETTY_NAME:-unknown}"
        case "${ID:-}" in
            raspbian|debian) log_pass "Supported base OS (${ID})." ;;
            *) log_error "Untested OS '${ID:-unknown}'. Raspberry Pi OS (Debian) is recommended." ;;
        esac
    fi

    local pyver
    pyver=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "0.0")
    log_info "Python ${pyver} detected (3.9+ recommended)."
}

# Enable SSH so the unit is reachable headlessly after flashing.
function enable_ssh {
    log_info "Enabling SSH"
    if command -v raspi-config >/dev/null 2>&1; then
        sudo raspi-config nonint do_ssh 0 || true
    fi
    sudo systemctl enable --now ssh 2>/dev/null \
        || sudo systemctl enable --now sshd 2>/dev/null \
        || log_error "Could not enable the SSH service automatically."
    log_pass "SSH enabled."
}

# Set a stable hostname + mDNS so the unit is reachable at <hostname>.local
# (e.g. gardyn.local) without knowing its IP. Honors GARDEN_HOSTNAME (default gardyn).
function setup_mdns_hostname {
    local desired="${GARDEN_HOSTNAME:-gardyn}"
    local current
    current=$(hostname)
    if [ "$current" != "$desired" ]; then
        log_info "Setting hostname to '$desired' (was '$current')"
        sudo hostnamectl set-hostname "$desired" 2>/dev/null || true
        # Keep /etc/hosts in sync so sudo doesn't complain.
        if ! grep -q "127.0.1.1.*$desired" /etc/hosts; then
            _backup_file /etc/hosts
            echo "127.0.1.1 $desired" | sudo tee -a /etc/hosts > /dev/null
        fi
    fi
    sudo systemctl enable --now avahi-daemon 2>/dev/null || true
    log_pass "Reachable at ${desired}.local (mDNS) once avahi is running."
}

# Install udev rules so the cameras get stable /dev/gardyn-upper|lower names.
function install_udev_rules {
    local rules_src="${INSTALL_DIR}/services/etc/udev/rules.d/99-gardyn-cameras.rules"
    if [ -f "$rules_src" ]; then
        sudo cp "$rules_src" /etc/udev/rules.d/
        sudo udevadm control --reload-rules
        sudo udevadm trigger
        log_pass "Installed camera udev rules. Edit KERNELS in $rules_src to match your ports."
    fi
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
After=network-online.target pigpiod.service
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
User=$USER
WorkingDirectory=$INSTALL_DIR
# Wait (up to 60s) for pigpiod to accept connections before starting, so the
# service doesn't crash-restart during the boot race.
ExecStartPre=/bin/bash -c 'for i in \$(seq 1 60); do (echo > /dev/tcp/127.0.0.1/8888) >/dev/null 2>&1 && exit 0; sleep 1; done; exit 0'
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/mqtt.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo cp $service_file /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable mqtt.service
    sudo systemctl start mqtt.service
    log_info "MQTT service has been started and enabled on boot."
}

# Setup and start the REST API + web UI service (served by waitress on :5000).
function setup_api_service {
    local service_file="$INSTALL_DIR/services/etc/systemd/system/garden-api.service"
    mkdir -p "$(dirname "$service_file")"

    cat > $service_file <<EOF
[Unit]
Description=Garden of Eden REST API + Web UI
After=network.target pigpiod.service
Wants=pigpiod.service

[Service]
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/waitress-serve --listen=0.0.0.0:5000 run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo cp $service_file /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable garden-api.service
    sudo systemctl start garden-api.service
    log_info "Web UI/API service started on http://$(hostname).local:5000"
}

# Boot heartbeat: pulse the lights on startup so power-on is visibly confirmed.
function setup_boot_indicator {
    local service_file="$INSTALL_DIR/services/etc/systemd/system/garden-boot-indicator.service"
    mkdir -p "$(dirname "$service_file")"

    cat > $service_file <<EOF
[Unit]
Description=Garden of Eden boot heartbeat (pulse lights on startup)
After=network.target pigpiod.service mqtt.service
Wants=pigpiod.service

[Service]
Type=oneshot
User=$USER
ExecStart=$INSTALL_DIR/bin/boot-indicator.sh

[Install]
WantedBy=multi-user.target
EOF

    chmod +x "$INSTALL_DIR/bin/boot-indicator.sh"
    sudo cp $service_file /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable garden-boot-indicator.service
    log_info "Boot heartbeat enabled — lights pulse on power-on."
}

# Nightly auto-update: a timer that fast-forwards the branch and restarts the
# services only when something changed (bin/autoupdate.sh does the safe pull).
function setup_autoupdate {
    local svc="$INSTALL_DIR/services/etc/systemd/system/garden-autoupdate.service"
    local tmr="$INSTALL_DIR/services/etc/systemd/system/garden-autoupdate.timer"
    mkdir -p "$(dirname "$svc")"

    chmod +x "$INSTALL_DIR/bin/autoupdate.sh"

    # Let the (unattended) updater restart just these two services without a
    # password. Nothing else is granted.
    local sudoers=/etc/sudoers.d/garden-autoupdate
    local tmp_sudoers
    tmp_sudoers=$(mktemp)
    cat > "$tmp_sudoers" <<EOF
$USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart mqtt.service, /usr/bin/systemctl restart garden-api.service
EOF
    if sudo visudo -cf "$tmp_sudoers" >/dev/null 2>&1; then
        sudo cp "$tmp_sudoers" "$sudoers"
        sudo chmod 440 "$sudoers"
    else
        log_error "Generated sudoers file failed validation; skipping (auto-update restarts may prompt)."
    fi
    rm -f "$tmp_sudoers"

    cat > $svc <<EOF
[Unit]
Description=Garden of Eden nightly auto-update
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/bin/autoupdate.sh
EOF

    cat > $tmr <<EOF
[Unit]
Description=Run Garden of Eden auto-update nightly

[Timer]
# 03:30 local time, with jitter so many units don't hit GitHub at once.
OnCalendar=*-*-* 03:30:00
RandomizedDelaySec=1800
Persistent=true

[Install]
WantedBy=timers.target
EOF

    sudo cp "$svc" "$tmr" /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now garden-autoupdate.timer
    log_info "Nightly auto-update enabled (garden-autoupdate.timer, ~03:30)."
}

# Verify the REST API responds, if it is running (issue #51 checklist item).
function verify_api {
    if command -v curl >/dev/null 2>&1 && curl -s -o /dev/null -w '' "http://localhost:5000/temperature" 2>/dev/null; then
        log_info "Running API smoke test (bin/api-test.sh)"
        bash "${INSTALL_DIR}/bin/api-test.sh" >/dev/null 2>&1 \
            && log_pass "API smoke test passed." \
            || log_error "API smoke test reported errors. Start it with 'python run.py' and re-run bin/api-test.sh."
    else
        log_info "REST API not running; skipping smoke test. Start it with 'python run.py' then run bin/api-test.sh."
    fi
}

# Summarize the system-level changes before touching anything.
function print_plan {
    local cfg
    cfg="$(boot_config_path)"
    [ -z "$cfg" ] && cfg="(no config.txt found)"
    cat >&2 <<PLAN

=== Garden of Eden setup — planned system changes (sudo) ===
  1. apt install: i2c-tools fswebcam ffmpeg pigpio python3(-pip,-venv)
     mosquitto(-clients) openssh-server avahi-daemon
  2. Create Python venv in $INSTALL_DIR/venv and pip install requirements
  3. Enable I2C: edit $cfg, /etc/modules, and raspi-config   [backups: *.garden.bak]
  4. Add user '$(whoami)' to groups: i2c, gpio, dialout
  5. Symlink /usr/local/bin/{light,water,garden-update}
  6. Install camera udev rules -> /etc/udev/rules.d/
  7. Enable SSH; set hostname '${GARDEN_HOSTNAME:-gardyn}' + avahi   [backup: /etc/hosts.garden.bak]
  8. Install + enable systemd services: mqtt.service, garden-api.service,
     garden-boot-indicator.service (pulses lights on power-on)
  9. Enable nightly auto-update timer (garden-autoupdate.timer, ~03:30) +
     a scoped sudoers rule to restart the two services unattended
Reversible with: bin/uninstall.sh
============================================================

PLAN
}

# Main script execution
cd $INSTALL_DIR

print_plan

if [ "$DRY_RUN" = "true" ]; then
    log_info "Dry run complete — NO changes were made. Re-run without --dry-run to apply."
    exit 0
fi

if [ "$ASSUME_YES" != "true" ]; then
    read -r -p "Proceed with these changes? [y/N] " _ans
    case "$_ans" in
        y|Y|yes|YES) ;;
        *) log_info "Aborted by user — no changes made."; exit 0 ;;
    esac
fi

check_os_compatibility

install_packages
setup_python_env

enable_i2c_config_txt
load_i2c_module
check_i2c_detection
ensure_env_file
add_user_to_groups
check_i2c_sensors
add_sensor_type_to_env

create_bash_script_symlinks
install_udev_rules
enable_ssh
setup_mdns_hostname

#Note: pigpiod will be started by mqtt.service
#enable_pigpiod_service

setup_mqtt_service
setup_api_service
setup_boot_indicator
setup_autoupdate
verify_api
