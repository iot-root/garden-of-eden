#!/bin/bash

# Stop the dphys-swapfile service
echo "Stopping dphys-swapfile service..."
sudo systemctl stop dphys-swapfile

# Backup the current swap file configuration
echo "Backing up the current swap file configuration..."
sudo cp /etc/dphys-swapfile /etc/dphys-swapfile.bak

# Edit the swap file configuration
echo "Updating the swap size to 2GB..."
sudo sed -i 's/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile

# Recreate the swap file
echo "Starting dphys-swapfile service to apply changes..."
sudo systemctl start dphys-swapfile

# Verify the swap size
echo "Verifying the new swap size..."
free -h

echo "Swap size successfully updated to 2GB."
