# Determine script's and project's root directory
BIN_DIR=$(dirname $(readlink -f $0))
INSTALL_DIR=$(realpath $BIN_DIR/..)

# Configure systemd service
SERVICE_FILE="$INSTALL_DIR/services/etc/systemd/system/mqtt.service"
cat > $SERVICE_FILE <<EOF
[Unit]
Description=Garden Of Eden MQTT Service
Requires=pigpiod.service
After=network.target pigpiod.service

[Service]
User=$USER
WorkingDirectory=$INSTALL_DIR/api
ExecStart=$INSTALL_DIR/venv/bin/python mqtt.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Install, reload, and start the MQTT service
sudo cp $SERVICE_FILE /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mqtt.service
sudo systemctl start mqtt.service
info "MQTT service has been started and enabled on boot."