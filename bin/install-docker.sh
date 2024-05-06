sudo apt update
sudo apt full-upgrade
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ${USER}
newgrp docker
sudo apt install python3-pip
sudo pip3 install docker-compose
sudo systemctl enable docker
