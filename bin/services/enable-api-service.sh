# Determine script's and project's root directory
BIN_DIR=$(dirname $(readlink -f $0))
INSTALL_DIR=$(realpath $BIN_DIR/..)

# Configure systemd service
# TODO: need env?
SERVICE_FILE="$INSTALL_DIR/services/etc/systemd/system/api.service"
cat > $SERVICE_FILE <<EOF
[Unit]
Description=Garden Of Eden API Service
Requires=pigpiod.service
Wants=network-online.target
After=network-online.target pigpiod.service

[Service]
User=$USER
WorkingDirectory=$INSTALL_DIR/api
ExecStart=$INSTALL_DIR/venv/bin/python app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Install, reload, and start the API service
sudo cp $SERVICE_FILE /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable api.service
sudo systemctl start api.service
sudo systemctl status api.service
info "API service has been started and enabled on boot."