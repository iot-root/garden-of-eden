# Determine script's and project's root directory
BIN_DIR=$(dirname $(readlink -f $0))
INSTALL_DIR=$(realpath $BIN_DIR/..)

# Configure systemd service
SERVICE_FILE="$INSTALL_DIR/services/etc/systemd/system/docker-compose.service"
cat > $SERVICE_FILE <<EOF
[Unit]
Description=Garden Of Eden Docker Service
Requires=pigpiod.service
Wants=network-online.target
After=network-online.target pigpiod.service

[Service]
Environment=NODE_PORT=3000
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOF

sudo cp $SERVICE_FILE /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable docker-compose-app.service
sudo systemctl start docker-compose-app.service
sudo systemctl status docker-compose-app.service
info "Docker Compose service has been started and enabled on boot."