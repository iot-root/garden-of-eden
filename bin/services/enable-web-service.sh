# Determine script's and project's root directory
BIN_DIR=$(dirname $(readlink -f $0))
INSTALL_DIR=$(realpath $BIN_DIR/../..)

# Configure systemd service
# TODO: change ExecStart to dist
SERVICE_FILE="$INSTALL_DIR/services/etc/systemd/system/web.service"
cat > $SERVICE_FILE <<EOF
[Unit]
Description=Garden Of Eden Web Service
Requires=pigpiod.service
Wants=network-online.target
After=network-online.target pigpiod.service

[Service]
Environment=NODE_PORT=3000
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/bin/run-web.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Install, reload, and start the API service
sudo cp $SERVICE_FILE /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable web.service
sudo systemctl start web.service
sudo systemctl status web.service
echo "Web service has been started and enabled on boot."