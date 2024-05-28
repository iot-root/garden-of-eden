#!/bin/bash

NEW_HOSTNAME="my-garden"

sudo raspi-config nonint do_hostname $NEW_HOSTNAME

# Update /etc/hosts file
sudo sed -i "s/$(hostname)/$NEW_HOSTNAME/g" /etc/hosts

echo "Hostname changed to $NEW_HOSTNAME. The system will now reboot."
sudo reboot
