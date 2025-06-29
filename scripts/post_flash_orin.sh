#!/bin/bash
set -e

source "$(dirname "$0")/utils.sh"

log "Updating system..."
sudo apt update && sudo apt upgrade -y

log "Installing Python & Jetson Stats..."
sudo apt install -y python3-pip
sudo pip3 install -U jetson-stats

log "Installing Jetpack..."
sudo apt install -y nvidia-jetpack

log "Adding CUDA paths to .bashrc..."
echo 'export PATH=/usr/local/cuda-12.6/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc

log "Rebooting to apply changes..."
sudo reboot
