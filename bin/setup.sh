# install apps
./setup/install-docker.sh
./setup/install-api.sh
./setup/install-web.sh

# enable hardware
./setup/enable-hardware.sh

# change hostname
./setup/change-hostname.sh

# enable services
./services/enable-api-service.sh
./services/enable-web-service.sh
# ../service/enable-docker-compose-service.sh
# ../service/enable-mqtt-service.sh
